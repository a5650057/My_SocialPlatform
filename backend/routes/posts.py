import re
from datetime import datetime, timedelta
from functools import wraps
from flask_cors import cross_origin
from flasgger import swag_from
import redis
import jwt
import pymysql
from pymysql.cursors import DictCursor
import pymysql.cursors
from flask import Blueprint, jsonify, request
from flask_cors import CORS
from jwt import ExpiredSignatureError
from dotenv import load_dotenv
import os
from dbutils.pooled_db import PooledDB
from utils.redis_manager import redis_manager
from utils.init import db_connection, token_required
import json
from flask import jsonify, request
from flask import url_for
from flask import current_app
from datetime import datetime
from uuid import uuid4
from werkzeug.utils import secure_filename
from models.PostService import PostService

redis_client = redis_manager.get_client()


posts = Blueprint("posts", __name__)
CORS(posts)




@posts.route('/posts', methods=['GET'])
@token_required
def get_posts(current_user_email):
    conn = db_connection()
    cursor = conn.cursor(DictCursor)

    feed_key = f'feed:{current_user_email}'
    post_ids = redis_client.lrange(feed_key, 0, -1)
    posts = []

    # 檢查並收集來自Redis的帖子數據
    for post_id in post_ids:
        post_data = redis_client.hgetall(f'post:{post_id.decode("utf-8")}')
        if post_data:
            post = {k.decode('utf-8'): v.decode('utf-8') for k, v in post_data.items()}
            post['images_urls'] = json.loads(post['images_urls']) if 'images_urls' in post and post['images_urls'] else []
            # 獲取該帖子的評論
            cursor.execute('''
                SELECT c.id, c.user_email, c.content, c.created_at, u.username
                FROM comments AS c
                JOIN users AS u ON c.user_email = u.email
                WHERE c.post_id = %s
                ORDER BY c.created_at ASC
            ''', (post_id,))
            comments = cursor.fetchall()
            post['comments'] = comments
            posts.append(post)

    # 獲取當前用戶及其關注的人的email列表
    cursor.execute(
        '''
        SELECT followed_id FROM follows WHERE follower_id = %s
        UNION ALL
        SELECT %s AS followed_id
        ''', (current_user_email, current_user_email)
    )
    following_emails = [row['followed_id'] for row in cursor.fetchall()]

    placeholders = ','.join(['%s'] * len(following_emails))
    query = f'''
        SELECT p.id, p.content, p.created_at, p.user_email, u.username
        FROM posts AS p
        JOIN users AS u ON p.user_email = u.email
        WHERE p.user_email IN ({placeholders})
        ORDER BY p.created_at DESC
    '''
    params = following_emails
    cursor.execute(query, params)
    additional_posts = cursor.fetchall()

    # 處理並更新缺失的帖子數據
    for post in additional_posts:
        post_id = post['id']
        cursor.execute('SELECT image_url FROM post_images WHERE post_id = %s', (post_id,))
        images = cursor.fetchall()
        post['images_urls'] = [image['image_url'] for image in images]
        # 獲取該帖子的評論
        cursor.execute('''
            SELECT c.id, c.user_email, c.content, c.created_at, u.username
            FROM comments AS c
            JOIN users AS u ON c.user_email = u.email
            WHERE c.post_id = %s
            ORDER BY c.created_at ASC
        ''', (post_id,))
        comments = cursor.fetchall()
        post['comments'] = comments

        post_info = {k: str(v) if not isinstance(v, datetime) else v.strftime('%Y-%m-%d %H:%M:%S') for k, v in post.items()}
        post_info['images_urls'] = post['images_urls'] 

        # 更新Redis中的數據
        redis_client.hset(f'post:{post_info["id"]}', mapping={**post_info, 'images_urls': json.dumps(post_info['images_urls'])})

        if post_info['id'] not in [p['id'] for p in posts]:
            posts.append(post_info)

    return jsonify(posts)




@posts.route('/posts', methods=['POST', 'OPTIONS'])
@token_required
def create_post(current_user_email):
    conn = db_connection()
    cursor = conn.cursor(DictCursor)

    if 'content' not in request.form:
        return jsonify({'message': 'No content provided'}), 400
    

    # 验证用户是否存在
    cursor.execute('SELECT email, username FROM users WHERE email = %s', (current_user_email,))
    user = cursor.fetchone()
    if not user:
        return jsonify({'message': 'User not found'}), 403

    


    content = request.form['content']
    # 插入新帖子到数据库
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    post = PostService(current_user_email,content, cursor)
    post_id, current_time = post.insert_post()
    images_urls = PostService.save_images(post_id, request.files, cursor)
    conn.commit()
    
    # 获取当前用户的所有追踪者
    cursor.execute('SELECT follower_id FROM follows WHERE followed_id = %s UNION SELECT %s AS follower_id', (current_user_email, current_user_email))
    followers = cursor.fetchall()

    # 缓存帖子信息到 Redis
    post_info = {
        'id': str(post_id),
        'content': content,
        'created_at': current_time,
        'user_email': current_user_email,
        'username': user['username'],
        'images_urls': json.dumps(images_urls)  # 将图片URL列表序列化为JSON字符串
    }
    if redis_client:
        redis_client.hset(f'post:{post_id}', mapping=post_info)
        for follower in followers:
            redis_client.lpush(f'feed:{follower["follower_id"]}', str(post_id))

    return jsonify({'message': 'Post created successfully', 'post_id': post_id, 'images_urls': images_urls}), 201










@posts.route('/posts/<int:post_id>', methods=['DELETE'])
@token_required
def delete_post(current_user_email, post_id):
    conn = db_connection()
    cursor = conn.cursor(DictCursor)

    # 检查帖子是否存在并且归当前用户所有
    cursor.execute("SELECT * FROM posts WHERE id = %s AND user_email = %s", (post_id, current_user_email))
    post = cursor.fetchone()

    if not post:
        return jsonify({'message': 'Post not found or you do not have permission to delete this post'}), 404

    cursor.execute("SELECT image_url FROM post_images WHERE post_id = %s", (post_id,))
    images = cursor.fetchall()

    for img in images:
        # 從image_url中提取檔案名
        filename = img['image_url'].split('/')[-1]
        file_path = os.path.join(current_app.root_path, 'static/images', filename)
        if os.path.exists(file_path):
            os.remove(file_path)
  

    # 从数据库中删除帖子
    cursor.execute("DELETE FROM post_images WHERE post_id = %s", (post_id,))
    conn.commit()
    cursor.execute("DELETE FROM posts WHERE id = %s", (post_id,))
    conn.commit()

    # 从 Redis 中删除帖子信息
    redis_client.delete(f'post:{post_id}')

    # 从当前用户及其关注者的 feed 中移除帖子ID
    # 首先找出所有关注当前用户的人
    cursor.execute("SELECT follower_id FROM follows WHERE followed_id = %s", (current_user_email,))
    followers = cursor.fetchall()

    # 对于每个关注者，从他们的 feed 中移除帖子ID
    for follower in followers:
        redis_client.lrem(f'feed:{follower["follower_id"]}', 1, post_id)

    # 同时也需要从当前用户自己的 feed 中移除帖子ID
    redis_client.lrem(f'feed:{current_user_email}', 1, post_id)

    return jsonify({'message': 'Post deleted successfully'}), 200

@posts.route('/comments/add', methods=['POST'])
@token_required
def add_comment(current_user_email):
    conn = db_connection()
    cursor = conn.cursor(DictCursor)
    
    post_id = request.json.get('post_id')
    content = request.json.get('content')
    
    if not post_id or not content:
        return jsonify({'message': 'Missing post ID or content'}), 400

    # 插入评论到数据库
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        cursor.execute(
            'INSERT INTO comments (post_id, user_email, content, created_at) VALUES (%s, %s, %s, %s)',
            (post_id, current_user_email, content, current_time)
        )
        conn.commit()
        return jsonify({'message': 'Comment added successfully'}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'message': str(e)}), 500
    


@posts.route('/user', methods=['GET'])
@token_required
def get_specific_user_posts(current_user_email):
    username = request.args.get('username', type=str)
    if not username:
        return jsonify({'message': 'Username is required'}), 400

    print(f"Fetching posts for username: {username}")  # 添加日誌打印
    conn = db_connection()
    cursor = conn.cursor(DictCursor)
    
    # Find user email by username
    cursor.execute('SELECT email FROM users WHERE username = %s', (username,))
    user = cursor.fetchone()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    user_email = user['email']

    # Fetch posts and their images for the specified user
    cursor.execute('''
        SELECT p.id, p.content, p.created_at, p.user_email, u.username, pi.image_url
        FROM posts AS p
        JOIN users AS u ON p.user_email = u.email
        LEFT JOIN post_images AS pi ON p.id = pi.post_id
        WHERE p.user_email = %s
        ORDER BY p.created_at DESC;
    ''', (user_email,))
    posts = cursor.fetchall()

    print(f"Fetched posts: {posts}")  # 添加日誌打印

    # Build the response data structure
    posts_by_id = {}
    for post in posts:
        if post['id'] in posts_by_id:
            posts_by_id[post['id']]['images_urls'].append(post['image_url'])
        else:
            post['images_urls'] = [post['image_url']] if post['image_url'] else []
            posts_by_id[post['id']] = post

    # Fetch comments for each post
    for post_id, post in posts_by_id.items():
        cursor.execute('''
            SELECT c.id, c.user_email, c.content, c.created_at, u.username
            FROM comments AS c
            JOIN users AS u ON c.user_email = u.email
            WHERE c.post_id = %s
            ORDER BY c.created_at ASC
        ''', (post_id,))
        comments = cursor.fetchall()
        post['comments'] = comments

    return jsonify(list(posts_by_id.values()))

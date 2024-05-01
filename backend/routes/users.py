

from datetime import datetime, timedelta
from functools import wraps
from flask_cors import cross_origin
from flasgger import swag_from
import jwt

from pymysql.cursors import DictCursor

from flask import Blueprint, jsonify, request
from flask_cors import CORS
from jwt import ExpiredSignatureError
from dotenv import load_dotenv
import os
from dbutils.pooled_db import PooledDB
from utils.redis_manager import redis_manager
from utils.init import db_connection, token_required
from flask import jsonify, request

import json
from werkzeug.utils import secure_filename
from flask import url_for
from flask import current_app
from datetime import datetime
from uuid import uuid4

redis_client = redis_manager.get_client()


users = Blueprint("users", __name__)
CORS(users)


@users.route("/verify_token", methods=["GET"])
@token_required
def verify_token(current_user_email):
    return jsonify({"message": "Token is valid.", "email": current_user_email}), 200


@users.route("/register", methods=["POST"])
@swag_from({
    'tags': ['Users'],
    'description': 'Register a new user',
    'consumes': ['application/json'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body', 
            'required': True,
            'description': 'User registration data',
            'schema': {
                'type': 'object',
                'properties': {
                    'email': {
                        'type': 'string',
                        'example': 'user@example.com',
                    },
                    'username': {
                        'type': 'string',
                        'example': 'username',
                    },
                    'password': {
                        'type': 'string',
                        'example': 'password123',
                    }
                },
                'required': ['email', 'username', 'password']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'User registered successfully'
        },
        400: {
            'description': 'Invalid request'
        },
        409: {
            'description': 'Email or username already exists'
        }
    }
})
def register():
    print(request.json, type(request.json))

    conn = db_connection()  # 連接資料庫
    cursor = conn.cursor(DictCursor)  # 創建一個游標

    email = request.json["email"]
    username = request.json["username"]
    password = request.json["password"]
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    if cursor.fetchone():
        return jsonify({"errormessage": "Email is already exist"}), 409

    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    if cursor.fetchone():
        return jsonify({"errormessage": "Username is already used"}), 409

    if len(email) < 8 or "@" not in email:
        return (
            jsonify(
                {
                    "errormessage": 'Email must be longer than 8 characters and contain "@"'
                }
            ),
            400,
        )

    
    sql = "INSERT INTO users (email, username, password, created_at) VALUES (%s, %s, %s, %s)"
    cursor.execute(sql, (email, username, password, created_at))
    conn.commit()

    return jsonify({"status": "success"}), 201


@users.route("/login", methods=["POST"])
@swag_from({
    'tags': ['Users'],
    'description': 'User login',
    'parameters': [
        {
            'name': 'email',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'email': {
                        'type': 'string'
                    },
                    'password': {
                        'type': 'string'
                    }
                },
                'required': ['email', 'password']
            },
            'description': 'User login credentials'
        }
    ],
    'responses': {
        200: {
            'description': 'Login successful, token returned',
            'schema': {
                'type': 'object',
                'properties': {
                    'token': {
                        'type': 'string',
                        'description': 'JWT token for authentication'
                    }
                }
            }
        },
        401: {
            'description': 'Login failed, invalid credentials'
        }
    }
})
def login():

    
    conn = db_connection()
    cursor = conn.cursor(DictCursor)

    email = request.json["email"]
    password = request.json["password"]

    sql = "SELECT * FROM users WHERE email = %s AND password = %s"

    cursor.execute(sql, (email, password))
    user = cursor.fetchone()

    if user:
        print("login success")
        token = jwt.encode(
            {"email": user["email"], "exp": datetime.utcnow() + timedelta(minutes=30)},
            "secret",
            algorithm="HS256",
        )
        return jsonify({"token": token})
    else:
        print("login failed")
        return jsonify({"status": "login failed"}), 401


@users.route("/recommended_users", methods=["GET"])
def get_recommended_users():
    conn = db_connection()
    cursor = conn.cursor(DictCursor)
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    else:
        return jsonify({"error": "Authorization header is missing or not valid."}), 401

    try:
        decoded = jwt.decode(token, "secret", algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401

    current_email = decoded["email"]
    cursor.execute(
        "SELECT email, username FROM users WHERE email != %s", (current_email,)
    )
    users = cursor.fetchall()
    return jsonify(users)


@users.route("/follow", methods=["POST"])
@token_required  # 使用装饰器自动处理Token验证和用户识别
def follow_user(current_user_email):
    conn = db_connection()
    cursor = conn.cursor(DictCursor)
    data = request.json
    followed_email = data["followed_email"]
    follower_email = current_user_email
    cursor.execute("SELECT * FROM users WHERE email = %s", (follower_email,))
    if not cursor.fetchone():
        return jsonify({"error": "Follower not found"}), 404

    cursor.execute("SELECT * FROM users WHERE email = %s", (followed_email,))
    if not cursor.fetchone():
        return jsonify({"error": "Followed user not found"}), 404

    cursor.execute(
        "SELECT * FROM follows WHERE follower_id = %s AND followed_id = %s",
        (follower_email, followed_email),
    )
    if cursor.fetchone():
        return jsonify({"error": "Already following"}), 409

    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO follows (follower_id, followed_id, created_at) VALUES (%s, %s, %s)",
        (follower_email, followed_email, current_time),
    )
    conn.commit()

    return jsonify({"status": "success"})

@users.route('/following', methods=['GET'])
@token_required
@swag_from({
    'tags': ['Users'],
    'description': 'Get a list of user emails that the current user is following',
    'responses': {
        200: {
            'description': 'A list of emails representing the users that the current user is following',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'string',
                    'description': 'User email'
                }
            }
        },
        401: {
            'description': 'Authorization information is missing or invalid'
        }
    }
})
def get_following(current_user_email):
    conn = db_connection()
    cursor = conn.cursor(DictCursor)
    cursor.execute("SELECT followed_id FROM follows WHERE follower_id = %s", (current_user_email,))
    following = cursor.fetchall()
    following_emails = [user['followed_id'] for user in following]
    return jsonify(following_emails)

def get_post_ids_by_user_email(user_email):
    # 根据用户邮箱获取所有帖子的ID列表
    conn = db_connection()
    cursor = conn.cursor(DictCursor)
    cursor.execute(
        "SELECT id FROM posts WHERE user_email = %s", (user_email,)
    )
    posts = cursor.fetchall()
    post_ids = [str(post['id']) for post in posts]  # 确保ID是字符串
    return post_ids





@users.route("/unfollow", methods=["POST"])
@token_required
def unfollow_user(current_user_email):
    conn = db_connection()
    cursor = conn.cursor(DictCursor)
    data = request.json
    followed_email = data["followed_email"]
    follower_email = current_user_email

    # 检查两个用户是否存在
    cursor.execute("SELECT * FROM users WHERE email = %s", (follower_email,))
    if not cursor.fetchone():
        return jsonify({"error": "Follower not found"}), 404

    cursor.execute("SELECT * FROM users WHERE email = %s", (followed_email,))
    if not cursor.fetchone():
        return jsonify({"error": "Followed user not found"}), 404

    # 检查是否已经关注了该用户
    cursor.execute(
        "SELECT * FROM follows WHERE follower_id = %s AND followed_id = %s",
        (follower_email, followed_email),
    )
    if not cursor.fetchone():
        return jsonify({"error": "Not following"}), 409

    # 执行取消关注操作
    cursor.execute(
        "DELETE FROM follows WHERE follower_id = %s AND followed_id = %s",
        (follower_email, followed_email),
    )
    conn.commit()

    # 从Redis中移除被取消关注用户的帖子ID
    unfollowed_user_post_ids = get_post_ids_by_user_email(followed_email)
    feed_key = f'feed:{current_user_email}'
    for post_id in unfollowed_user_post_ids:
        redis_client.lrem(feed_key, 0, post_id)

    return jsonify({"status": "unfollowed"})
def convert_post_to_redis_format(post): 
    post_for_redis = {k: (str(v) if isinstance(v, datetime) else v) for k, v in post.items()}
    return post_for_redis


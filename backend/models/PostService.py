from datetime import datetime
from flask import current_app, url_for
from werkzeug.utils import secure_filename
import os
from uuid import uuid4
from pymysql.cursors import DictCursor
import pymysql.cursors

class PostService:
    def __init__(self, user_email, content, cursor):
        self.user_email = user_email
        self.content = content
        self.cursor = cursor

    def insert_post(self):
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute('INSERT INTO posts (content, user_email, created_at) VALUES (%s, %s, %s)',
                            (self.content, self.user_email, current_time))
        self.post_id = self.cursor.lastrowid
        return self.post_id, current_time

    @staticmethod
    def save_images(post_id, files,cursor):
        images_urls = []
        for index in range(5):  # 假設最多上傳5張圖片
            image_key = f'image{index}'
            if image_key in files:
                image = files[image_key]
                original_filename = secure_filename(image.filename)
                extension = os.path.splitext(original_filename)[1]
                unique_filename = f"{uuid4()}{extension}"
                image_path = os.path.join(current_app.root_path, 'static/images', unique_filename)
                image.save(image_path)
                image_url = url_for('static', filename=f'images/{unique_filename}', _external=True)
                images_urls.append(image_url)
                cursor.execute('INSERT INTO post_images (post_id, image_url) VALUES (%s, %s)', (post_id, image_url))
        return images_urls

from datetime import datetime
from flask import jsonify
from utils.init import db_connection, redis_manager
from datetime import datetime, timedelta


class User:
    def __init__(self, email, username=None, password=None):
        self.email = email
        self.username = username
        self.password = password

    def register(self):
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (self.email,))
        if cursor.fetchone():
            return jsonify({"errormessage": "Email is already exist"}), 409

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = "INSERT INTO users (email, username, password, created_at) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (self.email, self.username, self.password, created_at))
        conn.commit()
        return jsonify({"status": "success"}), 201

    def login(self):
        conn = db_connection()
        cursor = conn.cursor()
        sql = "SELECT * FROM users WHERE email = %s AND password = %s"
        cursor.execute(sql, (self.email, self.password))
        user = cursor.fetchone()

        if user:
            from jwt import encode
            token = encode(
                {"email": user["email"], "exp": datetime.utcnow() + timedelta(minutes=30)},
                "secret",
                algorithm="HS256",
            )
            return jsonify({"token": token})
        else:
            return jsonify({"status": "login failed"}), 401

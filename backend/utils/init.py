import os
import re
from datetime import datetime, timedelta
from functools import wraps
import jwt
from jwt import ExpiredSignatureError
from flask import jsonify, request
from flask_cors import CORS, cross_origin
from flasgger import swag_from
import redis
import pymysql
from pymysql.cursors import DictCursor
from dbutils.pooled_db import PooledDB
from dotenv import load_dotenv

# 加载环境变量
dotenv_path = os.path.join('../../db.env')
load_dotenv(dotenv_path=dotenv_path)


# 初始化数据库连接池
pool = PooledDB(
    creator=pymysql,
    maxconnections=6,
    mincached=2,
    maxcached=5,
    blocking=True,
    maxusage=None,
    ping=0,
    host=os.getenv("DBHOST"),
    user=os.getenv("DBUSER"),
    password=os.getenv("DBPW"),
    database=os.getenv("DB_NAME"),
    charset='utf8'
)

def db_connection():
    return pool.connection()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            auth_header = request.headers['Authorization']
            token = auth_header.split(" ")[1] if len(auth_header.split(" ")) > 1 else None

        if not token:
            return jsonify({"message": "Token is missing!"}), 401

        try:
            data = jwt.decode(token, "secret", algorithms=["HS256"])
            current_user_email = data.get("email")
        except ExpiredSignatureError:
            return jsonify({"message": "Token has expired, please log in again."}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({"message": "Token is invalid!"}), 401

        return f(current_user_email, *args, **kwargs)

    return decorated

import logging

from waitress import serve

from app import app

logging.basicConfig(level=logging.INFO)  # 配置日誌級別，不然後端的終端並不會打印日誌

serve(app, host="0.0.0.0", port=5000) 


# serve(app, host='127.0.0.1', port=5000) 

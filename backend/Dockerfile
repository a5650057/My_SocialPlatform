# 使用官方Python运行时作为父镜像
FROM python:3.9.19-slim

#在容器中创建一个/app目录，并使其成为工作目录
WORKDIR /app 

# 将当前目录中的文件复制到位于/app中的容器中
COPY . /app  

# 安装requirements.txt中列出的任何需要的包
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# 使端口5000可供此容器外的环境使用
EXPOSE 5000


CMD ["python", "wsgi.py"]

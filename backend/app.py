from flasgger import Swagger
from flask import Flask
from flask_cors import CORS
from flask_restful import Api

from routes.posts import posts

from routes.users import users
from routes.huh import huh

app = Flask(__name__)
CORS(app)
api = Api(app)
Swagger(app)


app.register_blueprint(huh, url_prefix="/huh")
app.register_blueprint(users, url_prefix="/users")
app.register_blueprint(posts, url_prefix="/posts")


if __name__ == "__main__":

    app.run(debug=True)

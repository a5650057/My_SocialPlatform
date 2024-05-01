from flask import Blueprint

huh = Blueprint("your_blueprint_name", __name__)


@huh.route("/example")
def example():
    return {"message": "This is an example"}

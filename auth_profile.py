from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
import jwt
import os

SECRET_KEY = os.getenv("SECRET_KEY", 'secret')

# Blueprint for authorization endpoints
auth_blueprint = Blueprint("auth", __name__)

# Bcrypt and database instances (latter using SQLAlchemy as the ORM)
bcrypt = Bcrypt()
db = SQLAlchemy()


# User model used for registration, login, and authentication
class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    d_list = db.Column(db.String(500), nullable=False) # list of diseases, delimited by spaces

    def __init__(self, username, password, d_list):
        self.username = username
        self.password = password
        self.d_list = d_list


# Login endpoint, returns JWT if user is found and password hash matches
def login():
    data = request.json
    username = data["username"]
    password = data["password"]
    user = User.query.filter_by(username=username).first()
    if user:
        if bcrypt.check_password_hash(user.password, password):
            return jsonify(
                {
                    "success": True,
                    "token": jwt.encode({"username": user.username}, SECRET_KEY),
                    "user": user.username,
                    "d_list": user.d_list,
                }
            )
        else:
            return jsonify({"success": False, "message": "Incorrect password"})
    else:
        return jsonify({"success": False, "message": "User %s not found" % username})


# Registration endpoint, returns JWT if user doesn't already exist and registration is successful
def register():
    data = request.json
    username = data["username"]
    password = data["password"]
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({"success": False, "message": "User already exists"})
    else:
        user = User(username, bcrypt.generate_password_hash(password), "")
        db.session.add(user)
        try:
            db.session.commit()
            return jsonify(
            {
                "success": True,
                "token": jwt.encode({"username": user.username}, SECRET_KEY),
                "user": user.username,
                "d_list": user.d_list,
            }
        )
        except:
            db.rollback()
            return jsonify({"success": False, "message": "Error registering user"})
        


# Verifies JWT and returns user information if valid
def tokenauth():
    token = request.headers.get("Authorization").split(" ")[1]
    tokenObject = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    username = tokenObject["username"]
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify(
            {
                "success": True,
                "token": jwt.encode({"username": user.username}, SECRET_KEY),
                "user": user.username,
                "d_list": user.d_list,
            }
        )
    else:
        return jsonify({"success": False, "message": "User not found"})


# Bookmarking endpoints
# Handles add request
def additem():
    token = request.headers.get("Authorization").split(" ")[1]
    tokenObject = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    username = tokenObject["username"]
    user = User.query.filter_by(username=username).first()
    if user:
        data = request.json
        disease = data["label"]
        if len(user.d_list) + len(disease) > 498:
            return jsonify({"success": False, "message": "No more items can be bookmarked"})
        if disease in user.d_list:
            return jsonify({"success": False, "message": "Item already bookmarked"})
        user.d_list += " " + disease
        user.d_list = user.d_list.strip()
        try:
            db.session.commit()
            return jsonify({"success": True, "d_list": user.d_list})
        except:
            db.rollback()
            return jsonify({"success": False, "message": "Error bookmarking item"})


# Handles remove request
def removeitem():
    token = request.headers.get("Authorization").split(" ")[1]
    tokenObject = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    username = tokenObject["username"]
    user = User.query.filter_by(username=username).first()
    if user:
        data = request.json
        disease = data["label"]
        user.d_list = user.d_list.replace(disease, "").strip()
        user.d_list = user.d_list.strip()
        try:
            db.session.commit()
            return jsonify({"success": True, "d_list": user.d_list})
        except:
            db.rollback()
            return jsonify({"success": False, "message": "Error removing bookmarked item"})


# Map the functions to their respective endpoints as handlers
auth_blueprint.add_url_rule(rule="/user/login", view_func=login, methods=["POST"])
auth_blueprint.add_url_rule(rule="/user/register", view_func=register, methods=["POST"])
auth_blueprint.add_url_rule(rule="/user/tokenauth", view_func=tokenauth, methods=["POST"])
auth_blueprint.add_url_rule(rule="/user/profile/add", view_func=additem, methods=["PUT"])
auth_blueprint.add_url_rule(rule="/user/profile/remove", view_func=removeitem, methods=["PUT"])

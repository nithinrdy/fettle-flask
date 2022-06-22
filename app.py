from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json
import pandas as pd
import numpy as np
from ast import literal_eval
from sqlalchemy import JSON
from flask_bcrypt import Bcrypt
import jwt


app = Flask(__name__)
bcrypt = Bcrypt(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
model = SentenceTransformer("all-MiniLM-L12-v2")
df = pd.read_csv("diseases__encoded.csv").reset_index()

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
SAMPLE_SECRET_KEY = "secret"  # For local purposes

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    d_list = db.Column(db.String(500), nullable=False)

    def __init__(self, username, password, d_list):
        self.username = username
        self.password = password
        self.d_list = d_list


@app.route("/")
def home():
    return jsonify({"test": "Hello World!"})


@app.route("/data", methods=["GET"])
def data():
    to_client = df.drop(["symptomVectors", "symptoms", "index", "level_0"], axis=1)
    k = to_client.to_json(orient="records")
    return jsonify(json.loads(k))


@app.route("/query", methods=["GET"])
def query():
    query = request.args.get("query")
    vecs = model.encode(query)

    def calculateSimilarity(preVec, rScore):
        cosSim = cosine_similarity([vecs], [np.array(literal_eval(preVec))])[0][0]
        return cosSim + ((4 - rScore) / 20)

    to_client = df.drop(
        [
            "symptoms",
            "index",
            "level_0",
            "primary_description",
            "secondary_description",
            "rarity",
            "symptom_possibility",
            "raw_symptoms",
        ],
        axis=1,
    )
    print(to_client["symptomVectors"])
    to_client["simScore"] = to_client.apply(
        lambda x: calculateSimilarity((x["symptomVectors"]), x["rarityScore"]),
        axis=1,
    )
    return jsonify(
        json.loads(
            to_client.drop(["symptomVectors", "rarityScore"], axis=1)
            .sort_values(by="simScore", ascending=False)
            .to_json(orient="records")
        )
    )


@app.route("/user/login", methods=["POST"])
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
                    "token": jwt.encode({"username": user.username}, SAMPLE_SECRET_KEY),
                    "user": user.username,
                    "d_list": user.d_list,
                }
            )
        else:
            return jsonify({"success": False, "message": "Incorrect password"})
    else:
        return jsonify({"success": False, "message": "User %s not found" % username})


@app.route("/user/register", methods=["POST"])
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
        db.session.commit()
        return jsonify(
            {
                "success": True,
                "token": jwt.encode({"username": user.username}, SAMPLE_SECRET_KEY),
                "user": user.username,
                "d_list": user.d_list,
            }
        )


@app.route("/user/tokenauth", methods=["POST"])
def tokenauth():
    token = request.headers.get("Authorization").split(" ")[1]
    tokenObject = jwt.decode(token, SAMPLE_SECRET_KEY, algorithms=["HS256"])
    username = tokenObject["username"]
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify(
            {
                "success": True,
                "token": jwt.encode({"username": user.username}, SAMPLE_SECRET_KEY),
                "user": user.username,
                "d_list": user.d_list,
            }
        )
    else:
        return jsonify({"success": False, "message": "User not found"})


@app.route("/user/profile/add", methods=["PUT"])
def additem():
    token = request.headers.get("Authorization").split(" ")[1]
    tokenObject = jwt.decode(token, SAMPLE_SECRET_KEY, algorithms=["HS256"])
    username = tokenObject["username"]
    user = User.query.filter_by(username=username).first()
    if user:
        data = request.json
        disease = data["label"]
        if len(user.d_list) + len(disease) > 498:
            return jsonify({"success": False, "message": "No more items can be added"})
        user.d_list += " " + disease
        user.d_list = user.d_list.strip()
        db.session.commit()
        return jsonify({"success": True, "d_list": user.d_list})


@app.route("/user/profile/remove", methods=["PUT"])
def removeitem():
    token = request.headers.get("Authorization").split(" ")[1]
    tokenObject = jwt.decode(token, SAMPLE_SECRET_KEY, algorithms=["HS256"])
    username = tokenObject["username"]
    user = User.query.filter_by(username=username).first()
    if user:
        data = request.json
        disease = data["label"]
        user.d_list = user.d_list.replace(disease, "").strip()
        user.d_list = user.d_list.strip()
        db.session.commit()
        return jsonify({"success": True, "d_list": user.d_list})


if __name__ == "__main__":
    app.run(debug=True)

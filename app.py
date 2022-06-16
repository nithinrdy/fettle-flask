from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json
import pandas as pd
from ast import literal_eval
from sqlalchemy import JSON
from flask_bcrypt import Bcrypt
import jwt


app = Flask(__name__)
bcrypt = Bcrypt(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
# model = SentenceTransformer('all-MiniLM-L12-v2')
df = pd.read_csv("diseases__encoded.csv").reset_index()

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
SAMPLE_SECRET_KEY = "secret"  # For local purposes

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    d_list = db.Column(JSON)

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


# @app.route('/query', methods=['GET'])
# def query():
#     query = request.args.get('query')
#     vecs = model.encode(query)
#     cosine_sim = cosine_similarity([vecs], df['symptomVectors'].values)
#     return jsonify({'similarity_score': str(cosine_sim[0][0])})


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
        user = User(username, bcrypt.generate_password_hash(password), [])
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


if __name__ == "__main__":
    app.run(debug=True)

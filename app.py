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


app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
# model = SentenceTransformer('all-MiniLM-L12-v2')
df = pd.read_csv('diseases__encoded.csv').reset_index()

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    d_list = db.Column(JSON)

    def __init__(self, username, password, d_list):
        self.username = username
        self.password = password
        self.d_list = d_list


@app.route('/')
def home():
    return jsonify({'test': 'Hello World!'})

@app.route('/data', methods=['GET'])
def data():
    to_client = df.drop(['symptomVectors', 'symptoms', 'index', 'level_0'], axis=1)
    k = to_client.to_json(orient='records')
    return jsonify(json.loads(k))

# @app.route('/query', methods=['GET'])
# def query():
#     query = request.args.get('query')
#     vecs = model.encode(query)
#     cosine_sim = cosine_similarity([vecs], df['symptomVectors'].values)
#     return jsonify({'similarity_score': str(cosine_sim[0][0])})

@app.route('/user/login')
def login():
    args = request.args
    username = args.get('username')
    password = args.get('password')
    user = User.query.filter_by(username=username).first()
    if user:
        if bcrypt.check_password_hash(user.password, password):
            return jsonify({'success': True, 'user': user.username, 'd_list': user.d_list})
        else:
            return jsonify({'success': False, 'message': 'Incorrect password'})
    else:
        return jsonify({'success': False, 'message': 'User not found'})

@app.route('/user/register')
def register():
    args = request.args
    username = args.get('username')
    password = args.get('password')
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({'success': False, 'message': 'User already exists'})
    else:
        user = User(username, bcrypt.generate_password_hash(password), [])
        db.session.add(user)
        db.session.commit()
        return jsonify({'success': True, 'user': user.username, 'd_list': user.d_list})




if __name__ == '__main__':
    app.run(debug=True)
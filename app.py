from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json
import pandas as pd
from ast import literal_eval


app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
# model = SentenceTransformer('all-MiniLM-L12-v2')
df = pd.read_csv('diseases__encoded.csv').reset_index()

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

@app.route('/test')
def test():
    return jsonify({'list': literal_eval(df['symptomVectors'].to_list()[0])})


if __name__ == '__main__':
    app.run(debug=True)
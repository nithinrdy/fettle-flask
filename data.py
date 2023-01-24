from flask import Blueprint, request, jsonify
import json
from sklearn.metrics.pairwise import cosine_similarity
from ast import literal_eval
from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np


# Blueprint for data endpoints
data_blueprint = Blueprint("data", __name__)

# Dataframe containing all diseases and their symptoms generated using the scraper
df = pd.read_csv("diseases__encoded.csv").reset_index()
model = SentenceTransformer("all-MiniLM-L12-v2") # Model used for similarity calculation


# Endpoint for returning all diseases and their symptoms as a JSON object
def data():
    to_client = df.drop(["symptomVectors", "symptoms", "index", "level_0"], axis=1)
    k = to_client.to_json(orient="records")
    return jsonify(json.loads(k))


# Endpoint for returning diseases that are similar to the query string, calculated using
# cosine similarity
def query():
    query = request.args.get("query")
    vecs = model.encode(query) # Generates vector for query string

    # Calculates cosine similarity between query and all diseases' symptoms; also factors
    # in the rarity of the disease.
    def calculateSimilarity(preVec, rScore):
        cosSim = cosine_similarity([vecs], [np.array(literal_eval(preVec))])[0][0]
        return cosSim + ((4 - rScore) / 20)

    # Drop unnecessary columns and add a new column containing the similarity score
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
    to_client["simScore"] = to_client.apply(
        lambda x: calculateSimilarity((x["symptomVectors"]), x["rarityScore"]),
        axis=1,
    )

    # JSONify the dataframe and return it
    return jsonify(
        json.loads(
            to_client.drop(["symptomVectors", "rarityScore"], axis=1)
            .sort_values(by="simScore", ascending=False)
            .to_json(orient="records")
        )
    )


# Map the functions to their respective endpoints as handlers
data_blueprint.add_url_rule("/data", view_func=data, methods=["GET"])
data_blueprint.add_url_rule("/query", view_func=query, methods=["GET"])
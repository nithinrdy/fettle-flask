# fettle's backend

This is the backend for fettle. It is a flask app that uses a sqlite database to store data, and serves data retrieved using fettle-scraper.

Uses the SentenceTransformer library to generate embeddings for the symptoms of each diseases, which are then used to find diseases whose symptoms match that of the user's query, which is determined using the cosine similarity between the embeddings.

Also uses BCrypt to hash passwords, and JWT to generate tokens for authentication.

## Installation

1. Clone the repository
2. Create a virtual environment and activate it
3. Install the requirements using `pip install -r requirements.txt`
4. Run the app using `python app.py` (or as a module using `python -m app`)

# fettle's backend

This is the backend for fettle. It is a flask app that uses an sqlite database to store user data, and serves data retrieved using [fettle-scraper](https://github.com/nithinrdy/fettle-scraper.git).

Uses the SentenceTransformer library to generate embeddings for the symptoms of each disease, which are then used to find diseases whose symptoms match that of the user's query, which is determined using the cosine similarity between the embeddings.

Also uses BCrypt to hash passwords, and JWT to generate tokens for authentication.

## Important

For the web app to function as intended, you'll need to perform an additional step, prior to installation (regardless of whether you do it manually or using Docker) -- you'll need to add the `diseases__encoded.csv` dataset to the root directory of the project, which can be generated using [the scraper I mentioned above](https://github.com/nithinrdy/fettle-scraper.git). This dataset contains the information served by the app.

## Installation

1. Clone the repository
2. Create a virtual environment and activate it
3. Install the requirements using `pip install -r requirements.txt`
4. Run the app using `python app.py` (or as a module using `python -m app`)

### Using Docker

1. Clone the repository
2. Build the image using `docker build -t <image_name> .`
3. Run the container using `docker run -p <any_open_port>:5000 -v <a_name_for_your_volume>:/working/instance <the_image_name>` (add a `-d` somewhere in there if you want to run the container in detached mode)
4. The app should be running on `localhost:<port_you_used_above>`

Note: Building the image will take a while, since the dependencies include a handful of HUGE libraries (like torch).

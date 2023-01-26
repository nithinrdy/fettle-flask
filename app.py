from flask import Flask
from flask_cors import CORS
from auth_profile import auth_blueprint, bcrypt, db
from data import data_blueprint


# Initialize the Flask app
app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

# Initialize bcrypt and db with the app instance
bcrypt.init_app(app)
db.init_app(app)

def create_tables():
    with app.app_context():
        db.create_all()


create_tables()


# Manually push the app context so that the db can be used outside of the application context
# (in the python shell, for example)
app.app_context().push()


# Registering both blueprints
app.register_blueprint(auth_blueprint)
app.register_blueprint(data_blueprint)


if __name__ == "__main__":
    app.run()

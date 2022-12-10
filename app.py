from flask import Flask
from flask_cors import CORS
from auth_profile import auth_blueprint, bcrypt, db
from data import data_blueprint


app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

bcrypt.init_app(app)
db.init_app(app)

app.app_context().push()


# Registering both blueprints
app.register_blueprint(auth_blueprint)
app.register_blueprint(data_blueprint)


if __name__ == "__main__":
    app.run()

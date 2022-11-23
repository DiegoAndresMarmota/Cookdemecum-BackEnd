import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, User

BASEDIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

# Configuración
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + \
    os.path.join(BASEDIR, "auth.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["ENV"] = "development"

CORS(app)
db.init_app(app)
Migrate(app, db)


# Rutas
@app.route("/")
def home():
    return "Hello There, Flask"


@app.route("/user", methods=["POST"])
def user():
    user = User()
    name = request.json.get("name")
    email = request.json.get("email")
    password = request.json.get("password")

    found_user = User.query.filter_by(email=email).first()
    if found_user is not None:
        return jsonify({
            "msg": "Email is already in use"
        }), 400


# Configuración Servidor
if __name__ == "__main__":
    app.run(port=8080, host="localhost")

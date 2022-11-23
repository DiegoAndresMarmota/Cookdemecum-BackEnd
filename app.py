import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from models import db, User


BASEDIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

# Configuración
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + \
    os.path.join(BASEDIR, "auth.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["ENV"] = "development"
app.config["SECRET_KEY"] = "super_secret_key"

CORS(app)
db.init_app(app)
Migrate(app, db)
bcrypt = Bcrypt(app)


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
    print(found_user)
    if found_user is not None:
        return jsonify({
            "msg": "Email is already in use"
        }), 400

    user.email = email
    user.name = name
    password_hash = bcrypt.generate_password_hash(password)
    user.password = password_hash

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "msg": "success creating user"
        "data": user.serialize()
    }), 200


# Configuración Servidor
if __name__ == "__main__":
    app.run(port=8080, host="localhost")

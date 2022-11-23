import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from datetime import datetime
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from models import db, User, Blog


BASEDIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

# Configuración
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + \
    os.path.join(BASEDIR, "app.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "super_secret_key"
app.config["JWT_SECRET_KEY"] = "super_jwt_key"
app.config["ENV"] = "development"
CORS(app)
db.init_app(app)
Migrate(app, db)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# RUTAS

# Ruta Inicial
@app.route("/", methods=["GET"])
def home():
    return "<h1> Hello There </h1>"


# CRUD - Iniciar sesión un nuevo usuario ya registrado
@app.route("/login", method=["POST"])
def login():
    email = request.json.get("email")
    password = request.json.get("password")

    found_user = User.query.filter_by(email=email).first

    if found_user is None:
        return jsonify({
            "msg": "El USUARIO no ha sido encontrado. Favor, crear un nuevo USUARIO"
        }), 404

    if bcrypt.check_password_hash(found_user.password, password):
        access_token = create_access_token(identity=email)
        return jsonify({
            "access_token": access_token,
            "data": found_user.serialize(),
            "success": True
        }), 200

    else:
        return jsonify({
            "msg": "la contraseña no es válida"
        })

#CRUD - Registrar usuario con cuenta nueva
@app.route("/registro", methods=["POST"])
def registro():
    name = request.json.get("name")
    email = request.json.get("email")
    password = request.json.get("password")

# CRUD - Obtener publicaciones de usuarios
@app.route("/users/posts", methods=["GET"])
@jwt_required()
def get_posts(id):
    all_posts = User.query.filter_by(id=id).first()
    all_posts = list(map(lambda user: user.serialize(), all_posts))
    if all_posts is not None:
        return jsonify(all_posts.serialize())


# CRUD - Certificar la autentificación de la contraseña

#db.session.add(user)
#db.session.commit()


# CRUD - Obtener la lista completa de los usuarios
@app.route("/list_users", methods=["GET"])
@jwt_required()
def get_users():
    try:
        all_users = User.query.all()
        all_users = list(
            map(lambda editdata: user.serialize(), all_list_users))
    except Exception as error:
        print("Editar error : {error}")
    return jsonify(all_users)


# CRUD - Editar perfil del usuario
@app.route("/edit_user/<int:id>", methods=["PUT"])
def update_user(id):
    if id is not None:
        user = User.query.filter_by(id=id).first()
        if user is not None:
            user.name = request.json.get("name")
            user.password = bcrypt.generate_password_hash(
                request.json.get("password"))

            db.session.commit()
            return jsonify(user.serialize()), 200
        else:
            return jsonify({
                "msg": "El perfil de TU USUARIO no ha sido encontrado"
            }), 404
    else:
        return jsonify({
            "msg": "El perfil de TU USUARIO no existe o no esta registrado "
        }), 400


#CRUD - Eliminar la cuenta de un Usuario registrado
@app.route("/registro/<int:id>", methods=['DELETE'])
def delete_user(id):
    if id is not None:
        user = User.query.filter_by(id=id).first()
        db.session.delete(user)
        db.session.commit()
        return jsonify({"msg": "La eliminación de TU CUENTA se ha efectuado"})
    else:
        return jsonify({"msg": "TU CUENTA no ha sido encontrada"}), 404





###################################
@app.route("/users")
@jwt_required()
def users():
    all_users = User.query.get_all()
    all_users = list(map(lambda user: user.serialize(), all_users))
    return jsonify({
        "data": all_users
    })


@app.route("/login", method=["POST"])
def login():
    email = request.json.get("email")
    password = request.json.get("password")

    found_user = User.query.filter_by(email=email).first

    if found_user is None:
        return jsonify({
            "msg": "User not found. Please create user"
        }), 404

    if bcrypt.check_password_hash(found_user.password, password):
        access_token = create_access_token(identity=email)
        return jsonify({
            "access_token": access_token,
            "data": found_user.serialize(),
            "success": True
        }), 200

    else:
        return jsonify({
            "msg": "password is invalid"
        })


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
        "msg": "success creating user",
        "data": user.serialize()
    }), 200


# Configuración Servidor
if __name__ == "__main__":
    app.run(port=8080, host="localhost")

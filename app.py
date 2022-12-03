import os
from flask import Flask, jsonify, request, g, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from datetime import datetime
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from models import db, User, Post
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename


BASEDIR = os.path.abspath(os.path.dirname(__file__))
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)

# Configuración
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + \
    os.path.join(BASEDIR, "app.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "super_secret_key"
app.config["JWT_SECRET_KEY"] = "super_jwt_key"
app.config["ENV"] = "development"
app.config["UPLOAD_FOLDER"] = os.path.join(BASEDIR, "images")

CORS(app)
db.init_app(app)
Migrate(app, db)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# RUTAS

# CRUD - INICIO - 1. Página de Inicio.


@app.route("/", methods=["GET"])
def home():
    return "<h1> Hello There </h1>"


# CRUD - USER - 2. Iniciar sesión un nuevo usuario ya registrado.
@app.route("/login", methods=["POST"])
def login():
    email = request.json.get("email")
    password = request.json.get("password")

    found_user = User.query.filter_by(email=email).first()

    if found_user is None:
        return jsonify({
            "msg": "El USUARIO no ha sido encontrado. Favor, crear un nuevo USUARIO"
        }), 404

    else:
        if bcrypt.check_password_hash(found_user.password, password):
            access_token = create_access_token(identity=email)
            return jsonify({
                "access_token": access_token,
                "data": found_user.serialize(),
                "success": True
            }), 200
        else:
            return jsonify({
                "msg": "La contraseña ES VÁLIDA"
            })


# CRUD - USER - 3. Registrar usuario con cuenta nueva.
@app.route("/register", methods=["POST"])
def register():
    # if request.method == 'POST':
    name = request.json.get("name")
    email = request.json.get("email")

    new_contact = User()
    new_contact.name = name
    new_contact.email = email
    new_contact.password = bcrypt.generate_password_hash(
        request.json.get("password"))

    db.session.add(new_contact)
    db.session.commit()

    flash('Usuario registrado satisfactoriamente')

    return jsonify({"msg": "Usuario registrado satisfactoriamente."})


# CRUD - USER - 4. Editar perfil del usuario.
@app.route("/editProfile/<int:id>", methods=["PUT"])
@jwt_required()
def editProfile(id):
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


# CRUD - USER - 5. Subir imagen del usuario.
@app.route("/upload_image/<int:id>", methods=["POST"])
@jwt_required()
def uploadImage(id):
    if "file" not in request.files:
        return jsonify({"msg": "La consulta de 'File' no ha sido solicitada."})
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"msg": "El archivo 'file' no contiene un nombre."})
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
    return jsonify({"msg": "La imagen ha sido guardada."})


# CRUD - USER - 6. Ver perfil personal del usuario.
@app.route("/miPerfil", methods=["GET"])
@jwt_required()
def getUserProfile():
    email = get_jwt_identity()
    user = User.query.filter_by(email=email).first()
    return jsonify({
        "user": user.serialize()
    }), 200

    """
    userProfile = userProfile.query.filter_by(id=id).first()
    userProfile = list(map(lambda user: user.serialize(), userProfile))
    return jsonify(userProfile.serialize), 200
    """

# CRUD - USER - 7. Ver lista completa de publicaciones del usuario.


@app.route("/getSoloUser/<int:id>/posts", methods=["GET"])
@jwt_required()
def getSoloUser(id):
    all_posts = User.query.filter_by(id=id).first()
    all_posts = list(map(lambda user: user.serialize(), all_posts))
    if all_posts is not None:
        return jsonify(all_posts.serialize())


# CRUD - USER - 8. Ver lista completa de usuarios.
@app.route("/getUsers", methods=["GET"])
@jwt_required()
def getUsers(id):
    try:
        all_users = User.query.all()
        all_users = list(
            map(lambda editdata: user.serialize(), all_users))
    except Exception as error:
        print("Editar error : {error}")
    return jsonify(all_users)


"""
# CRUD - BLOG - 9. Ver lista completa de publicaciones de los usuarios.
@app.route("/blogUsers", methods=["GET"])
@jwt_required()
def blogUsers():
    all_users = User.query.get_all()
    all_users = list(map(lambda user: user.serialize(), all_users))
    return jsonify({
        "data": all_users
    })
"""

# CRUD - BLOG - 10. Ver lista completa de publicaciones de tu perfil.


@app.route("/soloBlog/<int:id>", methods=["GET"])
@jwt_required()
def soloBlogs():
    all_blogs = Post.query.get_all()
    all_blogs = list(map(lambda post: post.serialize(), all_blogs))
    return jsonify({
        "data": all_blogs
    })

# CRUD - BLOG - 11. Comentar una publicación.


@app.route("/addBlog/<int:id>", methods=["GET", "POST"])
@jwt_required()
def addBlog():
    if request.method == 'POST':
        title = request.form.get('title')
        post = request.form.get('comentary')
        date = request.form.get('date')

        post = Post(g.user.id, title, post, date)

        error = None
        if not title:
            error = 'Se requiere un TITULO para esta publicación'

        if error is not None:
            flash(error)

        else:
            db.session.add(post)
            db.session.commit()
            return post

        flash(error)

    return jsonify({
        "msg": "El post de TU USUARIO ha sido encontrado publicada"
    }), 200


def get_post(id, check_author=True):
    post = Post.query.get(id)

    if post is None:
        abort(404, f'La {id} de la publicación NO EXIST.')

    if check_author and post.title != g.user.id:
        abort(404)

    return post


# CRUD - BLOG - 12. Editar una publicación.
@app.route("/editBlog/<int:id>", methods=["GET", "POST"])
@jwt_required()
def editBlog(id):

    post = get_post(id)

    if request.method == 'POST':
        post.title = request.form.get('title')
        post.post = request.form.get('post')
        post.date = request.form.get('date')

        error = None
        if not post.title:
            error = 'Se requiere un TITULO para esta publicación'

        if error is not None:
            flash(error)
        else:
            db.session.add(post)
            db.session.commit()
            return post.post

        flash(error)

    return jsonify({
        "msg": "La edición de este POST ha sido publicada"
    }), 200


# CRUD - BLOG - 13. Eliminar una publicación.
@app.route("/deletePost/<int:id>", methods=["DELETE"])
@jwt_required()
def deletePost(id):
    post = get_post(id)
    db.session.delete(post)
    db.session.commit()

    return jsonify({
        "msg": "Se elimino la PUBLICACIÓN de forma satisfactoria"
    }), 200


# CRUD - USER - 14. Eliminar la cuenta de un Usuario registrado
@app.route("/deleteUser/<int:id>", methods=["DELETE"])
@jwt_required()
def deleteUser(id):
    if id is not None:
        user = User.query.filter_by(id=id).first()
        db.session.delete(user)
        db.session.commit()
        return jsonify({"msg": "La eliminación de TU CUENTA se ha efectuado"})
    else:
        return jsonify({"msg": "TU CUENTA no ha sido encontrada"}), 404


# CRUD - USER - 15. Salir sesión de un usuario logeado
@app.route("/logout")
@jwt_required()
def logout():
    session.clear()
    return jsonify({
        "msg": "SU SESIÓN ha sido cerrada"
    })


# CRUD - USER - 16. Certificar la autentificación de la contraseña
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
            "msg": "El email ya HA SIDO registrado"
        }), 400

    user.email = email
    user.name = name
    password_hash = bcrypt.generate_password_hash(password)
    user.password = password_hash

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "msg": "Creación de USUARIO se ha realizado de forma satisfactoria",
        "data": user.serialize()
    }), 200


# Configuración Servidor
if __name__ == "__main__":
    app.run(port=8080, host="localhost")

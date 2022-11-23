from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False, unique=False)
    
    def __repr__(self) -> str:
        return "<User %r>" % self.name

    def serialize (self):
        return {
            "id": self.id,
            "username": self.name,
            "email": self.email,
            "password": self.password,
        }

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    author = db.Column(db.String(30), nullable=False)
    comentary = db.Column(db.String(30), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def _repr_(self):
        return "<Product %r>" % self.title

    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "autor": self.author,
            "comentary": self.comentary,
            "user_id": self.user_id
        }

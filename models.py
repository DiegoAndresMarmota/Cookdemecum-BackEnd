from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    bio = db.Column(db.String(50), nullable=False)
    image = db.Column(db.ImageField, nullable=False)                                ######################
    password = db.Column(db.String(50), nullable=False, unique=False)
    #post = db.relationship("Post")

    def __repr__(self) -> str:
        return "<User %r>" % self.name

    def serialize(self):
        return {
            "id": self.id,
            "username": self.name,
            "email": self.email,
            "bio": self.bio,
            "image": self.image
            # "password": self.password,
        }


class Blog(db.Model):
    __tablename__ = "blogs"
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.DateTimeField, nullable=False, default=datetime.utcnow)
    posts = db.relantioship("Comment")

    def _repr_(self):
        return "<Product %r>" % self.body                              ##############################

    def serialize(self):
        return {
            "id": self.id,
            "body": self.body,
            "user_id": self.user_id,
            "date": self.date
        }


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    blog = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    text = db.Column(db.String(300), nullable=False)
    date = db.Column(db.DateTime(20), nullable=False, default=datetime.utcnow)
    user = db.relationship("Blog")

    def _repr_(self):
        return "<Post %r>" % self.title

    def serialize(self):
        return {
            "id": self.id,
            "blog": self.blog,
            "user_id": self.user_id,
            "text": self.text,
            "date": self.date
        }

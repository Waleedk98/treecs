from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()
bcrypt = Bcrypt()

# Datenbank-Modelle
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uname = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Beziehungen
    trees = db.relationship('Tree', backref='user', lazy=True)


class Tree(db.Model):
    __tablename__ = 'trees'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    tree_type = db.Column(db.String(100), nullable=False)
    tree_height = db.Column(db.Integer, nullable=False)
    inclination = db.Column(db.Integer, nullable=False)
    trunk_diameter = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    latitude = db.Column(db.Numeric(10, 8), nullable=False)
    longitude = db.Column(db.Numeric(11, 8), nullable=False)
    address = db.Column(db.String(255), nullable=True)

    # Beziehungen
    photos = db.relationship('TreePhoto', backref='tree', lazy=True)


class TreePhoto(db.Model):
    __tablename__ = 'tree_photos'

    id = db.Column(db.Integer, primary_key=True)
    tree_id = db.Column(db.Integer, db.ForeignKey('trees.id'), nullable=False)  # Referenz zur 'trees' Tabelle
    photo_path = db.Column(db.String(255), nullable=True)
    photo_blob = db.Column(db.LargeBinary, nullable=True)
    photo_metadata = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<TreePhoto id={self.id} tree_id={self.tree_id}>"

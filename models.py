# models.py
from extensions import db
from flask_login import UserMixin
from datetime import datetime
import os
import random
import string

# User Modell
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uname = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    salt = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Methode zum Generieren eines Salts
    @staticmethod
    def generate_salt(length=16):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Tree Modell
class Tree(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tree_type = db.Column(db.String(100), nullable=False)
    tree_height = db.Column(db.Float, nullable=False)
    inclination = db.Column(db.Float, nullable=False)
    trunk_diameter = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Beziehung
    user = db.relationship('User', backref=db.backref('trees', lazy=True))

# TreePhoto Modell (Optional, falls benötigt)
class TreePhoto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tree_id = db.Column(db.Integer, db.ForeignKey('tree.id'), nullable=False)
    photo_path = db.Column(db.String(300), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Beziehung
    tree = db.relationship('Tree', backref=db.backref('photos', lazy=True))

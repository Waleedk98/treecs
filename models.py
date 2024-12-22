# models.py
from extensions import db
from flask_login import UserMixin
from datetime import datetime
import os
import random
import string

db = SQLAlchemy()
bcrypt = Bcrypt()

# Datenbank-Modelle
class TrustLevel(db.Model):
    __tablename__ = 'trust_levels'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rank = db.Column(db.String(128), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<TrustLevel id={self.id} rank={self.rank}>"


class AccountType(db.Model):
    __tablename__ = 'account_types'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type_name = db.Column(db.String(128), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<AccountType id={self.id} type_name={self.type_name}>"


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uname = db.Column(db.String(128), unique=True, nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    latitude = db.Column(db.Numeric(8, 6), nullable=False)
    longitude = db.Column(db.Numeric(9, 6), nullable=False)
    verified = db.Column(db.Boolean, default=False, nullable=False)
    trust_level_id = db.Column(db.Integer, db.ForeignKey('trust_levels.id'), nullable=False, default=1)
    password = db.Column(db.String(256), nullable=False)  # Gehashter Wert
    salt = db.Column(db.String(16), nullable=False)
    xp = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Beziehungen
    trust_level = db.relationship('TrustLevel', backref='users')
    roles = db.relationship('UserRole', backref='user', lazy=True)
    trees = db.relationship('Tree', backref='initial_creator', lazy=True)

    @staticmethod
    def generate_salt():
        import os
        return os.urandom(16).hex()

    def __repr__(self):
        return f"<User id={self.id} uname={self.uname} email={self.email}>"


class UserRole(db.Model):
    __tablename__ = 'user_roles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    account_type_id = db.Column(db.Integer, db.ForeignKey('account_types.id'), nullable=False)

    # Beziehungen
    account_type = db.relationship('AccountType', backref='user_roles')

    def __repr__(self):
        return f"<UserRole id={self.id} user_id={self.user_id} account_type_id={self.account_type_id}>"


class TreeType(db.Model):
    __tablename__ = 'tree_types'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False, unique=True)
    true_type = db.Column(db.String(128), nullable=False)
    co2_compensation_rate = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)

    def __repr__(self):
        return f"<TreeType id={self.id} name={self.name}>"


class HealthStatus(db.Model):
    __tablename__ = 'health_statuses'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status = db.Column(db.String(128), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<HealthStatus id={self.id} status={self.status}>"


class Tree(db.Model):
    __tablename__ = 'trees'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    initial_creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    tree_type_id = db.Column(db.Integer, db.ForeignKey('tree_types.id'))
    latitude = db.Column(db.Numeric(8, 6), nullable=False)
    longitude = db.Column(db.Numeric(9, 6), nullable=False)
    co2_stored = db.Column(db.Numeric(10, 2), default=0.00)
    health_status_id = db.Column(db.Integer, db.ForeignKey('health_statuses.id'), nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Beziehungen
    tree_type = db.relationship('TreeType', backref='trees')
    health_status = db.relationship('HealthStatus', backref='trees')
    measurements = db.relationship('Measurement', backref='tree', lazy=True)
    photos = db.relationship('TreePhoto', backref='tree', lazy=True)

    def __repr__(self):
        return f"<Tree id={self.id} latitude={self.latitude} longitude={self.longitude}>"


class Measurement(db.Model):
    __tablename__ = 'measurements'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tree_id = db.Column(db.Integer, db.ForeignKey('trees.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    suspected_tree_type = db.Column(db.String(128))
    height = db.Column(db.Numeric(5, 2), nullable=False)
    inclination = db.Column(db.Integer, nullable=False)
    trunk_diameter = db.Column(db.Numeric(5, 2), nullable=False)
    notes = db.Column(db.Text)
    collected_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Measurement id={self.id} tree_id={self.tree_id} height={self.height}>"


class TreePhoto(db.Model):
    __tablename__ = 'tree_photos'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tree_id = db.Column(db.Integer, db.ForeignKey('trees.id'), nullable=False)
    measurement_id = db.Column(db.Integer, db.ForeignKey('measurements.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    photo_path = db.Column(db.String(512), nullable=False)
    description = db.Column(db.Text)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<TreePhoto id={self.id} tree_id={self.tree_id}>"


class CommunityContribution(db.Model):
    __tablename__ = 'community_contributions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tree_id = db.Column(db.Integer, db.ForeignKey('trees.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    contribution_type = db.Column(db.String(128))
    description = db.Column(db.Text)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<CommunityContribution id={self.id} tree_id={self.tree_id}>"


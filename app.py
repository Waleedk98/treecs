from flask import Flask, request, jsonify, render_template, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import math
import requests
from datetime import datetime
import logging

# Konfiguration und Setup
app = Flask(__name__)
app.secret_key = 'test'  # Sicherer Schlüssel für Sitzungen

# Datenbank-Konfiguration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Datenbank-Modelle
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    beta = db.Column(db.Float, nullable=False)
    distance = db.Column(db.Float, nullable=False)
    height = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Login-Manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Registrierung
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        if User.query.filter_by(username=username).first():
            return "Benutzername existiert bereits", 400

        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect("/login")
    return render_template("register.html")

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            session["user_id"] = user.id
            return redirect("/")
        return "Ungültige Anmeldedaten", 401
    return render_template("login.html")

# Logout
@app.route("/logout")
def logout():
    logout_user()
    session.clear()
    return redirect("/login")

# Startseite (geschützt)
@app.route("/")
@login_required
def home():
    return render_template("index.html")

# Route, um Sensor-Daten zu empfangen und zu speichern
@app.route("/submit_sensor_data", methods=["POST"])
@login_required
def submit_sensor_data():
    data = request.json

    # Überprüfen, ob alle erforderlichen Daten vorhanden sind
    if not all([data.get("latitude"), data.get("longitude"), data.get("beta"), data.get("distance"), data.get("location")]):
        return jsonify({"error": "Fehlende Daten"}), 400

    latitude = data.get("latitude")
    longitude = data.get("longitude")
    beta = data.get("beta")
    distance = data.get("distance")
    location = data.get("location")  # Standort aus der Anfrage

    # Umrechnung von Grad in Radiant
    beta_radians = math.radians(beta)

    # Berechnung der Baumhöhe
    height = distance * math.tan(beta_radians)

# Baumhöhe und Standort in der Datenbank speichern
    tree_data = SensorData(
        user_id=current_user.id,
        latitude=latitude,
        longitude=longitude,
        location=location,  # Speichern der korrekten Adresse
        height=round(height, 2),
        beta=beta,  # Hinzufügen des Winkels
        distance=distance,  # Speichern der Entfernung
        timestamp=datetime.now()
    )
    db.session.add(tree_data)
    db.session.commit()

    # Antwort an den Client
    return jsonify({"height": round(height, 2)})    

@app.route('/dashboard')
@login_required
def dashboard():
    # Hole ALLE Einträge aus der SensorData-Tabelle
    tree_data = SensorData.query.all()
    return render_template('dashboard.html', tree_data=tree_data, current_user=current_user)


# Hauptprogramm
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Stelle sicher, dass die Tabellen erstellt werden
    app.run(host="0.0.0.0", port=5000, debug=True)

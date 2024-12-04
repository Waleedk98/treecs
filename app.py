from flask import Flask, request, jsonify, render_template, redirect, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime
from extensions import db, bcrypt
from models import db, bcrypt, User, Tree, TreePhoto  # Importiere Modelle und Datenbank
import os

# Konfiguration und Setup
app = Flask(__name__)
app.secret_key = 'test'  # Sicherer Schlüssel für Sitzungen

# Datenbank-Konfiguration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
bcrypt.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# Login-Manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Registrierung
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        uname = request.form.get("uname")
        password = request.form.get("password")
        email = request.form.get("email")

        # Überprüfen, ob Benutzername oder E-Mail bereits existiert
        if User.query.filter_by(uname=uname).first():
            return "Benutzername existiert bereits", 400
        
        if User.query.filter_by(email=email).first():
            return "E-Mail existiert bereits", 400

        # Salt generieren
        salt = User.generate_salt()

        # Passwort mit Salt kombinieren und hashen
        salted_password = password + salt
        hashed_password = bcrypt.generate_password_hash(salted_password).decode("utf-8")

        # Neuen Benutzer erstellen
        new_user = User(uname=uname, password=hashed_password, salt=salt, email=email)
        db.session.add(new_user)
        db.session.commit()

        return redirect("/login")

    return render_template("register.html")


# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        account_type = request.form.get("account_type")
        
        if account_type == "Guest":
            # Gastbenutzer erstellen
            guest_user = User(
                uname="Anonymous",
                password="guest",  # Dummy-Passwort
                email="guest@gmail.com"  # Dummy-E-Mail
            )
            db.session.add(guest_user)
            db.session.commit()
            login_user(guest_user)
            session["user_id"] = guest_user.id
            return redirect("/")
        
        # Standardbenutzeranmeldung
        uname = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(uname=uname).first()

        if user:
            # Passwort mit Salt kombinieren
            salted_password = password + user.salt

            # Passwort überprüfen
            if bcrypt.check_password_hash(user.password, salted_password):
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

# Route, um Baumdaten zu empfangen und zu speichern
@app.route("/submit_tree_data", methods=["POST"])
@login_required
def submit_tree_data():
    data = request.json

    # Überprüfen, ob alle erforderlichen Daten vorhanden sind
    required_fields = ["tree_type", "tree_height", "inclination", "trunk_diameter", "latitude", "longitude", "address"]
    if not all([data.get(field) for field in required_fields]):
        return jsonify({"error": "Fehlende Daten"}), 400

    trees = Tree(
        user_id=current_user.id,
        tree_type=data.get("tree_type"),
        tree_height=data.get("tree_height"),
        inclination=data.get("inclination"),
        trunk_diameter=data.get("trunk_diameter"),
        latitude=data.get("latitude"),
        longitude=data.get("longitude"),
        address=data.get("address")
    )

    db.session.add(trees)
    db.session.commit()

    return jsonify({"message": "Baumdaten erfolgreich gespeichert"})

@app.route('/dashboard')
@login_required
def dashboard():
    # Lade alle Bäume des aktuellen Nutzers und füge die User-Daten hinzu
    trees = (
        Tree.query
        .filter_by(user_id=current_user.id)
        .options(joinedload(Tree.user))  # Verbinde die User-Daten mit Tree-Daten
        .all()
    )
    
    return render_template('dashboard.html', trees=trees, current_user=current_user)
# Hauptprogramm
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Stelle sicher, dass die Tabellen erstellt werden
    app.run(host="0.0.0.0", port=5000, debug=True)

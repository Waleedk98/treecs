# routes.py
from flask import request, jsonify, render_template, redirect, session
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from models import TrustLevel, User, UserRole, Tree, Measurement, TreeType, HealthStatus, TreePhoto, CommunityContribution, AccountType
from extensions import db, bcrypt_instance
from sqlalchemy.orm import joinedload

def init_routes(app):
    # Login-Manager
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

            trust_level = TrustLevel(rank="Basic", description="Standard Trust Level")
            db.session.add(trust_level)
            db.session.commit()
            
            account_type = AccountType(type_name="User", description="Standard Account Type")
            db.session.add(account_type)
            db.session.commit()

            # Salt generieren
            salt = User.generate_salt()

            # Passwort mit Salt kombinieren und hashen
            salted_password = password + salt
            hashed_password = bcrypt_instance.generate_password_hash(salted_password).decode("utf-8")

            # Neuen Benutzer erstellen und TrustLevel zuweisen
            new_user = User(
                uname=uname, 
                password=hashed_password, 
                salt=salt, 
                email=email, 
                trust_level_id=trust_level.id  # Hier wird der TrustLevel hinzugefügt
            )

            db.session.add(new_user)
            db.session.commit()
            
            user_role = UserRole(user_id=new_user.id, account_type_id=account_type.id)
            db.session.add(user_role)
            db.session.commit()

            return redirect("/login")

        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            account_type = request.form.get("account_type")

            if account_type == "Guest":
                # Überprüfen, ob ein Gastbenutzer bereits existiert
                guest_user = User.query.filter_by(uname="Anonymous").first()

                if not guest_user:
                    # Gastbenutzer erstellen, falls nicht vorhanden
                    guest_user = User(
                        uname="Anonymous",
                        password=bcrypt_instance.generate_password_hash("guest").decode('utf-8'),  # Dummy-Passwort sicher speichern
                        salt="dummy_salt",  # Dummy-Wert für Salt
                        email="guest@gmail.com",  # Dummy-E-Mail
                        verified=False,  # Optional, falls in Ihrem Modell vorhanden
                        trust_level_id=1,  # Standard TrustLevel (ID=1)
                        created_at=datetime.utcnow()  # Falls ein Erstellungsdatum erforderlich ist
                    )
                    db.session.add(guest_user)
                    db.session.commit()

                # Gastbenutzer anmelden
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
                if bcrypt_instance.check_password_hash(user.password, salted_password):
                    login_user(user)
                    session["user_id"] = user.id
                    return redirect("/")

            return "Ungültige Anmeldedaten", 401

        return render_template("login.html")

    @app.route("/logout")
    def logout():
        logout_user()
        session.clear()
        return redirect("/login")

    @app.route("/")
    @login_required
    def home():
        return render_template("index.html")

    @app.route("/submit_tree_data", methods=["POST"])
    @login_required
    def submit_tree_data():
        data = request.json

        # Überprüfen, ob alle erforderlichen Daten vorhanden sind
        required_fields = ["tree_type", "tree_height", "inclination", "trunk_diameter", "latitude", "longitude", "address"]
        if not all([data.get(field) for field in required_fields]):
            return jsonify({"error": "Fehlende Daten"}), 400

        
        userTree = Tree(
            user_id=current_user.id,
            tree_type=data.get("tree_type"),
            tree_height=data.get("tree_height"),
            inclination=data.get("inclination"),
            trunk_diameter=data.get("trunk_diameter"),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            address=data.get("address")
        )

        db.session.add(userTree)
        db.session.commit()
        
        userMeasurement = Measurement(
            user_id=current_user.id,
            tree_id=userTree.id,
            #measurerName=data.get("measurerName"),
            suspected_tree_type=data.get("tree_type"),
            height=data.get("tree_height"),
            inclination=data.get("inclination"),
            trunk_diameter=data.get("trunk_diameter"),
            
        )
        
        db.session.add(userMeasurement)
        db.session.commit()
        
        # Benutzer-XP aktualisieren
        user = User.query.get(current_user.id)  # Benutzer aus der Datenbank holen
        if user:
            user.xp = (user.xp or 0) + 5  # 5 XP hinzufügen
            db.session.commit()

        return jsonify({"message": "Baumdaten erfolgreich gespeichert"})

    @app.route('/dashboard')
    @login_required
    def dashboard():# Fetch trees associated with the current user
      trees = (
        Tree.query
        .filter_by(user_id=current_user.id)  # Filter trees by the logged-in user's ID
        .all()
    )

      return render_template('dashboard.html', trees=trees, current_user=current_user)
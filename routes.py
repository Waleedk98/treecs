# routes.py
from flask import request, jsonify, render_template, redirect, session
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from models import TrustLevel, User, UserRole, Tree, Measurement, TreeType, HealthStatus, TreePhoto, CommunityContribution, AccountType
from extensions import db, bcrypt_instance
from sqlalchemy.orm import joinedload
import os


def init_routes(app):
    # Funktion zur Überprüfung erlaubter Dateitypen
    def allowed_file(filename):
        allowed_extensions = app.config['ALLOWED_EXTENSIONS']
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

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
        #print("Content-Type der Anfrage:", request.content_type)
        #print("Dateien in Anfrage:", request.files)   # Erwartet Dateien
        # Use request.form for data coming from an HTML form
        tree_type = request.form.get("tree_type")
        tree_height = request.form.get("tree_height")
        inclination = request.form.get("inclination")
        trunk_diameter = request.form.get("trunk_diameter")
        latitude = request.form.get("latitude")
        longitude = request.form.get("longitude")
        address = request.form.get("address")

        # Validate required fields
        required_fields = [tree_type, tree_height, inclination, trunk_diameter, latitude, longitude, address]
        if not all(required_fields):
            return jsonify({"error": "Fehlende Daten. Bitte alle Felder ausfüllen."}), 400
        # Test if all pictures are uploaded
        if "tree_photos" not in request.files:
            return jsonify({"error": "Keine Bilder hochgeladen"}), 400
        
        # Get Files out of Request
        files = request.files.getlist("tree_photos")
        if not files or len(files) == 0:
            return jsonify({"error": "Keine Dateien gefunden."}), 400

        try:
            # Create new Tree object
            newTree = Tree(
                user_id=current_user.id,
                tree_type=tree_type,
                tree_height=float(tree_height),
                inclination=float(inclination),
                trunk_diameter=float(trunk_diameter),
                latitude=float(latitude),
                longitude=float(longitude),
                address=address or "Unbekannter Standort",  # Default address if none provided
                
            )

            # Save to database
            db.session.add(newTree)
            db.session.commit()
            
            newMeasurement = Measurement (
                 user_id=current_user.id,
                 tree_id=newTree.id,
                 suspected_tree_type=tree_type,
                 height=float(tree_height),
                 inclination=float(inclination),
                 trunk_diameter=float(trunk_diameter),
             )  
            
            db.session.add(newMeasurement)
            db.session.commit()

             # Bilder speichern und in TreePhoto einfügen
            uploaded_files = []
            for file in files:
                #print("Datei gefunden:", file.filename)
                if file and allowed_file(file.filename):
                    # Sicheren Dateinamen erstellen
                    filename = file.filename
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                    # Datei speichern
                    file.save(filepath)
                    uploaded_files.append(filename)

                    # In der TreePhoto-Tabelle speichern
                    newPhoto = TreePhoto(
                    tree_id=newTree.id,
                    measurement_id=newMeasurement.id,
                    user_id=current_user.id,
                    photo_path=filepath,
                    description=f"Foto für Baum {tree_type}"
                    )
                
            db.session.add(newPhoto)
            db.session.commit()

            return redirect("/dashboard")

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Es ist ein Fehler aufgetreten: {str(e)}"}), 500

    @app.route('/dashboard')
    @login_required
    def dashboard():
        # Fetch trees associated with the current user
        trees = (
            Tree.query
            .filter_by(user_id=current_user.id)  # Filter trees by the logged-in user's ID
            .all()
        )

        return render_template('dashboard.html', trees=trees, current_user=current_user)
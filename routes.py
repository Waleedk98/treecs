from flask import Flask, request, jsonify, render_template, redirect, session, url_for
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from models import TrustLevel, User, UserRole, Tree, Measurement, TreeType, HealthStatus, TreePhoto, CommunityContribution, AccountType
from extensions import db, bcrypt_instance
from functions import get_gps_data_exifread, get_address_from_coordinates
from sqlalchemy.orm import joinedload
from werkzeug.utils import secure_filename
import os

def init_routes(app):
    # Function to check allowed file types
    def allowed_file(filename):
        allowed_extensions = app.config['ALLOWED_EXTENSIONS']
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

    # Default route
    @app.route("/")
    def home():
        if current_user.is_authenticated:
            return redirect("/mainmenu")
        return redirect("/login")

    # Register route
    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            uname = request.form.get("uname")
            password = request.form.get("password")
            email = request.form.get("email")

            # Check if username or email already exists
            if User.query.filter_by(uname=uname).first():
                return "Benutzername existiert bereits", 400

            if User.query.filter_by(email=email).first():
                return "E-Mail existiert bereits", 400

            # Holen des Standard TrustLevels mit ID 1 (Basic)
            trust_level = TrustLevel.query.get(1)
            if not trust_level:
                return "Fehler: Der Standard TrustLevel (ID 1) wurde nicht gefunden.", 500

            account_type = AccountType(type_name="User", description="Standard Account Type")
            db.session.add(account_type)
            db.session.commit()

            # Generate salt and hash password
            salt = User.generate_salt()
            salted_password = password + salt
            hashed_password = bcrypt_instance.generate_password_hash(salted_password).decode("utf-8")

            # Create new user and assign TrustLevel
            new_user = User(
                uname=uname,
                password=hashed_password,
                salt=salt,
                email=email,
                trust_level_id=trust_level.id
            )
            db.session.add(new_user)
            db.session.commit()

            user_role = UserRole(user_id=new_user.id, account_type_id=account_type.id)
            db.session.add(user_role)
            db.session.commit()

            # Log in the newly registered user
            login_user(new_user)
            session["user_id"] = new_user.id
            return redirect("/mainmenu")

        return render_template("register.html")

    # Login route
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            uname = request.form.get("username")
            password = request.form.get("password")
            user = User.query.filter_by(uname=uname).first()

            if user:
                salted_password = password + user.salt
                if bcrypt_instance.check_password_hash(user.password, salted_password):
                    login_user(user)
                    session["user_id"] = user.id
                    return redirect("/mainmenu")

            return "Ungültige Anmeldedaten", 401

        return render_template("login.html")

    # Logout route
    @app.route("/logout")
    def logout():
        logout_user()
        session.clear()
        return redirect("/login")

    # Main menu route
    @app.route("/mainmenu")
    @login_required
    def mainmenu():
        return render_template("mainmenu.html", current_user=current_user)
    
    @app.route("/index", methods=["GET"])
    @login_required
    def index():
        return render_template("index.html")
    

    
    # Submit tree data route
    @app.route("/submit_tree_data", methods=["POST"])
    @login_required
    def submit_tree_data():
        tree_type = request.form.get("tree_type")
        tree_height = request.form.get("tree_height")
        inclination = request.form.get("inclination")
        trunk_diameter = request.form.get("trunk_diameter")
        address = request.form.get("address")

        # Validierung der erforderlichen Felder ohne Geodaten
        required_fields = [tree_type, tree_height, inclination, trunk_diameter]
        if not all(required_fields):
            return jsonify({"error": "Fehlende Daten. Bitte alle Felder ausfüllen."}), 400

        # Überprüfung, ob Bilder hochgeladen wurden
        if "tree_photos" not in request.files:
            return jsonify({"error": "Keine Bilder hochgeladen"}), 400

        files = request.files.getlist("tree_photos")
        if not files or len(files) == 0:
            return jsonify({"error": "Keine Dateien gefunden."}), 400

        # GPS-Daten aus dem ersten Bild extrahieren
        first_file = files[0]
        gps_coords = get_gps_data_exifread(first_file)  # Funktion zum Abrufen von GPS-Daten
        if not gps_coords:
            return jsonify({"error": "Das erste Bild enthält keine GPS-Daten. Stellen Sie sicher, dass das Bild Geotags enthält."}), 400

        # Extrahierte GPS-Daten verwenden
        extracted_latitude, extracted_longitude = gps_coords
        
        # Debug-Ausgabe der GPS-Daten
        #print(f"Extrahierte GPS-Daten: Latitude={extracted_latitude}, Longitude={extracted_longitude}")

        address = get_address_from_coordinates(extracted_latitude, extracted_longitude)
        try:
            tree_type_obj = TreeType.query.filter_by(name=tree_type).first()

            newTree = Tree(
                user_id=current_user.id,
                tree_type_id=tree_type_obj.id,
                tree_height=float(tree_height),
                inclination=float(inclination),
                trunk_diameter=float(trunk_diameter),
                latitude=float(extracted_latitude),
                longitude=float(extracted_longitude),
                address=address or "Unbekannter Standort"
            )
            db.session.add(newTree)
            db.session.commit()

            newMeasurement = Measurement(
                user_id=current_user.id,
                tree_id=newTree.id,
                suspected_tree_type=tree_type,
                height=float(tree_height),
                inclination=float(inclination),
                trunk_diameter=float(trunk_diameter),
            )
            db.session.add(newMeasurement)
            db.session.commit()

            # Speicherpfad für Bilder im 'static/uploads/tree_photos/'
            upload_folder = app.config['UPLOAD_FOLDER']  # z.B. 'static/uploads/tree_photos/'

            # Stelle sicher, dass der Ordner existiert
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            # Verarbeite die Bilder
            for file in files:
                if file and allowed_file(file.filename):
                 # Sicherstellen, dass der Dateiname sicher ist
                    filename = secure_filename(file.filename)

                    # Speichern der Datei im richtigen Ordner
                    filepath = os.path.join(upload_folder, filename)
                    file.save(filepath)

                    newPhoto = TreePhoto(
                        tree_id=newTree.id,
                        measurement_id=newMeasurement.id,
                        user_id=current_user.id,
                        photo_path=filepath,
                        description=f"Foto für Baum {tree_type}"
                    )
                    db.session.add(newPhoto)
                    db.session.commit()

            newContribution = CommunityContribution(
                tree_id=newTree.id,
                user_id=current_user.id,
                contribution_type="Added Tree",
                description=""
            )
            db.session.add(newContribution)
            db.session.commit()

            return redirect("/dashboard")

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Es ist ein Fehler aufgetreten: {str(e)}"}), 500


    # Dashboard route
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
    # Fetch trees with their associated photos for the current user
        trees = (
        Tree.query
        .filter_by(user_id=current_user.id)  # Only fetch trees for the logged-in user
        .options(joinedload(Tree.photos))  # Eagerly load photos associated with each tree
        .all()
    )
        return render_template('dashboard.html', trees=trees, current_user=current_user)
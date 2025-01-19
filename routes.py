from flask import Flask, request, jsonify, render_template, redirect, session, url_for
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from models import TrustLevel, User, UserRole, Tree, Measurement, TreeType, HealthStatus, TreePhoto, CommunityContribution, AccountType
from extensions import db, bcrypt_instance
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

            # Create default trust level and account type
            trust_level = TrustLevel(rank="Basic", description="Standard Trust Level")
            db.session.add(trust_level)
            db.session.commit()

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

        files = request.files.getlist("tree_photos")
        if not files or len(files) == 0:
            return jsonify({"error": "Keine Dateien gefunden."}), 400

        try:
            tree_type_obj = TreeType.query.filter_by(name=tree_type).first()

            newTree = Tree(
                user_id=current_user.id,
                tree_type_id=tree_type_obj.id,
                tree_height=float(tree_height),
                inclination=float(inclination),
                trunk_diameter=float(trunk_diameter),
                latitude=float(latitude),
                longitude=float(longitude),
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

            for file in files:
                if file and allowed_file(file.filename):
                    filename = file.filename
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
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
        trees = Tree.query.filter_by(user_id=current_user.id).all()
        return render_template('dashboard.html', trees=trees, current_user=current_user)
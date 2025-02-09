from flask import Flask, request, jsonify, render_template, redirect, session, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from models import User, Tree, TreeType, Measurement
from extensions import db, bcrypt_instance
from sqlalchemy.orm import joinedload
from werkzeug.security import generate_password_hash, check_password_hash
from logic.register import handle_register
from logic.login import handle_login
from logic.submit_tree import handle_submit_tree
from logic.Email_Verification import handle_verify_email
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

def init_routes(app):
    # Default route
    @app.route("/")
    def home():
        if current_user.is_authenticated:
            return redirect("/mainmenu")
        return redirect("/login")

    #Email-Verification
    @app.route('/verify_email/<token>')
    def verify_email(token):
        return handle_verify_email(token)

    # Register route
    @app.route("/register", methods=["GET", "POST"])
    def register():
        return handle_register()

    # Login route
    @app.route("/login", methods=["GET", "POST"])
    def login():
        return handle_login()

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

    # ✅ Submit tree data route (Now directly jumps to Dashboard)
    @app.route("/submit_tree_data", methods=["POST"])
    @login_required
    def submit_tree_data():
        try:
            return handle_submit_tree(request)  # ✅ Directly handles redirection to `/dashboard`
        except Exception as e:
            logging.error(f"Fehler beim Speichern der Baumdaten: {e}")
            flash("Ein unerwarteter Fehler ist aufgetreten!", "danger")
            return redirect(url_for('index'))  # Redirect to the form if something goes wrong

    # ✅ Dashboard route
    @app.route('/dashboard')
    @login_required
    def dashboard():
        trees = (
            Tree.query
            .filter_by(user_id=current_user.id)
            .options(joinedload(Tree.photos))  # Load associated tree photos
            .all()
        )
        return render_template('dashboard.html', trees=trees, current_user=current_user)

    # ✅ Profile route
    @app.route('/profile')
    @login_required
    def profile():
        return render_template("profile.html", current_user=current_user)

    # ✅ Update profile information
    @app.route('/update_profile', methods=['POST'])
    @login_required
    def update_profile():
        try:
            new_uname = request.form.get("uname")
            new_email = request.form.get("email")

            if not new_uname or not new_email:
                flash("Benutzername und E-Mail dürfen nicht leer sein!", "danger")
                return redirect(url_for('meinprofil'))

            existing_user_uname = User.query.filter(User.uname == new_uname, User.id != current_user.id).first()
            existing_user_email = User.query.filter(User.email == new_email, User.id != current_user.id).first()

            if existing_user_uname:
                flash("Dieser Benutzername ist bereits vergeben!", "danger")
                return redirect(url_for('meinprofil'))

            if existing_user_email:
                flash("Diese E-Mail wird bereits verwendet!", "danger")
                return redirect(url_for('meinprofil'))

            current_user.uname = new_uname
            current_user.email = new_email
            db.session.commit()

            flash("Profil erfolgreich aktualisiert!", "success")
            return redirect(url_for('meinprofil'))
        except Exception as e:
            logging.error(f"Fehler beim Aktualisieren des Profils: {e}")
            flash("Ein Fehler ist aufgetreten!", "danger")
            return redirect(url_for('meinprofil'))

    # ✅ Change password route
    @app.route('/update_password', methods=['POST'])
    @login_required
    def update_password():
        try:
            current_password = request.form.get("current_password")
            new_password = request.form.get("new_password")

            if not bcrypt_instance.check_password_hash(current_user.password, current_password + current_user.salt):
                flash("Falsches aktuelles Passwort!", "danger")
                return redirect(url_for('meinprofil'))

            hashed_new_password = bcrypt_instance.generate_password_hash(new_password + current_user.salt).decode("utf-8")
            current_user.password = hashed_new_password

            db.session.commit()
            flash("Passwort erfolgreich geändert!", "success")
            return redirect(url_for('meinprofil'))
        except Exception as e:
            logging.error(f"Fehler beim Ändern des Passworts: {e}")
            flash("Ein Fehler ist aufgetreten!", "danger")
            return redirect(url_for('meinprofil'))

    # ✅ About Us Route
    @app.route('/aboutus')
    def aboutus():
        return render_template("aboutus.html")

    # ✅ CO₂ Analysis Route (Still exists for manual access)
    @app.route('/analysis/<int:tree_id>', methods=['GET'])
    @login_required
    def analysis(tree_id):
        try:
            tree = Tree.query.get_or_404(tree_id)
            tree_type = TreeType.query.get(tree.tree_type_id)
            measurement = Measurement.query.filter_by(tree_id=tree.id).order_by(Measurement.collected_at.desc()).first()

            def calculate_co2_absorption(height, diameter, type_factor):
                try:
                    return round(float(height) * float(diameter) * float(type_factor) * 0.5, 2)
                except (TypeError, ValueError):
                    return 0.0  # Fallback if values are invalid

            # Assign values with fallback options
            type_factor = tree_type.co2_compensation_rate if tree_type else 1.0
            tree_height = measurement.height if measurement else tree.tree_height
            trunk_diameter = measurement.trunk_diameter if measurement else tree.trunk_diameter
            co2_absorbed = calculate_co2_absorption(tree_height, trunk_diameter, type_factor)

            # Save CO₂ absorption value to DB
            tree.co2_compensation_rate = co2_absorbed
            db.session.commit()

            flash("Analyse abgeschlossen!", "success")
            return render_template(
                "analysis.html",
                tree=tree,
                co2_absorbed=co2_absorbed,
                measurement=measurement
            )

        except Exception as e:
            logging.error(f"Fehler bei der Analyse: {e}")
            flash("Ein Fehler ist aufgetreten!", "danger")
            return redirect(url_for('dashboard'))
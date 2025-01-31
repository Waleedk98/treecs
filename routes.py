from flask import Flask, request, jsonify, render_template, redirect, session, url_for
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from models import TrustLevel, User, UserRole, Tree, Measurement, TreeType, HealthStatus, TreePhoto, CommunityContribution, AccountType
from extensions import db, bcrypt_instance
from functions import get_gps_data_exifread, get_address_from_coordinates
from sqlalchemy.orm import joinedload
from werkzeug.utils import secure_filename
import os
from logic.register import handle_register
from logic.login import handle_login
from logic.submit_tree import handle_submit_tree
#from logic.dashboard import handle_dashboard
#from logic.index import handle_index


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
    

    
    # Submit tree data route
    @app.route("/submit_tree_data", methods=["POST"])
    @login_required
    def submit_tree_data():
        return handle_submit_tree(request)


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
# logic/register.py
from models import TrustLevel, User, UserRole, Tree, Measurement, TreeType, HealthStatus, TreePhoto, CommunityContribution, AccountType
from extensions import db, bcrypt_instance
from flask import request, render_template, redirect, session
from flask_login import login_user

def handle_register():
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

            user_role = UserRole(user_id=new_user.id, account_type_id="1")
            db.session.add(user_role)
            db.session.commit()

            # Log in the newly registered user
            login_user(new_user)
            session["user_id"] = new_user.id
            return redirect("/mainmenu")

    return render_template("register.html")
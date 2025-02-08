# logic/register.py
from models import TrustLevel, User, UserRole, Tree, Measurement, TreeType, HealthStatus, TreePhoto, CommunityContribution, AccountType
from extensions import db, bcrypt_instance, mail
from flask import request, render_template, redirect, url_for, flash
from flask_mail import Message
from utils import generate_token

def send_verification_email(user):
    token = generate_token(user.email)
    verify_url = url_for('verify_email', token=token, _external=True)
    
    msg = Message("Bitte bestätige deine E-Mail", sender="noreply@yourapp.com", recipients=[user.email])
    msg.body = f"Klicke auf den folgenden Link, um deine E-Mail zu bestätigen: {verify_url}"

    mail.send(msg)


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

            send_verification_email(new_user)

            flash("Registrierung erfolgreich! Bitte überprüfe deine E-Mails zur Bestätigung.", "info")
            return redirect("/login")

    return render_template("register.html")
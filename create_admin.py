import os
import getpass
from models import User, UserRole, TrustLevel
from extensions import db, bcrypt_instance
from app import create_app  
import secrets

# Sicherheitscode aus der Umgebungsvariable abrufen
SECRET_CODE = os.getenv("ADMIN_SECRET_CODE")

# Prüfen, ob die Variable existiert
if not SECRET_CODE:
    print("Fehler: Kein Sicherheitscode gesetzt! Setze die Umgebungsvariable ADMIN_SECRET_CODE.")
    exit(1)

entered_code = input("Admin-Code eingeben: ")
if entered_code != SECRET_CODE:
    print("Falscher Code! Zugriff verweigert.")
    exit(1)

app = create_app()

with app.app_context():
    uname = input("Admin-Benutzername: ")
    email = input("Admin-E-Mail: ")
    password = getpass.getpass("Admin-Passwort: ")

    if User.query.filter_by(uname=uname).first():
        print("Fehler: Benutzername existiert bereits.")
        exit(1)

    if User.query.filter_by(email=email).first():
        print("Fehler: E-Mail existiert bereits.")
        exit(1)

    trust_level = TrustLevel.query.get(1)
    if not trust_level:
        print("Fehler: TrustLevel mit ID 1 nicht gefunden.")
        exit(1)

    salt = secrets.token_hex(8)
    salted_password = password + salt
    hashed_password = bcrypt_instance.generate_password_hash(salted_password).decode("utf-8")

    admin = User(
        uname=uname,
        password=hashed_password,
        salt=salt,
        email=email,
        trust_level_id=trust_level.id,
        verfied=True
    )
    db.session.add(admin)
    db.session.commit()

    admin_role = UserRole(user_id=admin.id, account_type_id=3)
    db.session.add(admin_role)
    db.session.commit()

    print("Admin erfolgreich erstellt!")

from flask import redirect, url_for, flash
from extensions import db
from models import User
from utils import verify_token


#Verarbeitet die E-Mail-Verifizierung basierend auf einem übergebenen Token.
#    
#Args:
#   token (str): Das zu überprüfende Verifizierungstoken.
#    
#Returns:
#   flask.Response: Eine Weiterleitung zur Login-Seite mit einer entsprechenden Flash-Nachricht.

def handle_verify_email(token):
        email = verify_token(token)
        if email is None:
            flash("Ungültiger oder abgelaufener Verifizierungslink.", "danger")
            return redirect(url_for("login"))

        user = User.query.filter_by(email=email).first()
        if user:
            user.verified = True
            db.session.commit()
            flash("E-Mail erfolgreich bestätigt! Du kannst dich jetzt einloggen.", "success")
        return redirect(url_for("login"))
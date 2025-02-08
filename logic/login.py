from flask import request, render_template, redirect, session, flash
from flask_login import login_user
from extensions import bcrypt_instance
from models import User

def handle_login():
    if request.method == "POST":
        uname = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(uname=uname).first()

        if user:
            salted_password = password + user.salt
            if bcrypt_instance.check_password_hash(user.password, salted_password):
                # ✅ Prüfen, ob die E-Mail verifiziert wurde
                if not user.verified:
                    flash("Bitte bestätige zuerst deine E-Mail!", "warning")
                    return redirect("/login")
                
                login_user(user)
                session["user_id"] = user.id
                return redirect("/mainmenu")

        flash("Ungültige Anmeldedaten!", "danger")
        return redirect("/login")

    return render_template("login.html")

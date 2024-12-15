# extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# Initialisierung der Erweiterungen
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()

# Zusätzliche Konfigurationen für den Login-Manager
login_manager.login_view = 'login'
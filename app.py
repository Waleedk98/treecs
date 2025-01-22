from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from flask_migrate import Migrate
from config import DevelopmentConfig
from initData import initialize_tree_types, initialize_trust_levels
from extensions import db, mail, bcrypt_instance
from models import User
from routes import init_routes

# App Factory Pattern
def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Erweiterungen initialisieren
    db.init_app(app)
    mail.init_app(app)
    bcrypt_instance.init_app(app)

    # LoginManager initialisieren
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"  # Falls der Benutzer nicht eingeloggt ist, umgeleitet werden soll

    # Initialisiere Migrate für Datenbankmigrationen
    migrate = Migrate(app, db)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    init_routes(app)

    # Nur in der Entwicklung verwenden
    with app.app_context():
        db.create_all()  # Sollte in der Produktion durch Migrationen ersetzt werden

    with app.app_context():
            initialize_tree_types()
            
    with app.app_context():
            initialize_trust_levels()
            
    
    return app



if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)  # Debug nur in der Entwicklungsumgebung

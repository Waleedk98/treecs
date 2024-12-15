from flask import Flask
from extensions import db, bcrypt, login_manager
from routes import init_routes
from config import DevelopmentConfig
from models import User

# App initialisieren
app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

# User-Loader registrieren
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Erweiterungen initialisieren
db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)

# Routen initialisieren
init_routes(app)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)

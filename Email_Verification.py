from flask import Flask, request, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from models import db, User # Import Datenbank

# Flask-App Factory Pattern
def create_app(config_name):
    app = Flask(__name__)

    # Konfiguration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db' # Ersetzen mit DB
    app.config['MAIL_SERVER'] = 'smtp.example.com'               # Ersetzen mit smtp Server 
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USERNAME'] = 'your-email@example.com'       # Echte Email
    app.config['MAIL_PASSWORD'] = 'your-password'
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.secret_key = 'your-secret-key'

    db.init_app(app)
    mail.init_app(app)

    with app.app_context():
        db.create_all()

    return app

# Initialisiere Extensions
mail = Mail()
serializer = URLSafeTimedSerializer('your-secret-key')

# Blueprint-Funktionen
def register_routes(app):
    @app.route('/register', methods=['POST']) # Anpassen
    def register():
        data = request.json
        email = data.get('email')
        
        if User.query.filter_by(email=email).first():
            return jsonify({'message': 'Email already registered.'}), 400

        new_user = User(email=email)
        db.session.add(new_user)
        db.session.commit()

        token = serializer.dumps(email, salt='email-confirm')  # Stellen Sie sicher, dass der Salt-Wert sicher und für Ihre Anwendung geeignet ist.
        link = url_for('verify_email', token=token, _external=True)

        msg = Message('Confirm your Email', sender='your-email@example.com', recipients=[email])
        msg.body = f'Please confirm your email by clicking on the link: {link}'
        mail.send(msg)

        return jsonify({'message': 'Verification email sent!'}), 200

    @app.route('/verify/<token>', methods=['GET']) # Anpassen
    def verify_email(token):
        try:
            email = serializer.loads(token, salt='email-confirm', max_age=3600)
            user = User.query.filter_by(email=email).first()
            if not user:
                return jsonify({'message': 'User not found!'}), 404
            user.verified = True
            db.session.commit()
            return jsonify({'message': 'Email verified!'}), 200
        except SignatureExpired:
            return jsonify({'message': 'The token has expired!'}), 400

# Integrieren in ein größeres Projekt
app = create_app('default')
register_routes(app)

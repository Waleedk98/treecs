# extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flask_bcrypt import Bcrypt

# Initialisiere Extensions
db = SQLAlchemy()
mail = Mail()
bcrypt_instance = Bcrypt()
serializer = URLSafeTimedSerializer('your-secret-key')

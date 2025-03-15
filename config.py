 # config.py
class Config:
    SECRET_KEY = 'your-secret-key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Photo Upload
    UPLOAD_FOLDER = 'static/uploads/tree_photos'  # Ordner für Bilder
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    # Flask-Mail Konfiguration
    MAIL_SERVER = "smtp.hs-fulda.de"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = "fdlt3859@hs-fulda.de"
    MAIL_PASSWORD = "xyz"
    MAIL_DEFAULT_SENDER = "noreply@deineapp.com"
    MAIL_MAX_EMAILS = 10  
    MAIL_ASCII_ATTACHMENTS = False

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:19x28x37x@127.0.0.1:5433/Tree'
    DEBUG = True
    

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:19x28x37x@127.0.0.1:5433/Tree'
    DEBUG = False
    

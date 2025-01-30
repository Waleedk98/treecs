 # config.py
class Config:
    SECRET_KEY = 'your-secret-key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Photo Upload
    UPLOAD_FOLDER = 'uploads/tree_photos'  # Ordner für Bilder
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:19x28x37x@127.0.0.1:5433/Tree'
    DEBUG = True
    

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:19x28x37x@127.0.0.1:5433/Tree'
    DEBUG = False
    

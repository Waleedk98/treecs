from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask import current_app


#Erstellt ein zeitlich begrenztes Token für eine gegebene E-Mail-Adresse.
#    
#Args:
#   email (str): Die E-Mail-Adresse, die in das Token eingebettet wird.
#    
#Returns:
#   str: Das generierte Token als Zeichenkette.
def generate_token(email):
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return s.dumps(email, salt="email-confirmation-salt")




#Überprüft die Gültigkeit eines Tokens und extrahiert die E-Mail-Adresse.
#    
#Args:
#   token (str): Das zu überprüfende Token.
#   expiration (int, optional): Maximale Gültigkeitsdauer in Sekunden. Standard: 3600 Sekunden (1 Stunde).
#    
#Returns:
#   str | None: Die E-Mail-Adresse, falls das Token gültig ist, sonst None.
def verify_token(token, expiration=3600):
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        email = s.loads(token, salt="email-confirmation-salt", max_age=expiration)
        return email
    except (BadSignature, SignatureExpired):
        return None

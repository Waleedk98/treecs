from flask import request, render_template, redirect, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import os
from functions import get_gps_data_exifread, get_address_from_coordinates
from extensions import db, bcrypt_instance
from models import TrustLevel, User, UserRole, Tree, Measurement, TreeType, HealthStatus, TreePhoto, CommunityContribution, AccountType
from flask import current_app

# Function to check allowed file types
def allowed_file(filename):
        allowed_extensions = current_app.config['ALLOWED_EXTENSIONS']
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def handle_submit_tree(request):
        tree_type = request.form.get("tree_type")
        tree_height = request.form.get("tree_height")
        inclination = request.form.get("inclination")
        trunk_diameter = request.form.get("trunk_diameter")
        address = request.form.get("address")

        # Validierung der erforderlichen Felder ohne Geodaten
        required_fields = [tree_type, tree_height, inclination, trunk_diameter]
        if not all(required_fields):
            return jsonify({"error": "Fehlende Daten. Bitte alle Felder ausfüllen."}), 400

        # Überprüfung, ob Bilder hochgeladen wurden
        if "tree_photos" not in request.files:
            return jsonify({"error": "Keine Bilder hochgeladen"}), 400

        files = request.files.getlist("tree_photos")
        if not files or len(files) == 0:
            return jsonify({"error": "Keine Dateien gefunden."}), 400

        # GPS-Daten aus dem ersten Bild extrahieren
        first_file = files[0]
        gps_coords = get_gps_data_exifread(first_file)  # Funktion zum Abrufen von GPS-Daten
        if not gps_coords:
            return jsonify({"error": "Das erste Bild enthält keine GPS-Daten. Stellen Sie sicher, dass das Bild Geotags enthält."}), 400

        # Extrahierte GPS-Daten verwenden
        extracted_latitude, extracted_longitude = gps_coords
        
        # Debug-Ausgabe der GPS-Daten
        #print(f"Extrahierte GPS-Daten: Latitude={extracted_latitude}, Longitude={extracted_longitude}")

        address = get_address_from_coordinates(extracted_latitude, extracted_longitude)
        try:
            tree_type_obj = TreeType.query.filter_by(name=tree_type).first()

            newTree = Tree(
                user_id=current_user.id,
                tree_type_id=tree_type_obj.id,
                tree_height=float(tree_height),
                inclination=float(inclination),
                trunk_diameter=float(trunk_diameter),
                latitude=float(extracted_latitude),
                longitude=float(extracted_longitude),
                address=address or "Unbekannter Standort"
            )
            db.session.add(newTree)
            db.session.commit()

            newMeasurement = Measurement(
                user_id=current_user.id,
                tree_id=newTree.id,
                suspected_tree_type=tree_type,
                height=float(tree_height),
                inclination=float(inclination),
                trunk_diameter=float(trunk_diameter),
            )
            db.session.add(newMeasurement)
            db.session.commit()

            # Speicherpfad für Bilder im 'static/uploads/tree_photos/'
            upload_folder = current_app.config['UPLOAD_FOLDER']  # z.B. 'static/uploads/tree_photos/'

            # Stelle sicher, dass der Ordner existiert
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            # Verarbeite die Bilder
            for file in files:
                if file and allowed_file(file.filename):
                 # Sicherstellen, dass der Dateiname sicher ist
                    filename = secure_filename(file.filename)

                    # Speichern der Datei im richtigen Ordner
                    filepath = os.path.join(upload_folder, filename)
                    file.save(filepath)

                    newPhoto = TreePhoto(
                        tree_id=newTree.id,
                        measurement_id=newMeasurement.id,
                        user_id=current_user.id,
                        photo_path=filepath,
                        description=f"Foto für Baum {tree_type}"
                    )
                    db.session.add(newPhoto)
                    db.session.commit()

            newContribution = CommunityContribution(
                tree_id=newTree.id,
                user_id=current_user.id,
                contribution_type="Added Tree",
                description=""
            )
            db.session.add(newContribution)
            db.session.commit()

            return redirect("/dashboard")

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Es ist ein Fehler aufgetreten: {str(e)}"}), 500
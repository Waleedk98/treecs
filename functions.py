import exifread
import requests


import requests

import requests

def get_address_from_coordinates(lat, lng):
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lng}&format=json&addressdetails=1"

    headers = {
        'User-Agent': 'TreeDataApp/1.0 (waleed.khaliq66@gmail.com)'
    }

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            if data and 'address' in data:
                address_data = data['address']

                # Adressdaten abrufen
                house_number = address_data.get('house_number', '')
                road = address_data.get('road', '')
                suburb = address_data.get('suburb', '')
                city = address_data.get('city', '') or address_data.get('town', '') or address_data.get('village', '')
                country = address_data.get('country', '')

                # Liste mit Adressbestandteilen, leere Werte herausfiltern
                address_parts = [road, house_number, suburb, city, country]
                address = ", ".join(filter(None, address_parts))  # Entferne leere Einträge

                return address if address else 'Unbekannter Standort'
            else:
                return 'Unbekannter Standort'
        else:
            print(f"Fehler: Ungültiger Statuscode {response.status_code}")
            return 'Unbekannter Standort'

    except requests.exceptions.RequestException as e:
        print(f"Fehler bei der Adresseermittlung: {e}")
        return 'Unbekannter Standort'




def get_gps_data_exifread(file):
    """
    Extrahiert GPS-Daten aus einem Bild mithilfe von exifread.
    """
    try:
        file.seek(0)  # Stelle sicher, dass wir am Anfang der Datei lesen
        tags = exifread.process_file(file, details=False)

        # GPS-Tags extrahieren
        gps_latitude = tags.get("GPS GPSLatitude")
        gps_latitude_ref = tags.get("GPS GPSLatitudeRef")
        gps_longitude = tags.get("GPS GPSLongitude")
        gps_longitude_ref = tags.get("GPS GPSLongitudeRef")

        if not gps_latitude or not gps_longitude:
            return None

        def convert_to_degrees(value):
            d, m, s = [float(v.num) / float(v.den) for v in value.values]
            return d + (m / 60.0) + (s / 3600.0)

        lat = convert_to_degrees(gps_latitude)
        if gps_latitude_ref.values[0] != "N":
            lat = -lat
            
            
        lon = convert_to_degrees(gps_longitude)
        if gps_longitude_ref.values[0] != "E":
            lon = -lon
            
        return lat, lon
    
    except Exception as e:
        print(f"Fehler beim Extrahieren der EXIF-Daten: {e}")
        return None
   
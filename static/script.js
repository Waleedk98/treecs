// Funktion zum Abrufen der Adresse basierend auf den Geokoordinaten
function getAddressFromCoordinates(latitude, longitude) {
    const url = `https://nominatim.openstreetmap.org/reverse?lat=${latitude}&lon=${longitude}&format=json`;

    // Rückgabe eines Promises, das die Adresse liefert
    return fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data && data.display_name) {
                return data.display_name; // Rückgabe der Adresse
            }
            return "Unbekannter Standort"; // Fallback
        })
        .catch(error => {
            console.error("Fehler beim Abrufen der Adresse:", error);
            return "Standort konnte nicht ermittelt werden."; // Fallback
        });
}

// Funktion zum Absenden der Formulardaten und Berechnen der Baumhöhe
document.getElementById("sensorForm").addEventListener("submit", async function(event) {
    event.preventDefault();

    // Eingabewerte aus dem Formular abrufen
    const latitude = parseFloat(document.getElementById("latitude").value);
    const longitude = parseFloat(document.getElementById("longitude").value);
    const beta = parseFloat(document.getElementById("beta").value);
    const distance = parseFloat(document.getElementById("distance").value);

    console.log("Daten:", latitude, longitude, beta, distance);

    // Standort-Adresse abrufen
    const location = await getAddressFromCoordinates(latitude, longitude);
    document.getElementById("location").innerText = "Du befindest dich in: " + location;

    // Daten an den Flask-Server senden
    fetch('/submit_sensor_data', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            latitude: latitude,
            longitude: longitude,
            beta: beta,
            distance: distance,
            location: location // Übergabe der korrekten Adresse
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log("Serverantwort:", data);
        document.getElementById("result").innerText = 
            "Baumhöhe: " + data.height + " Meter";
    })
    .catch(err => console.error("Fehler beim Senden der Daten:", err));
});

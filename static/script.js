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

// Funktion zum Absenden der Formulardaten und Speichern von Baumdaten
document.getElementById("treeDataForm").addEventListener("submit", async function(event) {
    event.preventDefault();

    // Eingabewerte aus dem Formular abrufen
    const treeType = document.getElementById("treeType").value;
    const treeHeight = parseInt(document.getElementById("treeHeight").value);
    const inclination = parseInt(document.getElementById("inclination").value);
    const trunkDiameter = parseInt(document.getElementById("trunkDiameter").value);
    const latitude = parseFloat(document.getElementById("latitude").value);
    const longitude = parseFloat(document.getElementById("longitude").value);

    console.log("Daten:", { treeType, treeHeight, inclination, trunkDiameter, latitude, longitude });

    // Standort-Adresse abrufen
    const address = await getAddressFromCoordinates(latitude, longitude);
    document.getElementById("location").innerText = "Standort: " + address;

    // Daten an den Flask-Server senden
    fetch('/submit_tree_data', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            tree_type: treeType,
            tree_height: treeHeight,
            inclination: inclination,
            trunk_diameter: trunkDiameter,
            latitude: latitude,
            longitude: longitude,
            address: address // Übergabe der korrekten Adresse
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log("Serverantwort:", data);
        document.getElementById("result").innerText =
            "Baumdaten erfolgreich gespeichert.";
    })
    .catch(err => console.error("Fehler beim Senden der Daten:", err));
});

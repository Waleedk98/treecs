from models import TreeType, TrustLevel, db  # Importiere TreeType und db aus deinen Modellen

def initialize_tree_types():
    """
    Initialisiert die Baumtypen in der Datenbank, wenn sie noch nicht existieren.
    """
    # Überprüfen, ob die Tabelle bereits Daten enthält
    if TreeType.query.first():  # Wenn es bereits Daten gibt, überspringen
        print("Tree types already initialized.")
        return

    # Liste der Baumtypen, die hinzugefügt werden sollen
    tree_types = [
        {"name": "Eiche", "true_type": "Eiche", "co2_compensation_rate": 1.2},
        {"name": "Kiefer", "true_type": "Kiefer", "co2_compensation_rate": 1.0},
        {"name": "Buche", "true_type": "Buche", "co2_compensation_rate": 1.3},
        {"name": "Ahorn", "true_type": "Ahorn", "co2_compensation_rate": 1.1},
        {"name": "Birke", "true_type": "Birke", "co2_compensation_rate": 0.8},
        {"name": "Fichte", "true_type": "Fichte", "co2_compensation_rate": 1.0},
        {"name": "Linde", "true_type": "Linde", "co2_compensation_rate": 0.9},
        {"name": "Esche", "true_type": "Esche", "co2_compensation_rate": 1.1},
        {"name": "Tanne", "true_type": "Tanne", "co2_compensation_rate": 1.2},
        {"name": "Douglasie", "true_type": "Douglasie", "co2_compensation_rate": 1.4},
        {"name": "Pappel", "true_type": "Pappel", "co2_compensation_rate": 0.7},
        {"name": "Ulme", "true_type": "Ulme", "co2_compensation_rate": 0.9},
        {"name": "Zeder", "true_type": "Zeder", "co2_compensation_rate": 1.5},
        {"name": "Walnussbaum", "true_type": "Walnussbaum", "co2_compensation_rate": 1.3},
        {"name": "Kastanie", "true_type": "Kastanie", "co2_compensation_rate": 1.1},
        {"name": "Mango", "true_type": "Mango", "co2_compensation_rate": 1.4},
        {"name": "Teak", "true_type": "Teak", "co2_compensation_rate": 1.6},
        {"name": "Mahagoni", "true_type": "Mahagoni", "co2_compensation_rate": 1.8},
        {"name": "Palme", "true_type": "Palme", "co2_compensation_rate": 0.6},
        {"name": "Olivenbaum", "true_type": "Olivenbaum", "co2_compensation_rate": 0.8},
        {"name": "Zypresse", "true_type": "Zypresse", "co2_compensation_rate": 1.2},
        {"name": "Eukalyptus", "true_type": "Eukalyptus", "co2_compensation_rate": 1.5},
        {"name": "Akazie", "true_type": "Akazie", "co2_compensation_rate": 1.0},
        {"name": "Roter Ahorn", "true_type": "Roter Ahorn", "co2_compensation_rate": 1.3},
        {"name": "Balsambaum", "true_type": "Balsambaum", "co2_compensation_rate": 1.2},
        {"name": "Kirschbaum", "true_type": "Kirschbaum", "co2_compensation_rate": 0.9},
        {"name": "Apfelbaum", "true_type": "Apfelbaum", "co2_compensation_rate": 0.8},
        {"name": "Pfefferbaum", "true_type": "Pfefferbaum", "co2_compensation_rate": 1.0},
        {"name": "Zitronenbaum", "true_type": "Zitronenbaum", "co2_compensation_rate": 0.7},
        {"name": "Kokospalme", "true_type": "Kokospalme", "co2_compensation_rate": 0.9},
        {"name": "Bambus", "true_type": "Bambus", "co2_compensation_rate": 2.0},  # Schnellwachsender Baum
    ]

    # Daten in die Datenbank einfügen
    print("Inserting tree types...")
    for tree in tree_types:
        db.session.add(TreeType(**tree))
    db.session.commit()
    print("Tree types initialized successfully.")

def initialize_trust_levels():
    """
    Initialisiert die TrustLevel in der Datenbank, wenn sie noch nicht existieren.
    """
    # Überprüfen, ob die Tabelle bereits Daten enthält
    if TrustLevel.query.first():  # Wenn es bereits TrustLevels gibt, überspringen
        print("Trust levels already initialized.")
        return

    # Liste der TrustLevel, die hinzugefügt werden sollen
    trust_levels = [
        {"id": "1" ,"rank": "Basic", "description": "Standard Trust Level"},
        {"id": "2" ,"rank": "Bronze", "description": "Low level of trust, new users"},
        {"id": "3" ,"rank": "Silver", "description": "Moderate level of trust"},
        {"id": "4" ,"rank": "Gold", "description": "High level of trust, established users"},
        {"id": "5" ,"rank": "Platinum", "description": "Top trust level, for most trusted users"}
    ]

    # Daten in die Datenbank einfügen
    print("Inserting trust levels...")
    
    for trust_level in trust_levels:
        db.session.add(TrustLevel(**trust_level))  # Erstelle und füge TrustLevel hinzu
    db.session.commit()  # Bestätige die Transaktion
    print("Trust levels initialized successfully.")

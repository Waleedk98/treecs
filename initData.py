from models import TreeType, TrustLevel, AccountType, db  # Importiere TreeType und db aus deinen Modellen

def initialize_tree_types():
    """
    Initialisiert die Baumtypen in der Datenbank, wenn sie noch nicht existieren.
    """
    # Überprüfen, ob die Tabelle bereits Daten enthält
    if TreeType.query.first():  # Wenn es bereits Daten gibt, überspringen
        print("Tree types already initialized.")
        return

    tree_types = [
    {"name": "Eiche", "true_type": "Quercus robur"},
    {"name": "Kiefer", "true_type": "Pinus sylvestris"},
    {"name": "Buche", "true_type": "Fagus sylvatica"},
    {"name": "Ahorn", "true_type": "Acer pseudoplatanus"},
    {"name": "Birke", "true_type": "Betula pendula"},
    {"name": "Fichte", "true_type": "Picea abies"},
    {"name": "Linde", "true_type": "Tilia cordata"},
    {"name": "Esche", "true_type": "Fraxinus excelsior"},
    {"name": "Tanne", "true_type": "Abies alba"},
    {"name": "Douglasie", "true_type": "Pseudotsuga menziesii"},
    {"name": "Pappel", "true_type": "Populus tremula"},
    {"name": "Ulme", "true_type": "Ulmus glabra"},
    {"name": "Zeder", "true_type": "Cedrus atlantica"},
    {"name": "Walnussbaum", "true_type": "Juglans regia"},
    {"name": "Kastanie", "true_type": "Castanea sativa"},
    {"name": "Mango", "true_type": "Mangifera indica"},
    {"name": "Teak", "true_type": "Tectona grandis"},
    {"name": "Mahagoni", "true_type": "Swietenia mahagoni"},
    {"name": "Palme", "true_type": "Arecaceae"},
    {"name": "Olivenbaum", "true_type": "Olea europaea"},
    {"name": "Zypresse", "true_type": "Cupressus sempervirens"},
    {"name": "Eukalyptus", "true_type": "Eucalyptus globulus"},
    {"name": "Akazie", "true_type": "Acacia spp."},
    {"name": "Roter Ahorn", "true_type": "Acer rubrum"},
    {"name": "Balsambaum", "true_type": "Abies balsamea"},
    {"name": "Kirschbaum", "true_type": "Prunus avium"},
    {"name": "Apfelbaum", "true_type": "Malus domestica"},
    {"name": "Pfefferbaum", "true_type": "Piper nigrum"},
    {"name": "Zitronenbaum", "true_type": "Citrus limon"},
    {"name": "Kokospalme", "true_type": "Cocos nucifera"},
    {"name": "Bambus", "true_type": "Bambusoideae"}, 
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

def initialize_acc_type():
    # Überprüfen, ob die Tabelle bereits Daten enthält
    if AccountType.query.first():  # Wenn es bereits TrustLevels gibt, überspringen
        print("Accounttypes already initialized.")
        return
    
    account_types = [
        {"id":"1", "type_name":"User", "description": "Standard Account Type"},
        {"id":"2", "type_name":"Expert", "description": "Expert Account Type"},
        {"id":"3", "type_name":"Admin", "description": "Admin Account Type"},
    ]
    
     # Daten in die Datenbank einfügen
    print("Inserting accounttypes...")
    
    for account_types in account_types:
        db.session.add(AccountType(**account_types))  # Erstelle und füge Accounttypes hinzu
    db.session.commit()  # Bestätige die Transaktion
    print("Accounttypes initialized successfully.")
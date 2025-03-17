from sqlalchemy.orm import joinedload
from math import log, exp
from extensions import db
from models import Tree,TreeBiomass,TreeType

def calculate_biomass(tree_id):
    # Baumdaten abrufen
    tree = db.session.query(Tree).options(joinedload(Tree.tree_type)).filter_by(id=tree_id).first()
    if not tree:
        return None  # Baum existiert nicht
    
    species_name = tree.tree_type.true_type  # Baumart aus tree_types
    dbh = tree.trunk_diameter  # Stammdurchmesser in cm
    height = tree.tree_height  # Höhe in m

    # Biomasse-Formel für die Spezies abrufen
    biomass_formula = db.session.query(TreeBiomass).filter_by(scientific_species=species_name).first()
    if not biomass_formula:
        return None  # Keine Formel für die Baumart gefunden

    # Werte aus der Formel-Tabelle extrahieren
    A = biomass_formula.A or 0
    B = biomass_formula.B or 0
    C = biomass_formula.C or 0
    D = biomass_formula.D or 0
    E = biomass_formula.E or 0
    F = biomass_formula.F or 0
    G = biomass_formula.G or 0
    equation_form = biomass_formula.equation_form

    # Die passende Berechnungsformel anwenden
    
    if equation_form == "Y=A+Bx+Cx^2+Dx^3+Ex^4+Fx^5" & species_name == "Picea abies" | equation_form == "Y=A+Bx+Cx^2+Dx^3+Ex^4+Fx^5" & species_name == "Pinus sylvestris":
        biomass = biomass = A + B * dbh + C * (dbh ** 2) + D * (dbh ** 3) + E * (dbh ** 4) + F * (dbh ** 5)
        
    else:
        return None  # Falls eine unbekannte Formel gespeichert wurde

    return biomass

def calculate_carbon_storage(tree_id):
    # Biomasse berechnen
    biomass = calculate_biomass(tree_id)
    if biomass is None:
        return None  # Falls keine Biomasse berechnet werden kann
    
    # Baumdaten abrufen
    tree = db.session.query(Tree).filter_by(id=tree_id).first()
    if not tree:
        return None  # Falls der Baum nicht existiert

    # Kohlenstoffspeicherung berechnen
    carbon_storage = biomass * 0.5  

    # Begrenzung für große Bäume (max. 40 kg C pro cm d.b.h. Wachstum ab 7.500 kg C)
    if carbon_storage > 7500:
        max_sequestration = 40 * tree.trunk_diameter
        carbon_storage = min(carbon_storage, 7500 + max_sequestration)

    return carbon_storage

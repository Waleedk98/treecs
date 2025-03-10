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
    if equation_form == "Y = A * x^B":
        biomass = A * (dbh ** B)
    elif equation_form == "Y = A + B * x + C * x^2":
        biomass = A + B * dbh + C * (dbh ** 2)
    elif equation_form == "Y = e^(A + B * ln(x) + (C/2))":
        biomass = exp(A + B * log(dbh) + (C / 2))
    elif equation_form == "Y = A * x^B + C * x^D":
        biomass = (A * (dbh ** B)) + (C * (dbh ** D))
    else:
        return None  # Falls eine unbekannte Formel gespeichert wurde

    return biomass

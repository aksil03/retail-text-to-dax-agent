# THÈME : PRODUITS (Products)


CA_ET_BENEFICE_PAR_CATEGORIE = """
EVALUATE
SUMMARIZECOLUMNS(
    'Products'[Category],
    "Chiffre d'Affaires", [Chiffre d'Affaires],
    "Bénéfice", [Bénéfice]
)
"""

SYNTHESE_PAR_MARQUE = """
EVALUATE
SUMMARIZECOLUMNS(
    'Products'[Brand],
    "Chiffre d'Affaires", [Chiffre d'Affaires],
    "Quantité Totale", [Quantité totale],
    "Total Produits", [Total Produits]
)
"""

PERFORMANCE_PAR_SOUS_CATEGORIE = """
EVALUATE
SUMMARIZECOLUMNS(
    'Products'[Subcategory],
    "Panier Moyen", [Panier Moyen],
    "Chiffre d'Affaires", [Chiffre d'Affaires]
)
"""

# THÈME : CLIENTS (Customers)


CLIENTS_ET_CA_PAR_PAYS = """
EVALUATE
SUMMARIZECOLUMNS(
    'Customers'[Country],
    "Total Clients", [Total Clients],
    "Chiffre d'Affaires", [Chiffre d'Affaires]
)
"""

CLIENTS_PAR_GENRE = """
EVALUATE
SUMMARIZECOLUMNS(
    'Customers'[Gender],
    "Total Clients", [Total Clients],
    "Panier Moyen", [Panier Moyen]
)
"""

ANALYSE_CLIENTS_VILLE = """
EVALUATE
SUMMARIZECOLUMNS(
    'Customers'[City],
    "Chiffre d'Affaires", [Chiffre d'Affaires],
    "Bénéfice", [Bénéfice]
)
"""

# THÈME : MAGASINS (Stores)


CA_PAR_PAYS_MAGASIN = """
EVALUATE
SUMMARIZECOLUMNS(
    'Stores'[Country],
    "Chiffre d'Affaires", [Chiffre d'Affaires],
    "Coût Total", [Coût Total]
)
"""

PERFORMANCE_PAR_SURFACE_MAGASIN = """
EVALUATE
SUMMARIZECOLUMNS(
    'Stores'[Square Meters],
    "Chiffre d'Affaires", [Chiffre d'Affaires]
)
"""

# THÈME : SYNTHÈSE GLOBALE DES VENTES (Sales)


VUE_ENSEMBLE_KPIS = """
EVALUATE
ROW(
    "Chiffre d'Affaires", [Chiffre d'Affaires],
    "Bénéfice", [Bénéfice],
    "Bénéfice Moyen", [Bénéfice Moyen],
    "Panier Moyen", [Panier Moyen],
    "Quantité Totale", [Quantité totale],
    "Temps Moyen de Livraison", [Temps moyen...]
)
"""
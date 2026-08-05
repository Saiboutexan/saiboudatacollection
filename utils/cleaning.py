"""Nettoyage des données brutes issues des scrapers Selenium."""

import re

import pandas as pd

# ---------------------------------------------------------------- livres

NOTES_TEXTE = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def _vers_float(valeur) -> float:
    """'£51.77' -> 51.77 ; '' -> NaN."""
    if valeur is None:
        return float("nan")
    chiffres = re.sub(r"[^\d.]", "", str(valeur))
    try:
        return float(chiffres)
    except ValueError:
        return float("nan")


def _vers_int(valeur) -> float:
    """'136 000 km' -> 136000 ; 'CFA 2 800 000' -> 2800000."""
    chiffres = re.sub(r"[^\d]", "", str(valeur or ""))
    return int(chiffres) if chiffres else float("nan")


def nettoyer_livres(df: pd.DataFrame) -> pd.DataFrame:
    """Type les colonnes, normalise la disponibilité et la note."""
    if df.empty:
        return df.copy()

    propre = df.copy()

    propre["titre"] = propre["titre"].astype(str).str.strip()
    propre["prix"] = propre["prix"].apply(_vers_float)
    propre["tax"] = propre["tax"].apply(_vers_float)

    # 'In stock' / 'In stock (22 available)' -> booléen + quantité
    dispo = propre["disponibilite"].astype(str).str.strip()
    propre["en_stock"] = dispo.str.lower().str.contains("in stock")
    propre["disponibilite"] = propre["en_stock"].map(
        {True: "En stock", False: "Rupture de stock"})

    propre["note"] = propre["note"].map(NOTES_TEXTE).astype("Int64")
    propre["nb_reviews"] = propre["nb_reviews"].apply(_vers_int).astype("Int64")
    propre["nb_produits_page"] = (
        propre["nb_produits_page"].apply(_vers_int).astype("Int64"))

    propre["description"] = (
        propre["description"].astype(str)
        .str.replace(r"\s+", " ", regex=True).str.strip()
        .replace({"": None, "nan": None}))
    propre["type_produit"] = propre["type_produit"].astype(str).str.strip()

    propre = propre.drop_duplicates(subset=["titre", "url"], keep="first")
    return propre.reset_index(drop=True)


# ---------------------------------------------------------------- véhicules

# Marques en deux mots : sans cette liste, « Land Rover Range Rover Sport »
# donnerait marque='Land' et modèle='Rover Range Rover Sport'.
MARQUES_COMPOSEES = [
    "Land Rover", "Alfa Romeo", "Aston Martin", "Great Wall",
    "Mercedes Benz", "Mercedes-Benz", "Range Rover", "Rolls Royce",
]

BOITES = {
    "manuelle": "Manuelle",
    "automatique": "Automatique",
    "semi-automatique": "Semi-automatique",
}


def _separer_titre(titre: str):
    """'2011 Citroen C3' -> (2011, 'Citroen', 'C3')."""
    titre = re.sub(r"\s+", " ", str(titre or "")).strip()
    if not titre:
        return (pd.NA, None, None)

    annee = pd.NA
    debut = re.match(r"^(19|20)\d{2}\b", titre)
    if debut:
        annee = int(debut.group(0))
        titre = titre[debut.end():].strip()

    for marque in MARQUES_COMPOSEES:
        if titre.lower().startswith(marque.lower()):
            modele = titre[len(marque):].strip()
            return (annee, marque, modele or None)

    morceaux = titre.split(" ", 1)
    marque = morceaux[0] if morceaux else None
    modele = morceaux[1].strip() if len(morceaux) > 1 else None
    return (annee, marque, modele)


def _extraire_carburant(texte: str):
    """'N/A (Diesel)' -> 'Diesel'."""
    trouve = re.search(r"\(([^)]+)\)", str(texte or ""))
    return trouve.group(1).strip() if trouve else None


def nettoyer_vehicules(df: pd.DataFrame) -> pd.DataFrame:
    """Éclate le titre en marque/modèle/année et type les colonnes."""
    if df.empty:
        return df.copy()

    propre = df.copy()

    separe = propre["titre_annonce"].apply(_separer_titre)
    propre["annee"] = [s[0] for s in separe]
    propre["marque"] = [s[1] for s in separe]
    propre["modele"] = [s[2] for s in separe]
    propre["annee"] = pd.to_numeric(propre["annee"], errors="coerce").astype("Int64")

    propre["prix"] = propre["prix"].apply(_vers_int).astype("Int64")
    propre["kilometrage"] = propre["kilometrage"].apply(_vers_int).astype("Int64")

    propre["boite_vitesses"] = (
        propre["boite_vitesses"].astype(str).str.strip().str.lower()
        .map(BOITES).fillna("Non renseignée"))
    propre["carburant"] = propre["carburant"].apply(_extraire_carburant)
    propre["region"] = (
        propre["region"].astype(str).str.strip().replace({"": None, "nan": None}))

    # Une année de 1980 ou un prix à 0 sont des saisies aberrantes du site.
    annee_valide = propre["annee"].between(1950, 2030) | propre["annee"].isna()
    propre = propre[annee_valide]
    propre.loc[propre["prix"] == 0, "prix"] = pd.NA

    propre = propre.drop_duplicates(
        subset=["titre_annonce", "prix", "kilometrage"], keep="first")

    colonnes = ["marque", "modele", "annee", "prix", "kilometrage",
                "boite_vitesses", "region", "carburant", "date_publication",
                "titre_annonce", "page"]
    return propre[colonnes].reset_index(drop=True)

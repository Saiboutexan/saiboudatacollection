"""Scraping de books.toscrape.com avec Selenium uniquement.

Variables extraites (cf. énoncé) :
    V1 titre · V2 prix · V3 disponibilité · V4 nombre de produits sur la page
    V5 note · V6 nombre de reviews · V7 description · V8 type de produit
    V9 tax

Les variables V6 à V9 ne figurent pas sur la page de catalogue : il faut
ouvrir la fiche de chaque livre. C'est le rôle du second passage
(`_completer_fiches`).
"""

import time

import pandas as pd
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .driver import attribut_ou_defaut, creer_driver, texte_ou_defaut

URL_CATALOGUE = "https://books.toscrape.com/catalogue/page-{}.html"

# Le nombre d'étoiles est porté par une classe CSS ("star-rating Three").
NOTES = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

COLONNES = [
    "titre", "prix", "disponibilite", "nb_produits_page", "note",
    "nb_reviews", "description", "type_produit", "tax", "url",
]


def _note_depuis_classe(classe_css: str) -> str:
    """'star-rating Three' -> 'Three'."""
    for mot in classe_css.split():
        if mot in NOTES:
            return mot
    return ""


def _scraper_catalogue(driver, n_pages, journal=None):
    """Premier passage : parcourt les pages de listing (V1 à V5)."""
    livres = []

    for page in range(1, n_pages + 1):
        try:
            driver.get(URL_CATALOGUE.format(page))
        except TimeoutException:
            pass
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "article.product_pod"))
            )
        except Exception:
            break  # page inexistante : on s'arrête là

        fiches = driver.find_elements(By.CSS_SELECTOR, "article.product_pod")
        nb_produits_page = len(fiches)
        if nb_produits_page == 0:
            break

        for fiche in fiches:
            lien = attribut_ou_defaut(fiche, By.CSS_SELECTOR, "h3 a", "href")
            livres.append({
                "titre": attribut_ou_defaut(fiche, By.CSS_SELECTOR, "h3 a", "title"),
                "prix": texte_ou_defaut(fiche, By.CSS_SELECTOR, "p.price_color"),
                "disponibilite": texte_ou_defaut(
                    fiche, By.CSS_SELECTOR, "p.instock.availability"),
                "nb_produits_page": nb_produits_page,
                "note": _note_depuis_classe(
                    attribut_ou_defaut(fiche, By.CSS_SELECTOR,
                                       "p.star-rating", "class")),
                "url": lien,
            })

        if journal:
            journal(page, n_pages, len(livres))

    return livres


def _completer_fiches(driver, livres, journal=None):
    """Second passage : ouvre chaque fiche produit (V6 à V9)."""
    total = len(livres)

    for i, livre in enumerate(livres, start=1):
        if not livre["url"]:
            continue
        try:
            driver.get(livre["url"])
        except TimeoutException:
            pass
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "table.table-striped"))
            )
        except Exception:
            continue

        # Le tableau produit : UPC, Product Type, Prix HT/TTC, Tax,
        # Availability, Number of reviews.
        infos = {}
        for ligne in driver.find_elements(By.CSS_SELECTOR, "table.table-striped tr"):
            cle = texte_ou_defaut(ligne, By.TAG_NAME, "th")
            valeur = texte_ou_defaut(ligne, By.TAG_NAME, "td")
            if cle:
                infos[cle] = valeur

        livre["nb_reviews"] = infos.get("Number of reviews", "")
        livre["tax"] = infos.get("Tax", "")
        livre["type_produit"] = texte_ou_defaut(
            driver, By.CSS_SELECTOR, "ul.breadcrumb li:nth-child(3) a")
        livre["description"] = texte_ou_defaut(
            driver, By.XPATH,
            "//div[@id='product_description']/following-sibling::p[1]")

        if journal and i % 5 == 0:
            journal(i, total, i)

    return livres


def scraper_livres(n_pages=1, avec_fiches=True, journal=None) -> pd.DataFrame:
    """Scrape `n_pages` pages du catalogue et renvoie un DataFrame brut.

    `journal` est une fonction (courant, total, nb_lignes) appelée pour
    alimenter la barre de progression Streamlit.
    """
    driver = creer_driver()
    debut = time.time()
    try:
        livres = _scraper_catalogue(driver, n_pages, journal)
        if avec_fiches:
            livres = _completer_fiches(driver, livres, journal)
    finally:
        driver.quit()

    df = pd.DataFrame(livres)
    for colonne in COLONNES:
        if colonne not in df.columns:
            df[colonne] = ""
    df = df[COLONNES]
    df.attrs["duree_s"] = round(time.time() - debut, 1)
    return df

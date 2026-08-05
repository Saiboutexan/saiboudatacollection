"""Scraping des annonces auto Dakar (gaaraas.com) avec Selenium uniquement.

Variables extraites (cf. énoncé) :
    V1 marque · V2 modèle · V3 année · V4 prix · V5 kilométrage
    V6 type de boîte de vitesses · V7 région de vente

Chaque annonce est un bloc `div.ad-specification` :

    <div class="ad-specification">
      <h4 title="2011 Citroen C3">…</h4>
      <div class="location">Dakar</div>
      <div class="ad-vehicle-price">… <span class="price">2 800 000</span></div>
      <div class="ad-vehicle-mileage"><div class="value">136 000 km</div></div>
      <div class="ad-vehicle-engine">… <div class="transmission"><span>Manuelle</span></div></div>
    </div>

L'année, la marque et le modèle sont tous les trois contenus dans le titre
`h4` : ils sont séparés au nettoyage (`utils.cleaning`).
"""

import time

import pandas as pd
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .driver import attribut_ou_defaut, creer_driver, texte_ou_defaut

URL_ANNONCES = "https://www.gaaraas.com/fr/users/dakar-auto?page={}"

COLONNES = [
    "titre_annonce", "region", "prix", "kilometrage", "boite_vitesses",
    "carburant", "date_publication", "page",
]


def scraper_vehicules(n_pages=1, journal=None) -> pd.DataFrame:
    """Scrape `n_pages` pages d'annonces et renvoie un DataFrame brut.

    La pagination s'arrête d'elle-même dès qu'une page ne renvoie plus
    d'annonce : le compte de pages disponibles varie dans le temps.
    """
    driver = creer_driver()
    debut = time.time()
    annonces = []

    try:
        for page in range(1, n_pages + 1):
            try:
                driver.get(URL_ANNONCES.format(page))
            except TimeoutException:
                # Page trop lente : on garde ce qui est déjà chargé et on
                # laisse le WebDriverWait ci-dessous trancher.
                pass
            try:
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "div.ad-specification"))
                )
            except Exception:
                break  # plus d'annonces : fin de la pagination

            cartes = driver.find_elements(By.CSS_SELECTOR, "div.ad-specification")
            if not cartes:
                break

            for carte in cartes:
                annonces.append({
                    "titre_annonce": attribut_ou_defaut(
                        carte, By.CSS_SELECTOR, "h4", "title")
                    or texte_ou_defaut(carte, By.CSS_SELECTOR, "h4"),
                    "region": texte_ou_defaut(carte, By.CSS_SELECTOR, "div.location"),
                    "prix": texte_ou_defaut(
                        carte, By.CSS_SELECTOR, ".ad-vehicle-price .price"),
                    "kilometrage": texte_ou_defaut(
                        carte, By.CSS_SELECTOR, ".ad-vehicle-mileage .value"),
                    "boite_vitesses": texte_ou_defaut(
                        carte, By.CSS_SELECTOR, ".transmission span"),
                    # textContent plutôt que .text : la mention du carburant
                    # est dans un span que Chrome headless considère masqué.
                    "carburant": attribut_ou_defaut(
                        carte, By.CSS_SELECTOR, ".engine-capacity", "textContent"),
                    "date_publication": texte_ou_defaut(
                        carte, By.CSS_SELECTOR, ".ad-post-date span"),
                    "page": page,
                })

            if journal:
                journal(page, n_pages, len(annonces))

    finally:
        driver.quit()

    df = pd.DataFrame(annonces)
    for colonne in COLONNES:
        if colonne not in df.columns:
            df[colonne] = ""
    df = df[COLONNES]
    df.attrs["duree_s"] = round(time.time() - debut, 1)
    return df

"""Scraping des annonces Dakar Auto (gaaraas.com) avec Selenium."""

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
    driver = creer_driver()
    debut = time.time()
    annonces = []

    try:
        for page in range(1, n_pages + 1):
            try:
                driver.get(URL_ANNONCES.format(page))
            except TimeoutException:
                pass
            try:
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "div.ad-specification"))
                )
            except Exception:
                break

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

"""Création du navigateur Selenium (local et Streamlit Cloud)."""

import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

CHROMIUM_BINAIRE = "/usr/bin/chromium"
CHROMEDRIVER = "/usr/bin/chromedriver"


def creer_driver(headless: bool = True) -> webdriver.Chrome:
    options = Options()
    options.page_load_strategy = "eager"
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )

    if os.path.exists(CHROMIUM_BINAIRE) and os.path.exists(CHROMEDRIVER):
        options.binary_location = CHROMIUM_BINAIRE
        driver = webdriver.Chrome(service=Service(CHROMEDRIVER), options=options)
    else:
        driver = webdriver.Chrome(options=options)

    driver.set_page_load_timeout(45)
    return driver


def texte_ou_defaut(parent, by, selecteur, defaut=""):
    from selenium.common.exceptions import NoSuchElementException

    try:
        return parent.find_element(by, selecteur).text.strip()
    except NoSuchElementException:
        return defaut


def attribut_ou_defaut(parent, by, selecteur, attribut, defaut=""):
    from selenium.common.exceptions import NoSuchElementException

    try:
        valeur = parent.find_element(by, selecteur).get_attribute(attribut)
        return (valeur or defaut).strip()
    except NoSuchElementException:
        return defaut

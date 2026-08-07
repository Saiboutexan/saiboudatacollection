# Collecte de données — Livres & Véhicules

Projet d'examen *Data Collection* : scraping Selenium, nettoyage, base SQLite
et application Streamlit.

## Fonctions

1. Scraper des données sur plusieurs pages (Selenium uniquement).
2. Télécharger les données brutes du scraping no-code (Web Scraper).
3. Visualiser un tableau de bord des données nettoyées.
4. Accéder aux deux formulaires d'évaluation.

## Sources

| Source | URL |
|---|---|
| Books to Scrape | https://books.toscrape.com/ |
| Dakar Auto (gaaraas) | https://www.gaaraas.com/fr/users/dakar-auto |

## Lancement

```bash
pip install -r requirements.txt
```

```bash
streamlit run app.py
```

Google Chrome doit être installé ; le driver est géré automatiquement par
Selenium Manager.

## Structure

```
app.py         application Streamlit
scrapers/      scraping Selenium des deux sources
utils/         nettoyage, base SQLite, graphiques
data/          exports bruts, CSV nettoyés et base collecte.db
webscraper/    sitemaps Web Scraper
formulaires/   XLSForm Kobo + script Google Forms
```

## Formulaires d'évaluation

| Plateforme | Lien |
|---|---|
| Kobo | https://ee-eu.kobotoolbox.org/x/hHUNArxt |
| Google Forms | https://forms.gle/YynLyMtpK5AQzCwp6 |

# Collecte de données — Livres & Véhicules

Projet d'examen *Data Collection* : web scraping, nettoyage, base SQL et
application Streamlit déployée.

L'application couvre les quatre fonctions demandées par l'énoncé :

1. **scraper** des données sur plusieurs pages (Selenium uniquement) ;
2. **télécharger** les données brutes du scraping no-code (Web Scraper) ;
3. **visualiser** un tableau de bord des données nettoyées ;
4. **accéder** aux deux formulaires d'évaluation (Kobo et Google Forms).

---

## 1. Sources et variables

### Books to Scrape — `https://books.toscrape.com/catalogue/page-N.html`

| Variable | Colonne | Où elle est lue |
|---|---|---|
| V1 Titre | `titre` | catalogue, `h3 a[title]` |
| V2 Prix | `prix` | catalogue, `p.price_color` |
| V3 Disponibilité | `disponibilite` | catalogue, `p.instock.availability` |
| V4 Nombre de produits sur la page | `nb_produits_page` | nombre de `article.product_pod` |
| V5 Note | `note` | catalogue, classe CSS `star-rating` |
| V6 Nombre de reviews | `nb_reviews` | **fiche produit**, `table.table-striped` |
| V7 Description | `description` | **fiche produit**, `#product_description + p` |
| V8 Type de produit | `type_produit` | **fiche produit**, 3ᵉ élément du fil d'Ariane |
| V9 Tax | `tax` | **fiche produit**, `table.table-striped` |

V6 à V9 n'existent pas sur la page de catalogue : le scraper fait un second
passage sur la fiche de chaque livre. La case à cocher de l'application permet
de désactiver ce passage (collecte ~10× plus rapide, mais 4 colonnes vides).

### Dakar Auto / gaaraas — `https://www.gaaraas.com/fr/users/dakar-auto?page=N`

| Variable | Colonne | Où elle est lue |
|---|---|---|
| V1 Marque | `marque` | extraite du titre `h4` |
| V2 Modèle | `modele` | extraite du titre `h4` |
| V3 Année | `annee` | extraite du titre `h4` |
| V4 Prix | `prix` | `.ad-vehicle-price .price` |
| V5 Kilométrage | `kilometrage` | `.ad-vehicle-mileage .value` |
| V6 Boîte de vitesses | `boite_vitesses` | `.transmission span` |
| V7 Région de vente | `region` | `div.location` |

Le titre d'annonce contient les trois premières variables en un seul bloc
(« 2011 Citroen C3 ») : la séparation est faite au nettoyage, avec une liste de
marques en deux mots pour ne pas couper « Land Rover » en deux.

> **Écart avec l'énoncé :** l'énoncé annonce 100 pages pour cette source. Au
> 5 août 2026 la page vendeur n'en compte que 13 (245 annonces). Le scraper
> s'arrête automatiquement dès qu'une page ne renvoie plus d'annonce.

---

## 2. Installation et lancement en local

```bash
pip install -r requirements.txt
```

```bash
streamlit run app.py
```

Google Chrome doit être installé : depuis Selenium 4.6, le driver est
téléchargé automatiquement (Selenium Manager), aucun chromedriver à gérer.

---

## 3. Structure du projet

```
app.py                     application Streamlit (4 pages)
scrapers/
  driver.py                création du navigateur Chrome/Chromium
  books_scraper.py         scraping Selenium de books.toscrape.com
  gaaraas_scraper.py       scraping Selenium des annonces Dakar Auto
utils/
  cleaning.py              nettoyage et typage des données
  database.py              base SQLite : schéma, écriture, lecture
  viz.py                   graphiques matplotlib / seaborn
assets/style.css           habillage de l'application
data/raw/                  exports bruts de Web Scraper (à déposer)
data/clean/                CSV nettoyés produits par l'application
data/collecte.db           base SQLite (créée au premier lancement)
webscraper/                sitemaps à importer dans l'extension Web Scraper
formulaires/               XLSForm Kobo + script Google Forms
```

---

## 4. Base de données

SQLite, une table par source (`data/collecte.db`) :

| Table | Contenu |
|---|---|
| `livres` | données nettoyées de Books to Scrape |
| `vehicules` | données nettoyées de Dakar Auto |
| `journal_scraping` | trace de chaque collecte : source, pages, lignes, durée |

Chaque collecte remplace le contenu de la table correspondante et ajoute une
ligne au journal. L'onglet « Base de données » du tableau de bord affiche le
décompte des lignes et l'historique des collectes.

---

## 5. Scraping no-code (Web Scraper)

Deux sitemaps prêts à l'emploi dans `webscraper/` :

1. ouvrir les DevTools → onglet **Web Scraper** → *Create new sitemap* →
   **Import sitemap** ;
2. coller le contenu de `sitemap_books_toscrape.json` ou
   `sitemap_dakar_auto.json` ;
3. *Scrape*, puis *Export data as CSV* ;
4. déposer le CSV obtenu dans `data/raw/`.

Les fichiers déposés là apparaissent automatiquement dans l'option
« Télécharger les données brutes » de l'application, **sans nettoyage**, comme
l'exige l'énoncé.

---

## 6. Formulaires d'évaluation

| Plateforme | Lien |
|---|---|
| Kobo | https://ee-eu.kobotoolbox.org/x/hHUNArxt |
| Google Forms | https://forms.gle/YynLyMtpK5AQzCwp6 |

Sources et procédure de redéploiement : voir
[`formulaires/README_formulaires.md`](formulaires/README_formulaires.md).

---

## 7. Déploiement sur Streamlit Community Cloud

1. Pousser le dossier sur GitHub (le `.gitignore` exclut la base et les CSV).
2. share.streamlit.io → *New app* → dépôt, branche, `app.py`.
3. `requirements.txt` et `packages.txt` sont pris en compte automatiquement :
   `packages.txt` installe `chromium` et `chromium-driver`, et
   `scrapers/driver.py` bascule tout seul sur ces binaires quand il les
   détecte.

Le scraping en ligne reste lent (environ 20 s par page d'annonces, 3 s par
fiche de livre) : garder un nombre de pages modeste pendant la démonstration.

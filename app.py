"""Application Streamlit — collecte, nettoyage et visualisation de données.

Quatre fonctions, pilotées depuis la barre latérale :
    1. scraper des données sur plusieurs pages (Selenium) ;
    2. télécharger les données brutes du scraping no-code (Web Scraper) ;
    3. visualiser le tableau de bord des données nettoyées ;
    4. accéder aux deux formulaires d'évaluation (Kobo et Google Forms).
"""

import base64
from pathlib import Path

import pandas as pd
import streamlit as st

from scrapers import scraper_livres, scraper_vehicules
from utils import database as bd
from utils import viz
from utils.cleaning import nettoyer_livres, nettoyer_vehicules

# ---------------------------------------------------------------- constantes

RACINE = Path(__file__).resolve().parent
DOSSIER_BRUT = RACINE / "data" / "raw"
DOSSIER_PROPRE = RACINE / "data" / "clean"

FORMULAIRE_KOBO = "https://ee-eu.kobotoolbox.org/x/hHUNArxt"
FORMULAIRE_GOOGLE = (
    "https://docs.google.com/forms/d/e/"
    "1FAIpQLSfbQ-zkFTtcFZPuO4fXG65G9vBL1WoFOBlCc4Yo23zTF5QMPw/viewform"
)

SOURCE_LIVRES = "Livres — Books to Scrape"
SOURCE_VEHICULES = "Véhicules — Dakar Auto"

OPTIONS = [
    "Scraper les données avec Selenium",
    "Télécharger les données brutes (Web Scraper)",
    "Tableau de bord des données",
    "Évaluer l'application",
]

st.set_page_config(
    page_title="Collecte de données — Livres & Véhicules",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


EXTENSIONS_IMAGE = (".png", ".jpg", ".jpeg", ".webp")


def _image_de_fond() -> Path | None:
    """Retourne l'image de fond déposée dans `assets/`.

    Toute image dont le nom commence par « dit » convient : `dit.jpeg`,
    `dit_banner.png`, etc.
    """
    dossier = RACINE / "assets"
    candidates = sorted(
        chemin for chemin in dossier.glob("dit*")
        if chemin.suffix.lower() in EXTENSIONS_IMAGE
    )
    return candidates[0] if candidates else None


def charger_style() -> None:
    feuille = RACINE / "assets" / "style.css"
    if feuille.exists():
        st.markdown(f"<style>{feuille.read_text(encoding='utf-8')}</style>",
                    unsafe_allow_html=True)

    # L'image est encodée en base64 et injectée dans la feuille de style :
    # Streamlit ne sert pas les fichiers statiques du projet par défaut.
    # Le voile sombre par-dessus garde le texte lisible.
    fond = _image_de_fond()
    if fond is None:
        return

    mime = "jpeg" if fond.suffix.lower() in (".jpg", ".jpeg") else fond.suffix.lstrip(".")
    encodee = base64.b64encode(fond.read_bytes()).decode()
    st.markdown(
        f"""<style>
        .stApp {{
            background-image:
                linear-gradient(rgba(4, 47, 46, 0.88), rgba(4, 47, 46, 0.94)),
                url("data:image/{mime};base64,{encodee}");
            background-size: cover;
            background-position: center top;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>""",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------- en-tête

def afficher_entete() -> None:
    st.markdown("<h1 class='titre-app'>COLLECTE DE DONNÉES</h1>",
                unsafe_allow_html=True)
    st.markdown(
        "<p class='sous-titre'>Cette application scrape des données sur "
        "plusieurs pages, les nettoie, les stocke dans une base SQL et les "
        "restitue sous forme de tableau de bord. Les données brutes issues du "
        "scraping no-code sont également téléchargeables.</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "- **Bibliothèques Python :** streamlit, selenium, pandas, seaborn, sqlite3\n"
        "- **Sources de données :** "
        "[Books to Scrape](https://books.toscrape.com/) — "
        "[Dakar Auto (gaaraas)](https://www.gaaraas.com/fr/users/dakar-auto)"
    )
    st.divider()


# ---------------------------------------------------------------- utilitaires

def bouton_telechargement(df: pd.DataFrame, nom_fichier: str, libelle: str,
                          cle: str) -> None:
    st.download_button(
        libelle,
        data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name=nom_fichier,
        mime="text/csv",
        key=cle,
        use_container_width=True,
    )


def afficher_tableau(df: pd.DataFrame, titre: str) -> None:
    st.subheader(titre)
    st.markdown(
        f"**Dimension des données : {df.shape[0]} lignes et "
        f"{df.shape[1]} colonnes.**"
    )
    st.dataframe(df, use_container_width=True, height=420)


def sauvegarder_csv(df: pd.DataFrame, nom: str) -> Path:
    DOSSIER_PROPRE.mkdir(parents=True, exist_ok=True)
    chemin = DOSSIER_PROPRE / nom
    df.to_csv(chemin, index=False, encoding="utf-8-sig")
    return chemin


# ---------------------------------------------------------------- option 1

def page_scraping(n_pages: int) -> None:
    st.header("Collecte des données avec Selenium")
    st.caption(
        "Le scraping est réalisé exclusivement avec Selenium, puis les données "
        "sont nettoyées et enregistrées dans la base SQLite de l'application."
    )

    avec_fiches = st.checkbox(
        "Ouvrir la fiche de chaque livre (description, catégorie, tax, "
        "nombre de reviews)",
        value=True,
        help="Ces quatre variables ne sont pas présentes sur la page de "
             "catalogue. Décocher accélère fortement la collecte.",
    )

    gauche, droite = st.columns(2)
    lancer_livres = gauche.button(SOURCE_LIVRES, use_container_width=True)
    lancer_vehicules = droite.button(SOURCE_VEHICULES, use_container_width=True)

    if lancer_livres:
        barre = st.progress(0.0, text="Ouverture du navigateur…")

        def suivi(courant, total, nb_lignes):
            barre.progress(min(courant / max(total, 1), 1.0),
                           text=f"{courant}/{total} — {nb_lignes} lignes collectées")

        with st.spinner("Collecte en cours sur books.toscrape.com…"):
            brut = scraper_livres(n_pages, avec_fiches=avec_fiches, journal=suivi)
            propre = nettoyer_livres(brut)

        barre.empty()
        lignes = bd.enregistrer(propre, bd.TABLE_LIVRES, remplacer=True)
        bd.journaliser("livres", n_pages, lignes, brut.attrs.get("duree_s", 0))
        sauvegarder_csv(propre, "livres_propre.csv")
        st.session_state["livres"] = propre
        st.success(
            f"{lignes} livres collectés en {brut.attrs.get('duree_s', 0)} s "
            f"puis enregistrés dans la table `{bd.TABLE_LIVRES}`."
        )

    if lancer_vehicules:
        barre = st.progress(0.0, text="Ouverture du navigateur…")

        def suivi(courant, total, nb_lignes):
            barre.progress(min(courant / max(total, 1), 1.0),
                           text=f"Page {courant}/{total} — {nb_lignes} annonces")

        with st.spinner("Collecte en cours sur gaaraas.com…"):
            brut = scraper_vehicules(n_pages, journal=suivi)
            propre = nettoyer_vehicules(brut)

        barre.empty()
        lignes = bd.enregistrer(propre, bd.TABLE_VEHICULES, remplacer=True)
        bd.journaliser("vehicules", n_pages, lignes, brut.attrs.get("duree_s", 0))
        sauvegarder_csv(propre, "vehicules_propre.csv")
        st.session_state["vehicules"] = propre
        st.success(
            f"{lignes} annonces collectées en {brut.attrs.get('duree_s', 0)} s "
            f"puis enregistrées dans la table `{bd.TABLE_VEHICULES}`."
        )

    for cle, titre, fichier in (
        ("livres", "Livres collectés", "livres_propre.csv"),
        ("vehicules", "Véhicules collectés", "vehicules_propre.csv"),
    ):
        if cle in st.session_state:
            afficher_tableau(st.session_state[cle], titre)
            bouton_telechargement(st.session_state[cle], fichier,
                                  "Télécharger ces données en CSV", f"dl_{cle}")


# ---------------------------------------------------------------- option 2

def page_donnees_brutes() -> None:
    st.header("Données brutes — scraping no-code (Web Scraper)")
    st.caption(
        "Fichiers exportés depuis l'extension Chrome Web Scraper, sans aucun "
        "nettoyage, tels que produits par l'outil."
    )

    DOSSIER_BRUT.mkdir(parents=True, exist_ok=True)
    fichiers = sorted(
        [f for f in DOSSIER_BRUT.iterdir() if f.suffix.lower() in (".csv", ".json")]
    )

    if not fichiers:
        st.warning(
            "Aucun export trouvé dans `data/raw/`. Déposer les fichiers "
            "exportés depuis Web Scraper dans ce dossier."
        )
        return

    for fichier in fichiers:
        st.subheader(fichier.name)
        try:
            if fichier.suffix.lower() == ".csv":
                df = pd.read_csv(fichier, dtype=str, keep_default_na=False)
            else:
                df = pd.read_json(fichier, dtype=str)
        except Exception as erreur:
            st.error(f"Lecture impossible : {erreur}")
            continue

        st.markdown(
            f"**Dimension des données : {df.shape[0]} lignes et "
            f"{df.shape[1]} colonnes.**"
        )
        st.dataframe(df.head(200), use_container_width=True, height=320)
        st.download_button(
            f"Télécharger {fichier.name}",
            data=fichier.read_bytes(),
            file_name=fichier.name,
            mime="text/csv",
            key=f"brut_{fichier.name}",
        )
        st.divider()


# ---------------------------------------------------------------- option 3

def _donnees_dashboard(table: str, cle_session: str, fichier: str) -> pd.DataFrame:
    """Priorité à la base SQL ; à défaut, au dernier CSV nettoyé."""
    if bd.compter(table) > 0:
        return bd.lire_table(table)
    chemin = DOSSIER_PROPRE / fichier
    if chemin.exists():
        return pd.read_csv(chemin)
    return st.session_state.get(cle_session, pd.DataFrame())


def _dashboard_livres() -> None:
    df = _donnees_dashboard(bd.TABLE_LIVRES, "livres", "livres_propre.csv")
    if df.empty:
        st.info("Aucune donnée : lancer d'abord une collecte sur les livres.")
        return

    categories = sorted(c for c in df["type_produit"].dropna().unique() if c)
    choix = st.multiselect("Filtrer par catégorie", categories)
    if choix:
        df = df[df["type_produit"].isin(choix)]

    prix = pd.to_numeric(df["prix"], errors="coerce")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Livres", f"{len(df)}")
    c2.metric("Prix moyen", f"£{prix.mean():.2f}" if prix.notna().any() else "—")
    c3.metric("Note moyenne",
              f"{pd.to_numeric(df['note'], errors='coerce').mean():.2f}")
    c4.metric("En stock", f"{int(pd.to_numeric(df['en_stock'], errors='coerce').sum())}")

    g, d = st.columns(2)
    g.pyplot(viz.livres_distribution_prix(df), use_container_width=True)
    d.pyplot(viz.livres_par_note(df), use_container_width=True)
    g2, d2 = st.columns(2)
    g2.pyplot(viz.livres_top_categories(df), use_container_width=True)
    d2.pyplot(viz.livres_prix_par_note(df), use_container_width=True)

    with st.expander("Voir les données nettoyées"):
        st.dataframe(df, use_container_width=True)


def _dashboard_vehicules() -> None:
    df = _donnees_dashboard(bd.TABLE_VEHICULES, "vehicules", "vehicules_propre.csv")
    if df.empty:
        st.info("Aucune donnée : lancer d'abord une collecte sur les véhicules.")
        return

    marques = sorted(m for m in df["marque"].dropna().unique() if m)
    choix = st.multiselect("Filtrer par marque", marques)
    if choix:
        df = df[df["marque"].isin(choix)]

    prix = pd.to_numeric(df["prix"], errors="coerce")
    km = pd.to_numeric(df["kilometrage"], errors="coerce")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Annonces", f"{len(df)}")
    c2.metric("Prix médian",
              f"{prix.median():,.0f} FCFA".replace(",", " ")
              if prix.notna().any() else "—")
    c3.metric("Kilométrage médian",
              f"{km.median():,.0f} km".replace(",", " ")
              if km.notna().any() else "—")
    c4.metric("Marques distinctes", f"{df['marque'].nunique()}")

    g, d = st.columns(2)
    g.pyplot(viz.vehicules_top_marques(df), use_container_width=True)
    d.pyplot(viz.vehicules_prix_median_marque(df), use_container_width=True)
    g2, d2 = st.columns(2)
    g2.pyplot(viz.vehicules_prix_par_annee(df), use_container_width=True)
    d2.pyplot(viz.vehicules_boite_vitesses(df), use_container_width=True)
    g3, d3 = st.columns(2)
    g3.pyplot(viz.vehicules_kilometrage(df), use_container_width=True)
    d3.pyplot(viz.vehicules_par_region(df), use_container_width=True)

    with st.expander("Voir les données nettoyées"):
        st.dataframe(df, use_container_width=True)


def page_dashboard() -> None:
    st.header("Tableau de bord des données nettoyées")
    st.caption("Données issues du scraping Selenium, lues depuis la base SQL.")

    onglet_livres, onglet_vehicules, onglet_base = st.tabs(
        ["Livres", "Véhicules", "Base de données"])
    with onglet_livres:
        _dashboard_livres()
    with onglet_vehicules:
        _dashboard_vehicules()
    with onglet_base:
        c1, c2 = st.columns(2)
        c1.metric(f"Table `{bd.TABLE_LIVRES}`", f"{bd.compter(bd.TABLE_LIVRES)} lignes")
        c2.metric(f"Table `{bd.TABLE_VEHICULES}`",
                  f"{bd.compter(bd.TABLE_VEHICULES)} lignes")
        st.subheader("Journal des collectes")
        journal = bd.journal_recent()
        if journal.empty:
            st.info("Aucune collecte enregistrée pour l'instant.")
        else:
            st.dataframe(journal, use_container_width=True)


# ---------------------------------------------------------------- option 4

def page_evaluation() -> None:
    st.markdown("<h2 class='titre-section'>Donnez votre avis</h2>",
                unsafe_allow_html=True)
    st.caption(
        "Le même formulaire est disponible en deux versions. Cinq minutes "
        "suffisent, les réponses sont anonymes."
    )

    gauche, droite = st.columns(2)
    gauche.link_button("Formulaire d'évaluation Kobo", FORMULAIRE_KOBO,
                       use_container_width=True)
    droite.link_button("Formulaire d'évaluation Google Forms", FORMULAIRE_GOOGLE,
                       use_container_width=True)

    onglet_kobo, onglet_google = st.tabs(["Formulaire Kobo", "Formulaire Google"])
    with onglet_kobo:
        st.components.v1.iframe(FORMULAIRE_KOBO, height=800, scrolling=True)
    with onglet_google:
        st.components.v1.iframe(FORMULAIRE_GOOGLE + "?embedded=true",
                                height=800, scrolling=True)


# ---------------------------------------------------------------- point d'entrée

def main() -> None:
    charger_style()

    st.sidebar.title("Paramètres de collecte")
    n_pages = st.sidebar.number_input(
        "Nombre de pages à scraper", min_value=1, max_value=100, value=2, step=1,
        help="books.toscrape.com compte 50 pages ; la page vendeur de "
             "gaaraas.com en compte une quinzaine. La collecte s'arrête "
             "automatiquement à la dernière page disponible.",
    )
    option = st.sidebar.selectbox("Options", OPTIONS)
    st.sidebar.divider()
    st.sidebar.caption(
        f"Base SQL : {bd.compter(bd.TABLE_LIVRES)} livres · "
        f"{bd.compter(bd.TABLE_VEHICULES)} véhicules"
    )

    afficher_entete()

    if option == OPTIONS[0]:
        page_scraping(int(n_pages))
    elif option == OPTIONS[1]:
        page_donnees_brutes()
    elif option == OPTIONS[2]:
        page_dashboard()
    else:
        page_evaluation()


if __name__ == "__main__":
    main()

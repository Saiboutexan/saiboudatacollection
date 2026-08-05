"""Base SQL (SQLite) de l'application : une table par source de données."""

import sqlite3
from pathlib import Path

import pandas as pd

RACINE = Path(__file__).resolve().parent.parent
CHEMIN_BD = RACINE / "data" / "collecte.db"

TABLE_LIVRES = "livres"
TABLE_VEHICULES = "vehicules"
TABLE_JOURNAL = "journal_scraping"

SCHEMA = f"""
CREATE TABLE IF NOT EXISTS {TABLE_LIVRES} (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    titre             TEXT    NOT NULL,
    prix              REAL,
    disponibilite     TEXT,
    en_stock          INTEGER,
    nb_produits_page  INTEGER,
    note              INTEGER,
    nb_reviews        INTEGER,
    description       TEXT,
    type_produit      TEXT,
    tax               REAL,
    url               TEXT,
    collecte_le       TEXT    DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS {TABLE_VEHICULES} (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    marque            TEXT,
    modele            TEXT,
    annee             INTEGER,
    prix              INTEGER,
    kilometrage       INTEGER,
    boite_vitesses    TEXT,
    region            TEXT,
    carburant         TEXT,
    date_publication  TEXT,
    titre_annonce     TEXT,
    page              INTEGER,
    collecte_le       TEXT    DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS {TABLE_JOURNAL} (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    source       TEXT,
    nb_pages     INTEGER,
    nb_lignes    INTEGER,
    duree_s      REAL,
    execute_le   TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_livres_type ON {TABLE_LIVRES}(type_produit);
CREATE INDEX IF NOT EXISTS idx_vehicules_marque ON {TABLE_VEHICULES}(marque);
"""


def connexion() -> sqlite3.Connection:
    """Ouvre la base (et la crée au premier appel)."""
    CHEMIN_BD.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(CHEMIN_BD, check_same_thread=False)
    conn.executescript(SCHEMA)
    return conn


def enregistrer(df: pd.DataFrame, table: str, remplacer: bool = True) -> int:
    """Écrit un DataFrame nettoyé dans la table indiquée.

    `remplacer=True` vide la table avant insertion : c'est le comportement
    voulu quand on relance un scraping complet. `False` ajoute les lignes.
    """
    if df.empty:
        return 0

    conn = connexion()
    try:
        colonnes_bd = {
            info[1] for info in conn.execute(f"PRAGMA table_info({table})")
        }
        a_ecrire = df[[c for c in df.columns if c in colonnes_bd]].copy()

        if remplacer:
            conn.execute(f"DELETE FROM {table}")
        a_ecrire.to_sql(table, conn, if_exists="append", index=False)
        conn.commit()
        return len(a_ecrire)
    finally:
        conn.close()


def journaliser(source: str, nb_pages: int, nb_lignes: int, duree_s: float) -> None:
    """Trace chaque exécution de scraping dans la table de journal."""
    conn = connexion()
    try:
        conn.execute(
            f"INSERT INTO {TABLE_JOURNAL} (source, nb_pages, nb_lignes, duree_s) "
            "VALUES (?, ?, ?, ?)",
            (source, nb_pages, nb_lignes, duree_s),
        )
        conn.commit()
    finally:
        conn.close()


def lire_table(table: str, limite: int | None = None) -> pd.DataFrame:
    """Relit une table complète sous forme de DataFrame."""
    conn = connexion()
    try:
        requete = f"SELECT * FROM {table}"
        if limite:
            requete += f" LIMIT {int(limite)}"
        return pd.read_sql_query(requete, conn)
    finally:
        conn.close()


def compter(table: str) -> int:
    """Nombre de lignes stockées dans une table."""
    conn = connexion()
    try:
        return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    finally:
        conn.close()


def journal_recent(limite: int = 10) -> pd.DataFrame:
    """Dernières exécutions de scraping, les plus récentes en premier."""
    conn = connexion()
    try:
        return pd.read_sql_query(
            f"SELECT source, nb_pages, nb_lignes, duree_s, execute_le "
            f"FROM {TABLE_JOURNAL} ORDER BY id DESC LIMIT {int(limite)}",
            conn,
        )
    finally:
        conn.close()

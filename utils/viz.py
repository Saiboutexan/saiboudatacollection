"""Graphiques du tableau de bord (matplotlib + seaborn)."""

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

matplotlib.use("Agg")
sns.set_theme(style="whitegrid", palette="crest")

TAILLE = (7, 4)


def _figure():
    fig, ax = plt.subplots(figsize=TAILLE)
    return fig, ax


def _numerique(serie: pd.Series) -> pd.Series:
    return pd.to_numeric(serie, errors="coerce").dropna().astype(float)


def livres_distribution_prix(df: pd.DataFrame):
    fig, ax = _figure()
    sns.histplot(_numerique(df["prix"]), bins=30, kde=True, ax=ax)
    ax.set_title("Distribution des prix des livres")
    ax.set_xlabel("Prix (£)")
    ax.set_ylabel("Nombre de livres")
    fig.tight_layout()
    return fig


def livres_par_note(df: pd.DataFrame):
    fig, ax = _figure()
    donnees = _numerique(df["note"]).astype(int)
    sns.countplot(x=donnees, ax=ax)
    ax.set_title("Répartition des livres par note")
    ax.set_xlabel("Note (étoiles)")
    ax.set_ylabel("Nombre de livres")
    fig.tight_layout()
    return fig


def livres_top_categories(df: pd.DataFrame, n: int = 10):
    fig, ax = _figure()
    top = (df["type_produit"].dropna().replace("", pd.NA).dropna()
           .value_counts().head(n))
    sns.barplot(x=top.values, y=top.index, ax=ax, orient="h")
    ax.set_title(f"Top {n} des catégories de livres")
    ax.set_xlabel("Nombre de livres")
    ax.set_ylabel("")
    fig.tight_layout()
    return fig


def livres_prix_par_note(df: pd.DataFrame):
    fig, ax = _figure()
    donnees = df[["note", "prix"]].copy()
    donnees["note"] = pd.to_numeric(donnees["note"], errors="coerce")
    donnees["prix"] = pd.to_numeric(donnees["prix"], errors="coerce")
    donnees = donnees.dropna()
    sns.boxplot(data=donnees, x="note", y="prix", ax=ax)
    ax.set_title("Prix des livres selon la note")
    ax.set_xlabel("Note (étoiles)")
    ax.set_ylabel("Prix (£)")
    fig.tight_layout()
    return fig


def vehicules_top_marques(df: pd.DataFrame, n: int = 10):
    fig, ax = _figure()
    top = df["marque"].dropna().value_counts().head(n)
    sns.barplot(x=top.values, y=top.index, ax=ax, orient="h")
    ax.set_title(f"Top {n} des marques les plus proposées")
    ax.set_xlabel("Nombre d'annonces")
    ax.set_ylabel("")
    fig.tight_layout()
    return fig


def vehicules_prix_median_marque(df: pd.DataFrame, n: int = 10):
    fig, ax = _figure()
    donnees = df[["marque", "prix"]].copy()
    donnees["prix"] = pd.to_numeric(donnees["prix"], errors="coerce")
    donnees = donnees.dropna()
    marques = donnees["marque"].value_counts().head(n).index
    median = (donnees[donnees["marque"].isin(marques)]
              .groupby("marque")["prix"].median().sort_values(ascending=False))
    sns.barplot(x=(median.values / 1_000_000), y=median.index, ax=ax, orient="h")
    ax.set_title(f"Prix médian des {n} marques les plus proposées")
    ax.set_xlabel("Prix médian (millions FCFA)")
    ax.set_ylabel("")
    fig.tight_layout()
    return fig


def vehicules_prix_par_annee(df: pd.DataFrame):
    fig, ax = _figure()
    donnees = df[["annee", "prix", "boite_vitesses"]].copy()
    donnees["annee"] = pd.to_numeric(donnees["annee"], errors="coerce")
    donnees["prix"] = pd.to_numeric(donnees["prix"], errors="coerce")
    donnees = donnees.dropna(subset=["annee", "prix"])
    sns.scatterplot(data=donnees, x="annee", y="prix",
                    hue="boite_vitesses", alpha=0.7, ax=ax)
    ax.set_title("Prix des véhicules selon l'année")
    ax.set_xlabel("Année")
    ax.set_ylabel("Prix (FCFA)")
    ax.legend(title="Boîte", fontsize=8)
    fig.tight_layout()
    return fig


def vehicules_boite_vitesses(df: pd.DataFrame):
    fig, ax = _figure()
    comptes = df["boite_vitesses"].fillna("Non renseignée").value_counts()
    ax.pie(comptes.values, labels=comptes.index, autopct="%1.1f%%",
           startangle=90, colors=sns.color_palette("crest", len(comptes)))
    ax.set_title("Répartition par type de boîte de vitesses")
    fig.tight_layout()
    return fig


def vehicules_kilometrage(df: pd.DataFrame):
    fig, ax = _figure()
    km = _numerique(df["kilometrage"])
    km = km[km.between(0, 600_000)]
    sns.histplot(km, bins=30, kde=True, ax=ax)
    ax.set_title("Distribution du kilométrage")
    ax.set_xlabel("Kilométrage (km)")
    ax.set_ylabel("Nombre d'annonces")
    fig.tight_layout()
    return fig


def vehicules_par_region(df: pd.DataFrame, n: int = 10):
    fig, ax = _figure()
    top = df["region"].dropna().value_counts().head(n)
    sns.barplot(x=top.values, y=top.index, ax=ax, orient="h")
    ax.set_title(f"Top {n} des régions de vente")
    ax.set_xlabel("Nombre d'annonces")
    ax.set_ylabel("")
    fig.tight_layout()
    return fig

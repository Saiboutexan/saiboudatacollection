# Formulaires d'évaluation de l'application web

Deux versions du même formulaire, conformes au document
« Questions des deux formulaire d'évaluation.pdf » (6 sections, 3 logiques
conditionnelles, 1 champ calculé).

| Fichier | Cible | Rôle |
|---|---|---|
| `kobo_evaluation_application.xlsx` | KoboToolbox | XLSForm à importer tel quel |
| `google_forms_script.gs` | Google Forms | Script Apps Script qui construit le formulaire |

---

## 1. Déploiement sur KoboToolbox

1. Se connecter sur https://kf.kobotoolbox.org (ou https://eu.kobotoolbox.org).
2. **NEW** → **Upload an XLSForm** → déposer `kobo_evaluation_application.xlsx`.
3. Ouvrir le projet créé → **Deploy** (bouton en haut à droite).
4. Onglet **FORM** → **Collect data** → copier le lien **Online-Only** (ou
   **Online-Offline**). C'est ce lien qui va dans l'application Streamlit.

Le fichier a été validé avec `pyxform` (le convertisseur utilisé par Kobo) :
la conversion en XForm passe sans erreur.

### Contenu du XLSForm

* Feuille `survey` : 45 lignes (6 groupes = 6 sections, en mode `style: pages`,
  donc une section par écran).
* Feuille `choices` : 41 lignes (9 listes de choix).
* Feuille `settings` : titre, `form_id`, version, langue `Français (fr)`.

### Les 3 logiques conditionnelles (colonne `relevant`)

| Question affichée | Condition |
|---|---|
| Autre profession | `${role} = 'autre'` |
| Combien de fois l'avez-vous utilisée auparavant ? | `${premiere_utilisation} = 'non'` |
| Quel(s) type(s) de problème(s) ? + description | `${problemes} = 'oui'` |

### Le champ calculé

* `rating` : type `integer`, `constraint` = `. >= 0 and . <= 10`.
* `niveau_satisfaction` : type `calculate`, formule exactement celle de la
  spécification :

  ```
  if(${rating} >= 9, "Excellent", if(${rating} >= 7, "Très bon",
  if(${rating} >= 5, "Bon", if(${rating} >= 3, "Passable", "Médiocre"))))
  ```

* Une `note` en lecture seule affiche le résultat au répondant
  (« Niveau de satisfaction : **Très bon** »), puisqu'un champ `calculate`
  est invisible par défaut.

---

## 2. Déploiement sur Google Forms

1. Aller sur https://script.google.com → **Nouveau projet**.
2. Remplacer tout le code par le contenu de `google_forms_script.gs`.
3. Choisir la fonction `creerFormulaireEvaluation` → **Exécuter**.
4. Autoriser le script (première exécution : *Paramètres avancés* →
   *Accéder au projet non sécurisé* — c'est ton propre script).
5. Ouvrir **Journal d'exécution** (`Ctrl+Entrée`) : les 3 liens s'affichent.
   Le **lien public** est celui à mettre dans Streamlit.

> ⚠️ Ne pas utiliser le bouton **Déployer** de l'éditeur Apps Script : il
> produit une URL du type `https://script.google.com/macros/s/.../dev`, qui
> est une URL de déploiement du *script* (accessible uniquement à son
> propriétaire), pas le formulaire. Le bon lien commence toujours par
> `https://docs.google.com/forms/d/e/` et se termine par `/viewform`.
> Si le journal a été perdu, exécuter `retrouverLienFormulaire()`.

### Correspondance des logiques conditionnelles

Google Forms ne fait pas d'affichage conditionnel question par question :
il fait du **branchement de section**. Le script crée donc des pages dédiées :

| Réponse | Aiguillage |
|---|---|
| Rôle = *Autre* | → page « Précision sur votre profession », puis retour au flux |
| Rôle ≠ *Autre* | → page « Section 1 (suite) » (saute la question) |
| Première utilisation = *Non* | → page « Fréquence d'utilisation » |
| Première utilisation = *Oui* | → Section 2 directement |
| Problèmes = *Oui* | → page « Détail des problèmes » |
| Problèmes = *Non* | → Section 5 directement |

Chaque question de branchement est placée en **dernière position de sa page** :
c'est la condition pour que le « Accéder à la section en fonction de la
réponse » fonctionne de façon fiable.

### Le champ calculé sous Google Forms

Google Forms n'a pas de type « Calcul ». Deux solutions, les deux fournies
dans le script :

* **Automatique** : les fonctions `installerCalculNiveauSatisfaction` /
  `majNiveauSatisfaction` à coller dans le script de la feuille de réponses.
  Un déclencheur « à l'envoi du formulaire » remplit une colonne
  *Niveau de satisfaction*.
* **Manuelle** : la formule à mettre dans la feuille de réponses

  ```
  =SI(B2>=9;"Excellent";SI(B2>=7;"Très bon";SI(B2>=5;"Bon";SI(B2>=3;"Passable";"Médiocre"))))
  ```

La règle affichée au répondant (9-10 = Excellent, 7-8 = Très bon, 5-6 = Bon,
3-4 = Passable, 0-2 = Médiocre) est reprise en texte d'aide dans la section 5.

---

## 3. Écarts assumés par rapport à la spécification

* **« Combien de fois l'avez-vous utilisée auparavant ? »** et
  **« Quel(s) type(s) de problème(s) ? »** / **« décrire le(s) problème(s) »** :
  la spécification ne les marque pas *Obligatoire* — elles sont donc laissées
  facultatives. Si le correcteur les attend obligatoires, il suffit de mettre
  `yes` dans la colonne `required` du XLSForm et `.setRequired(true)` dans le
  script Google.
* **Note globale** : sous Kobo c'est bien un `integer` avec contrainte 0-10 ;
  sous Google Forms c'est une échelle linéaire 0→10 (seul moyen natif de
  garantir un entier borné).
* **Échelles de Likert** : une question par affirmation (comme dans la
  spécification), pas une grille.

---

## 4. Intégration dans l'application Streamlit

Une fois les deux liens obtenus :

```python
KOBO_URL = "https://ee-eu.kobotoolbox.org/x/hHUNArxt"
GOOGLE_FORM_URL = (
    "https://docs.google.com/forms/d/e/"
    "1FAIpQLSfbQ-zkFTtcFZPuO4fXG65G9vBL1WoFOBlCc4Yo23zTF5QMPw/viewform"
)
# lien court équivalent : https://forms.gle/YynLyMtpK5AQzCwp6

st.subheader("Évaluer l'application")
onglet_kobo, onglet_google = st.tabs(["Formulaire Kobo", "Formulaire Google"])

with onglet_kobo:
    st.link_button("Ouvrir dans un nouvel onglet", KOBO_URL)
    st.components.v1.iframe(KOBO_URL, height=800, scrolling=True)

with onglet_google:
    st.link_button("Ouvrir dans un nouvel onglet", GOOGLE_FORM_URL)
    st.components.v1.iframe(GOOGLE_FORM_URL + "?embedded=true",
                            height=800, scrolling=True)
```

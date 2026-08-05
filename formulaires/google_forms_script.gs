/**
 * ============================================================================
 *  ÉVALUATION DE L'APPLICATION WEB — Générateur de formulaire Google Forms
 * ============================================================================
 *
 *  Ce script reproduit à l'identique le formulaire spécifié dans
 *  « Questions des deux formulaire d'évaluation.pdf » :
 *  6 sections, types de champs, questions obligatoires et logiques
 *  conditionnelles (branchement par sections).
 *
 *  UTILISATION
 *  -----------
 *   1. Aller sur https://script.google.com  →  « Nouveau projet ».
 *   2. Coller tout ce fichier dans l'éditeur (remplacer le code par défaut).
 *   3. Sélectionner la fonction `creerFormulaireEvaluation` puis « Exécuter ».
 *   4. Autoriser le script (compte Google → « Paramètres avancés » →
 *      « Accéder au projet »).
 *   5. Les liens (édition + réponse publique) s'affichent dans « Journal
 *      d'exécution » (Ctrl+Entrée). C'est le lien « publique » à mettre
 *      dans l'application Streamlit.
 *
 *  REMARQUE SUR LE CHAMP « Niveau de satisfaction » (type Calcul)
 *  -------------------------------------------------------------
 *  Google Forms ne gère pas les champs calculés (contrairement à Kobo).
 *  Le calcul est donc reproduit côté feuille de réponses :
 *  voir la fonction `installerCalculNiveauSatisfaction` en bas de fichier.
 * ============================================================================
 */

// ---------------------------------------------------------------- constantes

var TITRE = "Évaluation de l'application web";
var DESCRIPTION =
  "Ce formulaire vise à recueillir votre avis sur l'application de collecte " +
  "de données (scraping, téléchargement, tableau de bord). " +
  "Vos réponses sont anonymes et prendront environ 5 minutes.";

var LIKERT = [
  "Tout à fait en désaccord",
  "En désaccord",
  "Neutre",
  "D'accord",
  "Tout à fait d'accord"
];

var INTRO_LIKERT =
  "Indiquez votre niveau d'accord avec chacune des affirmations suivantes.";

var MESSAGE_FINAL =
  "Merci pour votre précieux retour ! Vos commentaires nous aideront à " +
  "améliorer l'application.";

// ---------------------------------------------------------------- générateur

/**
 * >>> C'EST CETTE FONCTION QU'IL FAUT EXÉCUTER. <<<
 * Les autres fonctions de ce fichier (choixUnique, likert, choixMultiple,
 * texteLong) sont des utilitaires : elles attendent le formulaire en
 * paramètre et échouent avec « Cannot read properties of undefined » si on
 * les lance seules depuis le menu déroulant de l'éditeur.
 */
function creerFormulaireEvaluation() {
  var form = FormApp.create(TITRE);
  form.setTitle(TITRE);
  form.setDescription(DESCRIPTION);
  form.setProgressBar(true);
  form.setAllowResponseEdits(false);
  form.setCollectEmail(false);
  form.setConfirmationMessage(MESSAGE_FINAL);

  // ======================================================= SECTION 1 (page 1)
  // La page 1 est implicite : pas de saut de page à créer.

  form.addSectionHeaderItem()
    .setTitle("SECTION 1 : Informations sur l'évaluateur");

  form.addDateItem()
    .setTitle("Date de l'évaluation")
    .setIncludesYear(true)
    .setRequired(true);

  form.addTextItem()
    .setTitle("Votre nom (facultatif)")
    .setHelpText("Cette question est facultative.")
    .setRequired(false);

  // Question de branchement n° 1 : doit être la DERNIÈRE de sa page.
  var qRole = form.addMultipleChoiceItem()
    .setTitle("Votre rôle / profession")
    .setRequired(true);

  // ------------------------------------------------- page « Autre profession »
  var pageAutre = form.addPageBreakItem()
    .setTitle("Précision sur votre profession");

  form.addTextItem()
    .setTitle("Autre profession")
    .setRequired(true);

  // ------------------------------------------------- page « Section 1 (suite) »
  var pageSuite1 = form.addPageBreakItem()
    .setTitle("SECTION 1 : Informations sur l'évaluateur (suite)");

  choixUnique(form, "Comment avez-vous accédé à l'application ?",
    ["Ordinateur", "Tablette", "Smartphone"], true);

  // Question de branchement n° 2 : dernière de sa page.
  var qPremiere = form.addMultipleChoiceItem()
    .setTitle("Est-ce votre première utilisation de l'application ?")
    .setRequired(true);

  // ------------------------------------------------- page « Fréquence »
  var pageFrequence = form.addPageBreakItem()
    .setTitle("Fréquence d'utilisation");

  choixUnique(form, "Combien de fois l'avez-vous utilisée auparavant ?",
    ["2 à 3 fois", "4 à 5 fois", "Plus de 5 fois"], false);

  // ======================================================= SECTION 2
  var pageSection2 = form.addPageBreakItem()
    .setTitle("SECTION 2 : Première impression et interface")
    .setHelpText(INTRO_LIKERT);

  likert(form, "L'interface est attrayante et bien conçue");
  likert(form, "L'application est facile à naviguer");
  likert(form, "Les menus et les boutons sont clairement libellés");
  likert(form, "L'application se charge rapidement");
  likert(form, "L'application fonctionne bien sur mon appareil");

  // ======================================================= SECTION 3
  form.addPageBreakItem()
    .setTitle("SECTION 3 : Fonctionnalités et performances");

  choixMultiple(form, "Quelles fonctionnalités avez-vous testées ?", [
    "Collecte (scraping) de données",
    "Téléchargement",
    "Remplissage du formulaire",
    "Tableau de bord des données"
  ], true);

  form.addSectionHeaderItem().setTitle(INTRO_LIKERT);

  likert(form, "Les fonctionnalités répondent à mes besoins");
  likert(form, "Les fonctionnalités sont faciles à utiliser");
  likert(form, "Les résultats fournis sont précis");
  likert(form, "L'application m'aide à accomplir mes tâches efficacement");
  likert(form, "Les instructions et l'aide sont claires et utiles");

  // ======================================================= SECTION 4
  form.addPageBreakItem().setTitle("SECTION 4 : Problèmes rencontrés");

  // Question de branchement n° 3 : seule question de sa page.
  var qProblemes = form.addMultipleChoiceItem()
    .setTitle("Avez-vous rencontré des problèmes ou des erreurs ?")
    .setRequired(true);

  // ------------------------------------------------- page « Détail problèmes »
  var pageProblemes = form.addPageBreakItem()
    .setTitle("SECTION 4 : Détail des problèmes rencontrés");

  choixMultiple(form, "Quel(s) type(s) de problème(s) ?", [
    "Erreur de chargement",
    "Problème d'affichage",
    "Fonctionnalité non fonctionnelle",
    "Perte de données",
    "Performance lente",
    "Interface confuse",
    "Autre"
  ], false);

  texteLong(form, "Veuillez décrire le(s) problème(s) en détail", false);

  // ======================================================= SECTION 5
  var pageSection5 = form.addPageBreakItem()
    .setTitle("SECTION 5 : Satisfaction globale");

  form.addScaleItem()
    .setTitle("Note globale de l'application")
    .setBounds(0, 10)
    .setLabels("0 — Très insatisfait", "10 — Très satisfait")
    .setRequired(true);

  form.addSectionHeaderItem()
    .setTitle("Niveau de satisfaction")
    .setHelpText(
      "Champ calculé automatiquement à partir de la note globale : " +
      "9-10 = Excellent · 7-8 = Très bon · 5-6 = Bon · 3-4 = Passable · " +
      "0-2 = Médiocre.");

  choixUnique(form, "Recommanderiez-vous cette application ?", [
    "Oui, sans hésiter",
    "Oui, probablement",
    "Peut-être",
    "Probablement pas",
    "Non"
  ], true);

  choixUnique(form, "Utiliseriez-vous cette application à nouveau ?", [
    "Oui, régulièrement",
    "Oui, occasionnellement",
    "Peut-être",
    "Probablement pas",
    "Non"
  ], true);

  // ======================================================= SECTION 6
  form.addPageBreakItem().setTitle("SECTION 6 : Suggestions d'amélioration");

  texteLong(form, "Quels sont les principaux points forts de cette application ?", true);
  texteLong(form, "Qu'est-ce qui pourrait être amélioré ?", true);
  texteLong(form, "Quelles fonctionnalités manquantes aimeriez-vous voir ajoutées ?", false);
  texteLong(form, "Commentaires ou suggestions supplémentaires", false);

  // ============================================== LOGIQUES CONDITIONNELLES
  // Les sauts de page existent tous : on peut définir les branchements.

  // Si « Votre rôle » = Autre  →  page « Autre profession », sinon page suivante.
  qRole.setChoices([
    qRole.createChoice("Étudiant", pageSuite1),
    qRole.createChoice("Enseignant", pageSuite1),
    qRole.createChoice("Chercheur", pageSuite1),
    qRole.createChoice("Analyste de données", pageSuite1),
    qRole.createChoice("Développeur", pageSuite1),
    qRole.createChoice("Chef de projet", pageSuite1),
    qRole.createChoice("Autre", pageAutre)
  ]);
  // Après « Autre profession », on rejoint la suite de la section 1.
  pageAutre.setGoToPage(pageSuite1);

  // Si « première utilisation » = Non  →  page « Fréquence », sinon section 2.
  qPremiere.setChoices([
    qPremiere.createChoice("Oui", pageSection2),
    qPremiere.createChoice("Non", pageFrequence)
  ]);
  pageFrequence.setGoToPage(pageSection2);

  // Si « problèmes rencontrés » = Oui  →  page détail, sinon section 5.
  qProblemes.setChoices([
    qProblemes.createChoice("Oui", pageProblemes),
    qProblemes.createChoice("Non", pageSection5)
  ]);
  pageProblemes.setGoToPage(pageSection5);

  // ============================================== liens à récupérer
  Logger.log("Lien d'édition  : " + form.getEditUrl());
  Logger.log("Lien public     : " + form.getPublishedUrl());
  Logger.log("Lien court      : " + form.shortenFormUrl(form.getPublishedUrl()));
  return form.getPublishedUrl();
}

// ---------------------------------------------------------------- utilitaires
// Fonctions appelées par creerFormulaireEvaluation() — ne pas exécuter seules.

/** Ajoute une question à choix unique (boutons radio). */
function choixUnique(form, titre, options, obligatoire) {
  var item = form.addMultipleChoiceItem()
    .setTitle(titre)
    .setChoiceValues(options)
    .setRequired(obligatoire);
  return item;
}

/** Ajoute une question Likert (choix unique sur l'échelle en 5 points). */
function likert(form, titre) {
  return choixUnique(form, titre, LIKERT, true);
}

/** Ajoute une question à choix multiples (cases à cocher). */
function choixMultiple(form, titre, options, obligatoire) {
  return form.addCheckboxItem()
    .setTitle(titre)
    .setChoiceValues(options)
    .setRequired(obligatoire);
}

/** Ajoute une question texte long (paragraphe). */
function texteLong(form, titre, obligatoire) {
  return form.addParagraphTextItem()
    .setTitle(titre)
    .setRequired(obligatoire);
}

/**
 * Retrouve le lien public du formulaire déjà créé (si le journal d'exécution
 * a été perdu). À exécuter depuis le même projet Apps Script.
 * NB : le lien à utiliser est celui en `docs.google.com/forms/d/e/.../viewform`
 * — surtout PAS une URL `script.google.com/macros/s/.../dev`, qui est une
 * URL de déploiement du script et non le formulaire.
 */
function retrouverLienFormulaire() {
  var fichiers = DriveApp.getFilesByName(TITRE);
  var trouve = false;
  while (fichiers.hasNext()) {
    var f = fichiers.next();
    if (f.getMimeType() !== MimeType.GOOGLE_FORMS) continue;
    var form = FormApp.openById(f.getId());
    Logger.log("Formulaire      : " + form.getTitle());
    Logger.log("Lien d'édition  : " + form.getEditUrl());
    Logger.log("Lien public     : " + form.getPublishedUrl());
    trouve = true;
  }
  if (!trouve) {
    Logger.log("Aucun formulaire « " + TITRE + " » trouvé dans le Drive. " +
               "Exécuter d'abord creerFormulaireEvaluation().");
  }
}

/**
 * ============================================================================
 *  OPTIONNEL — reproduction du champ calculé « Niveau de satisfaction »
 * ============================================================================
 *  Google Forms n'ayant pas de type « Calcul », le niveau est calculé à la
 *  réception de chaque réponse et écrit dans la feuille de réponses.
 *
 *  Mode d'emploi :
 *   1. Dans le formulaire : onglet « Réponses » → icône Sheets → créer la
 *      feuille de réponses liée.
 *   2. Ouvrir cette feuille → Extensions → Apps Script, y coller les deux
 *      fonctions ci-dessous.
 *   3. Exécuter `installerCalculNiveauSatisfaction` UNE SEULE FOIS
 *      (elle installe le déclencheur « à l'envoi du formulaire »).
 *
 *  Équivalent en formule de feuille de calcul (colonne libre) :
 *    =SI(B2>=9;"Excellent";SI(B2>=7;"Très bon";SI(B2>=5;"Bon";
 *      SI(B2>=3;"Passable";"Médiocre"))))
 *  où B2 est la cellule contenant la note globale.
 */
function installerCalculNiveauSatisfaction() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  ScriptApp.newTrigger("majNiveauSatisfaction")
    .forSpreadsheet(ss)
    .onFormSubmit()
    .create();
  Logger.log("Déclencheur installé.");
}

function majNiveauSatisfaction(e) {
  var feuille = e.range.getSheet();
  var ligne = e.range.getRow();
  var entetes = feuille.getRange(1, 1, 1, feuille.getLastColumn()).getValues()[0];

  var colNote = entetes.indexOf("Note globale de l'application") + 1;
  var colNiveau = entetes.indexOf("Niveau de satisfaction") + 1;
  if (colNote === 0) return;

  // Crée la colonne de résultat si elle n'existe pas encore.
  if (colNiveau === 0) {
    colNiveau = feuille.getLastColumn() + 1;
    feuille.getRange(1, colNiveau).setValue("Niveau de satisfaction");
  }

  var rating = Number(feuille.getRange(ligne, colNote).getValue());
  var niveau =
    rating >= 9 ? "Excellent" :
    rating >= 7 ? "Très bon" :
    rating >= 5 ? "Bon" :
    rating >= 3 ? "Passable" : "Médiocre";

  feuille.getRange(ligne, colNiveau).setValue(niveau);
}

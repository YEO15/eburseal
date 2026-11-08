"""Cahier des charges EburSeal."""
import sys, pathlib
from vmpdf import Doc, W
import data as D

HERE = pathlib.Path(__file__).parent
out = sys.argv[1] if len(sys.argv) > 1 else str(HERE.parent / "cahier-des-charges.pdf")
d = Doc(out, "Cahier des charges", "Application PWA/SPA — Jakarta EE 11 · WildFly 42 · Java 25", D.VERSION, "cdc")

d.cover([
    ("Projet", "EburSeal — plateforme de délivrance et de vérification de diplômes infalsifiables (Côte d'Ivoire)"),
    ("Équipe (binôme)", D.TEAM),
    ("Formation", "SUP'COM — 3<super>e</super> année cycle ingénieur, option Cybersecurity and Defense (CySeD)"),
    ("Module / encadrant", "Sécurité Applicative — Dr. Ing. Mohamed-Becha Kaâniche"),
    ("Document compagnon", "Recueil des besoins fonctionnels et de sécurité (SRE) — docs/recueil-des-besoins.pdf"),
    ("Version / date", f"v{D.VERSION} — {D.DATE}"),
], [[D.VERSION, D.DATE, "O. Yacouba, Y. T. Daouda", "Version initiale remise à la séance 2 (spécification &amp; conception)"]])
d.h1_break = False

# =====================================================================
d.H1("Présentation du projet", newpage=True)
d.H2("Cadre de l'atelier")
d.P("Ce cahier des charges est réalisé dans le cadre de l'atelier du module <b>Sécurité Applicative</b>. Chaque équipe conçoit puis développe une application "
    "<b>PWA/SPA</b> dont la partie serveur repose sur <b>Jakarta EE 11</b> (serveur <b>WildFly 42</b>, <b>Java 25</b>). L'énoncé impose trois contraintes :")
d.L(["le métier doit faire <b>la part belle aux services de dissimulation de l'information</b> : stéganographie, watermarking, fingerprinting ;",
     "le périmètre métier est <b>proportionnel à l'effectif</b> de l'équipe, alors que les exigences de sécurité sont <b>identiques pour toutes les équipes</b> ;",
     "les aspects de sécurité <b>suivent l'agenda du cours</b> (chapitres 2 à 7) : l'application s'enrichit au fil des séances."])
d.P("La progression est suivie sur un dépôt <b>GitHub privé</b>, partagé avec l'encadrant. Ce document et le recueil des besoins sont déposés en PDF dans le répertoire <b>docs/</b>.")
d.H2("Équipe")
d.P("Le binôme est composé de <b>OUATTARA Yacouba</b> et <b>YEO Tanna Daouda</b>. Les responsabilités sont <b>partagées</b> : chaque membre intervient sur le socle de sécurité, "
    "le moteur de dissimulation et l'application cliente. La seule règle d'organisation est la <b>revue croisée</b> : aucune contribution n'est fusionnée sans avoir été relue "
    "et approuvée par l'autre membre (inspection par les pairs, étape 9 de SQUARE).")

# =====================================================================
d.H1("Contexte et problématique")
d.H2("Le problème : la confiance dans les diplômes")
d.P("En Côte d'Ivoire, la fraude aux diplômes est un problème public et récurrent. En 2025, 84 agents des Douanes ont été condamnés pour usage de faux diplômes. "
    "Des étudiants d'écoles de formation ont été exclus pour la même raison, et les concours de la fonction publique signalent chaque année des candidats porteurs de faux diplômes. "
    "Aujourd'hui, vérifier un diplôme suppose de contacter l'établissement émetteur : c'est lent, rarement fait, et impossible à grande échelle.")
d.P("EburSeal répond à <b>un seul problème</b> : <b>permettre à quiconque de savoir, en quelques secondes, si un diplôme ivoirien est authentique, intact et présenté par son vrai titulaire.</b> "
    "Ce problème recouvre trois fraudes distinctes, et chacune des trois techniques de dissimulation de l'énoncé en traite une :")
d.table([["Fraude", "Exemple", "Technique", "Ce qu'elle prouve"],
         ["<b>Le faux complet</b>", "Diplôme fabriqué de toutes pièces", "<b>Watermarking</b> : filigrane invisible lié à la clé de l'établissement", "<b>Qui</b> a émis le diplôme"],
         ["<b>Le vrai diplôme retouché</b>", "Mention, niveau ou année modifiés sur une copie authentique", "<b>Stéganographie</b> : les données officielles signées sont cachées dans le document", "<b>Ce qui</b> a été émis"],
         ["<b>Le diplôme usurpé</b>", "Copie authentique d'un autre présentée comme la sienne", "<b>Fingerprinting</b> : chaque copie partagée porte une empreinte propre à son destinataire", "<b>À qui</b> la copie a été remise"]],
        [3.4, 4.6, 5.8, 3.6])
d.box("le nom <b>EburSeal</b> associe <i>ebur</i>, « ivoire » en latin (racine d'« Éburnie », nom poétique de la Côte d'Ivoire), et <i>seal</i>, le sceau. "
      "Littéralement : <b>le sceau de l'Ivoire</b>, un sceau que l'on ne voit pas mais que l'on peut toujours vérifier.", "Le nom", kind="info")
d.H2("Les trois techniques, et pourquoi elles sont complémentaires")
d.table([["Critère", "Watermarking (filigrane)", "Stéganographie (sceau caché)", "Fingerprinting (empreinte)"],
         ["Ce qui est inséré", "Une marque de l'établissement, identique sur tous ses diplômes", "Les données officielles du diplôme, signées et chiffrées", "Un code aléatoire différent pour chaque copie"],
         ["Propriété recherchée", "Robustesse + infalsifiabilité (clé secrète)", "Dissimulation + intégrité (signature)", "Robustesse + unicité"],
         ["Ce qu'un fraudeur ignore", "La clé de l'établissement", "L'existence et l'emplacement du sceau", "Le code de sa copie et sa position"],
         ["Moteur", "DCT 8×8, blocs réservés à la couche filigrane", "DCT 8×8, blocs réservés au sceau", "DCT 8×8, blocs réservés à l'empreinte"],
         ["Question à laquelle elle répond", "« Cet établissement a-t-il émis ce document ? »", "« Le contenu a-t-il été modifié ? »", "« Cette copie m'était-elle destinée ? »"]],
        [3.3, 4.7, 4.7, 4.7])
d.P("Les trois couches partagent <b>un seul moteur</b> (transformée en cosinus discrète par blocs 8×8, comme JPEG) mais occupent des <b>ensembles de blocs disjoints</b> tirés au sort par une clé secrète. "
    "C'est ce qui rend le projet réalisable par un binôme : un seul moteur à maîtriser, trois usages.")

# =====================================================================
d.H1("Objectifs")
d.H2("Objectifs métier")
d.table([["Code", "Objectif", "Indicateur de réussite"],
         ["OM-1", "Permettre à un établissement validé d'émettre des diplômes infalsifiables", "Émission d'un diplôme en moins de 15 s, double validation, certificat signé"],
         ["OM-2", "Permettre à quiconque de vérifier un diplôme à partir du seul document", "Verdict en moins de 10 s ; marques lisibles après JPEG qualité 75 et redimensionnement à 75 %"],
         ["OM-3", "Détecter les copies présentées hors de leur contexte", "Alerte au vérificateur et au titulaire ; zéro fausse accusation sur le banc de test"],
         ["OM-4", "Offrir une application installable, simple sur mobile", "PWA installable ; vérification en 3 écrans maximum"]],
        [1.5, 8.6, 7.3])
d.H2("Objectifs de sécurité (repris de l'énoncé)")
d.table([["Principe imposé", "Traduction dans EburSeal"],
         ["<b>Shift-Left</b>", f"{len(D.SEC)} exigences de sécurité rédigées <b>avant</b> la première ligne de code métier ; chaque fonctionnalité a ses cas d'abus avant d'être développée"],
         ["<b>Perspective de l'attaquant</b>", f"{len(D.ABUSE)} cas d'abus, {len(D.MIS_ACTORS)} profils d'attaquants (faussaire, titulaire fraudeur, imposteur, agent corrompu…), 2 arbres d'attaque, analyse STRIDE"],
         ["<b>Triptyque C-I-D</b>", f"Besoins C-I-D cotés pour chacun des {len(D.ASSETS)} actifs ; l'<b>intégrité</b> du registre et des documents est la propriété dominante"],
         ["<b>Pas de listes génériques</b>", "Exigences chiffrées et propres au métier, ex. « un diplôme n'est émis qu'après validation par un responsable différent du préparateur » plutôt que « contrôler les accès »"]],
        [4.6, 12.8])

# =====================================================================
d.H1("Périmètre")
d.H2("Inclus dans le projet")
d.table([["Module", "Contenu", "Besoins"],
         ["Socle", "Comptes, activation par invitation, MFA, données personnelles", "BF-CPT-01 à 05"],
         ["Établissement", "Inscription et validation des établissements, gestion des agents", "BF-ETB-01, 02"],
         ["Émission", "Préparation, double validation, émission unitaire et par lot, révocation", "BF-EMI-01 à 04"],
         ["Watermarking", "Filigrane invisible de l'établissement, mention visible, certificat d'émission", "BF-WM-01 à 03"],
         ["Stéganographie", "Sceau caché signé, comparaison affiché/officiel, vérification autoportée", "BF-STG-01 à 03"],
         ["Fingerprinting", "Copies traçables, copie personnelle, détection hors contexte, gestion des partages", "BF-FP-01 à 04"],
         ["Vérification", "Vérification publique, espace vérificateur, rapport signé", "BF-VER-01 à 03"],
         ["Administration / PWA", "Validation des acteurs, quotas, audit ; application installable", "BF-ADM-01 à 03, BF-PWA-01, 02"]],
        [3.6, 9.6, 4.2])
d.H2("Proportionnalité au binôme")
d.P("Le métier est proportionné à un binôme ; un trinôme irait plus loin sur les points ci-dessous. Les exigences de sécurité restent <b>complètes</b>.")
d.table([["Dimension", "Binôme (EburSeal v1)", "Trinôme (référence, non retenu)"],
         ["Supports", "Diplômes numériques : PDF d'une page et images (PNG, JPEG)", "Idem + diplômes papier imprimés puis photographiés (robustesse impression–numérisation)"],
         ["Vérification du contenu", "Données officielles du sceau affichées <b>à côté</b> du document ; comparaison par le vérificateur", "Comparaison automatique par OCR"],
         ["Fingerprinting", "Code de 64 bits par copie, code correcteur, ≤ 30 partages par diplôme", "Codes anti-collusion (Tardos) résistant à la comparaison de plusieurs copies"],
         ["Établissements", "Clés gérées par la plateforme (coffre chiffré)", "Clés détenues par l'établissement (HSM / carte à puce)"],
         ["Sécurité", f"<b>Ensemble complet des {len(D.SEC)} exigences</b>", "<b>Identique</b>"]],
        [3.2, 7.1, 7.1])
d.H2("Exclu du périmètre")
d.L(["diplômes <b>papier</b> photographiés : la robustesse à l'impression puis à la photographie relève de la recherche ; elle est reportée ;",
     "résistance des empreintes à la <b>collusion</b> de plusieurs destinataires (limite assumée, cf. SR-DIM-06) ;",
     "rattachement du compte titulaire à l'identité numérique nationale (NNI) : évolution envisagée après le module ;",
     "diplômes émis <b>avant</b> l'adhésion d'un établissement : seuls les diplômes émis via EburSeal sont vérifiables ;",
     "vérificateur qui ne vérifie pas : traité par la sensibilisation, pas par l'application."])

# =====================================================================
d.H1("Acteurs et rôles")
d.table([["Acteur", "Description", "Ce qu'il peut faire"]] + [list(a) for a in D.ACTORS], [3.0, 5.0, 9.4])
d.P("La matrice ci-dessous fixe les droits par défaut. Toute case vide est un <b>refus</b> (refus par défaut, SR-AUZ-01).")
X = "✔"
d.table([["Fonction", "Visit.", "Titul.", "Agent", "Resp.", "Vérif.", "Admin", "Audit."],
         ["Vérification publique", X, X, X, X, X, X, X],
         ["Portefeuille, copie personnelle, partages", "", "✔ (les siens)", "", "", "", "", ""],
         ["Préparer un diplôme", "", "", "✔ (son étab.)", "✔ (son étab.)", "", "", ""],
         ["Valider / émettre / révoquer", "", "", "", "✔ (≠ préparateur)", "", "", ""],
         ["Recevoir des copies, vérifier avec contrôle du destinataire", "", "", "", "", X, "", ""],
         ["Valider établissements et vérificateurs, quotas", "", "", "", "", "", "✔ (MFA)", ""],
         ["Créer, modifier ou réactiver un diplôme", "", "", "", "", "", "<b>✘</b>", "<b>✘</b>"],
         ["Consulter journaux et alertes", "", "Son historique", "", "", "", "", "✔ lecture (MFA)"],
         ["Modifier / supprimer un journal", "", "", "", "", "", "<b>✘</b>", "<b>✘</b>"]],
        [5.6, 1.3, 1.9, 1.9, 2.1, 1.4, 1.6, 1.6], small=True)

# =====================================================================
d.H1("Description fonctionnelle")
d.P(f"La liste détaillée des {len(D.FUNC)} besoins fonctionnels, avec priorités MoSCoW et critères d'acceptation, figure dans le recueil des besoins (§ 3). En voici la synthèse par module.")
INTRO = {
    "Socle": "Les comptes ne sont pas ouverts librement : un titulaire est <b>invité</b> par son établissement, un vérificateur est <b>validé</b> par l'administrateur.",
    "Établissement": "Un établissement n'émet rien tant qu'il n'a pas été validé ; à la validation, la plateforme génère ses clés de filigrane et de signature.",
    "Émission": "L'émission suit le principe des « quatre yeux » : l'agent prépare, un responsable différent valide. C'est la parade principale au diplôme de complaisance.",
    "Watermarking": "Chaque diplôme émis reçoit le filigrane invisible de son établissement et un certificat d'émission signé.",
    "Stéganographie": "Le sceau caché transporte les données officielles signées : le document porte sa propre preuve, vérifiable même sans le registre.",
    "Fingerprinting": "Aucun fichier non marqué ne sort de la plateforme : chaque copie, y compris celle du titulaire, porte une empreinte unique.",
    "Vérification": "La vérification part toujours du <b>document</b>, jamais d'une recherche par nom ou numéro, ce qui protège les données des titulaires.",
    "Administration": "L'administration gère la plateforme sans pouvoir toucher aux diplômes ; l'audit est confié à un rôle distinct.",
    "PWA": "L'application s'installe sur mobile ; hors ligne, seule l'interface est disponible.",
}
for mod in D.MODULES:
    d.H3(f"Module {mod}")
    d.P(INTRO[mod])
    d.table([["ID", "Fonctionnalité", "Prio"]] + [[f[0], f"<b>{f[2]}</b> — {f[3]}", f[4]] for f in D.FUNC if f[1] == mod], [2.2, 14.0, 1.2])
d.H2("Scénario nominal : de l'émission à la vérification")
d.L(["L'agent de scolarité de l'établissement saisit les données du diplôme d'Awa et dépose le visuel (PDF) (BF-EMI-01).",
     "Le directeur des études, connecté avec son second facteur, relit et valide (BF-EMI-02, SR-AUZ-03). La plateforme rastérise le PDF à 300 dpi, insère le filigrane, le sceau caché et produit le certificat signé.",
     "Awa reçoit une invitation, active son compte et retrouve son diplôme dans son portefeuille (BF-CPT-01).",
     "Pour une candidature, Awa partage une copie avec l'organisation « Orange CI », finalité « candidature », valable 60 jours (BF-FP-01).",
     "Le recruteur vérifie la copie depuis son espace : établissement authentique, données officielles affichées à côté du document, copie bien destinée à son organisation (BF-VER-02).",
     "Si la même copie est présentée plus tard à une autre organisation, la vérification l'indique et Awa est alertée (BF-FP-03, SR-DIM-10)."])

# =====================================================================
d.H1("Exigences non fonctionnelles (hors sécurité)")
d.table([["Code", "Domaine", "Exigence"],
         ["ENF-01", "Performance", "Émission d'un diplôme A4 (300 dpi) en moins de 15 s ; vérification en moins de 10 s (serveur 4 vCPU)"],
         ["ENF-02", "Performance", "Écrans de navigation en moins de 500 ms au 95<super>e</super> centile"],
         ["ENF-03", "Qualité d'image", "Marques imperceptibles : PSNR ≥ 40 dB par rapport au visuel déposé"],
         ["ENF-04", "Robustesse", "Marques lisibles après JPEG qualité 75 et redimensionnement à 75 % (seuils validés par prototype au jalon J2)"],
         ["ENF-05", "Compatibilité", "Deux dernières versions de Chrome, Firefox, Edge, Safari ; de 360 px à 1920 px de large ; connexions mobiles lentes (3G)"],
         ["ENF-06", "Ergonomie", "Interface en français ; contraste WCAG 2.1 AA ; verdict compréhensible par un non-spécialiste (couleur + texte)"],
         ["ENF-07", "Maintenabilité", "Couverture de tests ≥ 70 % sur les services métier et 90 % sur le moteur ; API documentée en OpenAPI 3.1"]],
        [1.7, 3.0, 12.7])

# =====================================================================
d.H1("Contraintes techniques et architecture")
d.H2("Socle technique")
d.table([["Couche", "Technologie", "Usage dans EburSeal"],
         ["Langage / JVM", "<b>Java 25</b> (LTS)", "Back-end ; ImageIO ; EdDSA (Ed25519) natif pour signatures et certificats"],
         ["Serveur d'application", "<b>WildFly 42</b>", "Déploiement du WAR, Elytron (sécurité, credential store), Undertow (HTTP/TLS)"],
         ["Plateforme", "<b>Jakarta EE 11</b>", "REST 4.0 (API), CDI 4.1 (services), Persistence 3.2 + Data 1.0 (dépôts à requêtes paramétrées), Validation 3.1, Security 4.0, Concurrency 3.1, JSON Binding 3.0"],
         ["Documents", "Apache PDFBox", "Rastérisation des PDF déposés et production des diplômes émis"],
         ["Cryptographie", "JCA + Bouncy Castle", "AES-256-GCM, Argon2id, Ed25519, ES256 (JWT)"],
         ["Base de données", "PostgreSQL 17", "Registre, partages, clés chiffrées"],
         ["Client", "SPA React 19 + TypeScript, Vite, vite-plugin-pwa", "Espaces titulaire, émetteur, vérificateur ; Service Worker"],
         ["Intégration continue", "GitHub Actions", "Build, tests, SAST, SCA, recherche de secrets"]],
        [3.3, 4.2, 9.9])
d.H2("Architecture cible")
d.P("L'architecture est en trois couches. Le <b>moteur EburSeal</b> concentre la dissimulation ; il s'exécute dans une file de traitement bornée. Les clés ne quittent jamais le serveur.")
d.img(str(HERE / "diagrams" / "architecture.png"), W, "Figure 1 — Architecture logique d'EburSeal")
d.H2("Principales ressources de l'API REST")
d.table([["Ressource", "Méthodes", "Rôles autorisés", "Besoins"],
         ["/api/auth/{activate, login, refresh, logout, reset, mfa}", "POST", "Public / authentifié", "BF-CPT-01 à 04"],
         ["/api/institutions, …/{id}/agents", "GET, POST, PUT", "Administrateur, Responsable (son établissement)", "BF-ETB-01, 02"],
         ["/api/diplomas, …/{id}/validate, …/{id}/revoke, /api/batches", "GET, POST", "Agent, Responsable (son établissement)", "BF-EMI-01 à 04"],
         ["/api/wallet, /api/wallet/{id}/copy", "GET", "Titulaire (les siens)", "BF-FP-02"],
         ["/api/shares, /api/shares/{id}", "GET, POST, DELETE", "Titulaire (les siens)", "BF-FP-01, 04"],
         ["/api/verify", "POST", "Public (10/h/IP) ou Vérificateur", "BF-VER-01, 02"],
         ["/api/inbox, /api/reports/{id}", "GET", "Vérificateur (son organisation)", "BF-VER-02, 03"],
         ["/api/admin/**, /api/audit/**", "GET, PUT", "Administrateur / Auditeur (MFA)", "BF-ADM-01 à 03"]],
        [6.6, 2.2, 5.4, 3.2], small=True)

# =====================================================================
d.H1("Démarche de sécurité et feuille de route")
d.P("La sécurité suit l'agenda du cours. Toutes les exigences sont spécifiées dès la séance 2 (Shift-Left), puis le code les rejoint chapitre après chapitre.")
d.table([["Chapitre du cours", "Livrable dans EburSeal", "Exigences visées"],
         ["Ch. 2 — Spécification &amp; conception", "Cahier des charges, recueil (SQUARE), cas d'abus, arbres d'attaque, STRIDE, squelette du dépôt + test SR-AUZ-01, <b>prototype du moteur</b>", "Toutes (spécifiées)"],
         ["Ch. 3 — Confidentialité, intégrité, disponibilité", "Moteur DCT (filigrane, sceau, empreinte), signatures, chiffrement au repos, validation et rastérisation des fichiers, quotas", "CON, INT, NRP, DIM, DIS"],
         ["Ch. 4 — Authentification, autorisation, vie privée", "Comptes, Argon2id, TOTP, JWT, RBAC, double validation, rattachement à l'établissement, minimisation", "AUT, AUZ, PRV"],
         ["Ch. 5 — Journalisation &amp; erreurs", "Journal d'audit chaîné, alertes de volume, ExceptionMapper RFC 9457", "LOG, ERR"],
         ["Ch. 6 — Tests de sécurité", "SAST, SCA, DAST (ZAP), tests d'abus, banc de robustesse", "TST"],
         ["Ch. 7 — Déploiement &amp; maintenance", "WildFly durci, conteneurs non root, en-têtes, sauvegardes, rotation des clés", "DEP, DIS-04"]],
        [4.4, 9.2, 3.8])
d.box("le recueil des besoins est versionné et mis à jour à chaque séance (phase de <b>gestion des exigences</b>). Toute évolution passe par une issue GitHub et une pull request relue.",
      "Évolution", kind="info")

# =====================================================================
d.H1("Organisation, livrables et planning")
d.H2("Organisation du dépôt GitHub")
d.table([["Élément", "Convention"],
         ["Visibilité", "Dépôt <b>privé</b>, accès accordé à l'encadrant ; tous droits réservés aux auteurs"],
         ["Arborescence", "backend/ (WAR Jakarta EE 11) · frontend/ (PWA) · docs/ (PDF + sources) · .github/ (CI, modèles d'issues et de PR)"],
         ["Branches", "<b>main</b> protégée (release, tag par séance) · <b>develop</b> (intégration) · feature/&lt;id-besoin&gt;-&lt;description&gt;"],
         ["Pull requests", "Relecture obligatoire par l'autre membre ; liste de contrôle sécurité ; CI verte obligatoire"],
         ["Backlog", "Issues <b>feature</b> (BF-…), <b>abuse-story</b> (CA-…), <b>security-story</b> (SR-…), étiquetées par chapitre (ch2 … ch7)"],
         ["Traçabilité", "Chaque commit et PR citent l'identifiant du besoin (ex. « SR-AUZ-03 : double validation de l'émission »)"]],
        [3.2, 14.2])
d.H2("Livrables")
d.table([["Livrable", "Emplacement", "Échéance"],
         ["Cahier des charges (ce document)", "docs/cahier-des-charges.pdf", "Séance 2"],
         ["Recueil des besoins fonctionnels et SRE", "docs/recueil-des-besoins.pdf", "Séance 2, mis à jour à chaque séance"],
         ["Référentiel des exigences (CSV)", "docs/exigences.csv", "Séance 2, mis à jour en continu"],
         ["Rapport du prototype du moteur (PSNR, robustesse)", "docs/rapports/prototype-moteur.pdf", "Séance 3"],
         ["Code source + pipeline CI", "backend/, frontend/, .github/", "Incrémental, séances 3 à 7"],
         ["Rapports de tests de sécurité", "docs/rapports/", "Séance 6"]],
        [6.4, 6.2, 4.8])
d.H2("Planning prévisionnel")
d.table([["Jalon", "Contenu", "Critère de passage (« gate »)"],
         ["J1 — Séance 2", "Spécification &amp; conception, squelette du dépôt", "Documents dans docs/ ; CI verte ; déploiement WildFly 42 du squelette"],
         ["J2 — Séance 3", "Prototype du moteur + intégrité / confidentialité", "PSNR ≥ 40 dB et marques lisibles après JPEG Q75 ; exigences INT/CON P1 testées"],
         ["J3 — Séance 4", "Comptes, MFA, RBAC, double validation ; émission", "Exigences AUT/AUZ P1 testées ; tests IDOR et auto-validation verts"],
         ["J4 — Séance 5", "Audit, alertes, erreurs ; partages et fingerprinting", "Chaîne d'audit vérifiée ; détection « hors contexte » démontrée"],
         ["J5 — Séance 6", "Campagne de tests de sécurité", f"0 alerte haute SAST/SCA/ZAP ; {len(D.ABUSE)}/{len(D.ABUSE)} cas d'abus couverts"],
         ["J6 — Séance 7", "Déploiement durci, démonstration", "Checklist DEP validée ; restauration testée"]],
        [3.0, 7.0, 7.4])

# =====================================================================
d.H1("Critères d'acceptation et « Definition of Done »")
d.P("Une fonctionnalité est considérée comme <b>terminée</b> seulement si :")
d.L(["ses critères d'acceptation (recueil, § 3) sont vérifiés par un test automatisé ;",
     "ses cas d'abus ont été rédigés <b>avant</b> le développement, et chacun est couvert par un test qui démontre l'échec de l'attaque (SR-TST-04) ;",
     "les exigences de sécurité qu'elle touche sont implémentées et vérifiées selon la méthode prévue ;",
     "la CI est verte : build, tests, SAST sans alerte haute, SCA sans CVSS ≥ 7, aucun secret détecté ;",
     "la pull request a été relue et approuvée par l'autre membre, et la matrice de traçabilité est à jour."])
d.H2("Risques projet")
d.table([["Risque projet", "Impact", "Parade"],
         ["Robustesse des marques DCT insuffisante après recompression", "OM-2 partiellement atteint", "Prototype dès J2 sur un banc de 50 diplômes ; redondance et code correcteur ajustables"],
         ["Capacité insuffisante pour trois couches sur un A4", "Sceau tronqué", "Rastérisation à 300 dpi (≈ 136 000 blocs) ; sceau compact (≈ 250 octets)"],
         ["Charge de travail (sécurité identique à un trinôme)", "Retard", "Priorisation AHP : P1 d'abord ; besoins « Could » abandonnables"],
         ["Évolution des exigences au fil du cours", "Incohérences documentaires", "Référentiel unique (data.py → PDF + CSV) régénéré à chaque évolution"]],
        [5.6, 3.6, 8.2])

d.build()
print("OK", out)

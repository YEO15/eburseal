"""Référentiel unique des besoins EburSeal (source de vérité pour les PDF et l'export CSV).

Toute évolution d'exigence (ajout, modification, passage en « Obsolète ») se fait ICI,
puis on régénère les documents avec build.sh : c'est la phase « gestion des exigences » de l'IES/SRE.
"""

APP = "EburSeal"
TAGLINE = "Le sceau invisible des diplômes ivoiriens"
VERSION = "1.0"
DATE = "08/11/2026"
TEAM = "OUATTARA Yacouba · YEO Tanna Daouda"

# --------------------------------------------------------------------------- acteurs
ACTORS = [
    ("Visiteur", "Toute personne, sans compte", "<b>Vérifier publiquement</b> un diplôme (authenticité, contenu officiel, statut), sans jamais voir le destinataire d'une copie"),
    ("Titulaire", "Diplômé, invité par son établissement", "Consulter son portefeuille de diplômes, télécharger sa copie personnelle, <b>partager des copies traçables</b>, voir qui a vérifié ses copies"),
    ("Agent émetteur", "Personnel de scolarité d'un établissement validé", "Saisir un diplôme, déposer son visuel, soumettre à validation"),
    ("Responsable émetteur", "Directeur des études / scolarité (MFA obligatoire)", "<b>Valider</b> l'émission préparée par un agent (double validation), révoquer un diplôme"),
    ("Vérificateur", "Organisation inscrite et validée (employeur, administration, école)", "Recevoir des copies partagées, vérifier avec contrôle du destinataire, télécharger un rapport de vérification"),
    ("Administrateur", "Exploitant de la plateforme (MFA obligatoire)", "Valider établissements et vérificateurs, gérer comptes et quotas — <b>sans pouvoir émettre ni modifier un diplôme</b>"),
    ("Auditeur", "Responsable sécurité (MFA obligatoire)", "Lecture seule des journaux d'audit, des alertes et de l'état de la chaîne d'intégrité"),
]
MIS_ACTORS = [
    ("Faussaire", "Fabrique de toutes pièces un diplôme d'apparence officielle (logiciel de retouche, imprimeur)"),
    ("Titulaire fraudeur", "Possède un vrai diplôme et en modifie le contenu (mention, intitulé, année)"),
    ("Imposteur", "Présente comme le sien le diplôme authentique d'une autre personne (copie récupérée, homonyme)"),
    ("Agent corrompu ou compromis", "Agent émetteur (ou compte d'agent volé) qui tente d'émettre un « vrai faux » diplôme de complaisance"),
    ("Destinataire indélicat", "Vérificateur qui laisse fuiter ou revend les dossiers de candidature reçus"),
    ("Attaquant externe", "Anonyme sur Internet : force brute, injection, collecte massive de données, déni de service"),
]

# --------------------------------------------------------------------------- besoins fonctionnels
# (id, module, intitulé, description, priorité MoSCoW, critère d'acceptation)
FUNC = [
    ("BF-CPT-01", "Socle", "Activer un compte", "Le titulaire active son compte depuis l'invitation envoyée par son établissement ; les vérificateurs créent un compte d'organisation soumis à validation.", "M",
     "Lien d'activation à usage unique valable 72 h ; compte vérificateur inactif tant qu'il n'est pas validé."),
    ("BF-CPT-02", "Socle", "Se connecter / se déconnecter", "Authentification par e-mail + mot de passe, puis second facteur si activé ou obligatoire pour le rôle.", "M",
     "Après déconnexion, l'ancien jeton est refusé (401)."),
    ("BF-CPT-03", "Socle", "Gérer le second facteur", "Activer un TOTP (application d'authentification) et obtenir des codes de secours.", "M",
     "QR code d'enrôlement + 10 codes de secours à usage unique."),
    ("BF-CPT-04", "Socle", "Réinitialiser le mot de passe", "Demande par e-mail, lien à usage unique.", "M",
     "Lien expiré après 15 min ou après première utilisation."),
    ("BF-CPT-05", "Socle", "Gérer ses données personnelles", "Le titulaire consulte et exporte ses données, et peut fermer son compte (les diplômes restent au registre de l'établissement).", "S",
     "Export JSON + copies personnelles en ZIP ; fermeture effective sous 30 jours."),
    ("BF-ETB-01", "Établissement", "Inscrire un établissement", "Demande d'inscription d'un établissement (pièces justificatives) ; validation par l'administrateur, qui génère ses clés.", "M",
     "Aucune émission possible avant validation ; clés de filigrane et de signature propres à l'établissement."),
    ("BF-ETB-02", "Établissement", "Gérer les agents", "Le responsable émetteur invite, suspend et retire les agents de son établissement.", "M",
     "Un agent n'est rattaché qu'à un seul établissement."),
    ("BF-EMI-01", "Émission", "Préparer un diplôme", "L'agent saisit les données officielles (titulaire, date de naissance, intitulé, spécialité, mention, session, numéro) et dépose le visuel du diplôme (PDF d'une page ou PNG).", "M",
     "Diplôme créé au statut « en attente de validation »."),
    ("BF-EMI-02", "Émission", "Valider et émettre", "Le responsable relit et valide ; la plateforme applique automatiquement le <b>filigrane</b>, le <b>sceau caché</b> et produit le <b>certificat d'émission</b> ; le titulaire est invité.", "M",
     "Le valideur est différent du préparateur ; diplôme émis en PDF et PNG en moins de 15 s."),
    ("BF-EMI-03", "Émission", "Émettre par lot", "Import d'un fichier CSV + visuels pour une promotion entière, puis validation groupée.", "S",
     "Lot de 200 diplômes traité en tâche de fond, avec rapport d'erreurs par ligne."),
    ("BF-EMI-04", "Émission", "Révoquer un diplôme", "Le responsable révoque un diplôme (erreur, fraude) avec motif ; une réémission corrigée est possible.", "M",
     "Toute vérification ultérieure affiche « révoqué » avec la date."),
    ("BF-WM-01", "Watermarking", "Filigrane de l'établissement", "Filigrane invisible, robuste, lié à la clé secrète de l'établissement, inséré dans le domaine DCT de chaque diplôme émis.", "M",
     "Invisible (PSNR ≥ 40 dB) ; détecté après JPEG qualité 75 et redimensionnement à 75 %."),
    ("BF-WM-02", "Watermarking", "Mention visible", "Mention visible discrète « Vérifiable sur EburSeal » et numéro court du diplôme.", "C",
     "Position et taille paramétrables par l'établissement."),
    ("BF-WM-03", "Watermarking", "Certificat d'émission", "Certificat signé par l'établissement : empreinte SHA-256 du document, données officielles, date d'émission.", "M",
     "Certificat JSON + PDF vérifiable avec la clé publique de l'établissement."),
    ("BF-STG-01", "Stéganographie", "Sceau caché", "Les données officielles signées sont <b>dissimulées dans le document lui-même</b> (domaine DCT, positions secrètes, code correcteur).", "M",
     "Sceau extrait intact après JPEG qualité 75 ; aucune trace visible."),
    ("BF-STG-02", "Stéganographie", "Comparer affiché / caché", "À la vérification, les données extraites du sceau sont affichées <b>à côté</b> du document pour que le vérificateur compare.", "M",
     "Écran « données officielles » + aperçu du document côte à côte."),
    ("BF-STG-03", "Stéganographie", "Vérification autoportée", "Le document se vérifie même si le diplôme n'est pas trouvé au registre (instance partenaire, base indisponible), grâce au sceau signé.", "S",
     "Résultat « authentique (vérification par sceau) » sans accès au registre."),
    ("BF-FP-01", "Fingerprinting", "Partager une copie traçable", "Le titulaire génère une copie pour un destinataire (organisation inscrite ou nom libre), une finalité et une durée de validité.", "M",
     "Chaque copie porte un code d'empreinte unique ; ≤ 30 partages actifs par diplôme."),
    ("BF-FP-02", "Fingerprinting", "Copie personnelle", "Tout téléchargement par le titulaire produit une copie empreintée à son nom ; l'original non marqué n'est jamais téléchargeable.", "M",
     "Aucun fichier sans empreinte ne sort de la plateforme."),
    ("BF-FP-03", "Fingerprinting", "Détecter une copie hors contexte", "Si une copie est vérifiée par une organisation qui n'en est pas le destinataire, ou après expiration, la vérification l'indique et le titulaire est alerté.", "M",
     "Alerte « copie émise pour un autre destinataire » + notification au titulaire."),
    ("BF-FP-04", "Fingerprinting", "Gérer ses partages", "Lister, révoquer un partage, consulter l'historique des vérifications de ses copies.", "S",
     "Une copie révoquée est signalée comme telle à toute vérification."),
    ("BF-VER-01", "Vérification", "Vérification publique", "Déposer un fichier (PDF, PNG, JPEG) et obtenir : établissement émetteur, authenticité, données officielles, statut.", "M",
     "Verdict « authentique / non authentique / indéterminé » en moins de 10 s."),
    ("BF-VER-02", "Vérification", "Espace vérificateur", "L'organisation reçoit les copies qui lui sont partagées et vérifie tout document avec contrôle du destinataire.", "M",
     "Boîte de réception des partages ; contrôle automatique « copie destinée à mon organisation »."),
    ("BF-VER-03", "Vérification", "Rapport de vérification", "Télécharger un rapport PDF signé de la vérification (date, résultat, identifiant de copie).", "S",
     "Rapport vérifiable avec la clé publique de la plateforme."),
    ("BF-ADM-01", "Administration", "Gérer la plateforme", "Valider établissements et vérificateurs, suspendre des comptes, attribuer les rôles plateforme.", "M",
     "Toute action d'administration est journalisée et exige le MFA."),
    ("BF-ADM-02", "Administration", "Gérer les quotas", "Quotas d'émission par établissement et de vérifications par vérificateur.", "S",
     "Dépassement → refus explicite (429) et événement journalisé."),
    ("BF-ADM-03", "Administration", "Consulter l'audit", "L'auditeur consulte et filtre journaux et alertes, et l'état de la chaîne d'intégrité.", "M",
     "Recherche par acteur, type d'événement, période ; export CSV."),
    ("BF-PWA-01", "PWA", "Application installable", "Manifest, icônes, Service Worker ; vérification utilisable sur mobile ; page hors ligne informative.", "M",
     "PWA installable ; aucune donnée privée disponible hors ligne."),
    ("BF-PWA-02", "PWA", "Notifications", "Notification dans l'application lors d'une vérification de ses copies ou d'une alerte.", "C",
     "Badge de compteur sur le tableau de bord du titulaire."),
]
MODULES = ["Socle", "Établissement", "Émission", "Watermarking", "Stéganographie", "Fingerprinting", "Vérification", "Administration", "PWA"]

# --------------------------------------------------------------------------- actifs (SQUARE étape 2)
ASSETS = [
    ("A1", "Registre des diplômes", "Données officielles émises par les établissements et leur statut (émis, révoqué)", 3, 4, 3),
    ("A2", "Clés cryptographiques", "Clés de filigrane et de signature des établissements, clé de position du sceau, clé maître", 4, 4, 3),
    ("A3", "Documents diplômes", "Visuels déposés, diplômes émis, copies empreintées", 3, 4, 3),
    ("A4", "Identifiants et sessions", "Mots de passe hachés, secrets TOTP, jetons", 4, 4, 3),
    ("A5", "Certificats d'émission", "Preuves signées de l'émission et de la révocation", 2, 4, 4),
    ("A6", "Table des partages", "Correspondance code d'empreinte ↔ titulaire, destinataire, finalité", 4, 4, 2),
    ("A7", "Journaux d'audit", "Traces des émissions, validations, révocations, vérifications", 3, 4, 3),
    ("A8", "Données personnelles des titulaires", "Nom, prénoms, date de naissance, parcours, historique des vérifications", 4, 3, 2),
    ("A9", "Service de vérification", "Disponibilité de la vérification, en particulier en période de recrutement", 1, 3, 4),
]

# --------------------------------------------------------------------------- cas d'abus
ABUSE = [
    dict(id="CA-01", nom="Faire accepter un faux diplôme", prio="Élevée", misactor="Faussaire",
         access="Aucun", entry="Document présenté à un recruteur, POST /api/verify", cia="I",
         soph="Moyenne", uc="Vérifier un diplôme",
         desc="Le faussaire fabrique un diplôme imitant parfaitement le modèle d'un établissement (logo, signatures scannées, mise en page) et espère qu'il passera la vérification ou que le recruteur ne vérifiera pas.",
         pre="Modèle visuel de l'établissement disponible (diplômes publiés sur les réseaux sociaux).", post="Recrutement ou admission sur la base d'un diplôme inexistant.",
         reco="Filigrane invisible lié à une clé secrète par établissement ; certificat signé ; verdict « non authentique » en l'absence de filigrane valide.",
         cs="CS-01", cs_name="Garantir l'origine du diplôme"),
    dict(id="CA-02", nom="Retoucher un diplôme authentique", prio="Élevée", misactor="Titulaire fraudeur",
         access="Titulaire (possède une copie)", entry="Copie personnelle téléchargée", cia="I",
         soph="Faible", uc="Vérifier un diplôme, Télécharger sa copie",
         desc="Le titulaire modifie sur sa copie la mention (Passable → Bien), le niveau (Licence → Master) ou l'année, en conservant le reste du document intact pour garder le filigrane.",
         pre="Disposer d'une copie authentique.", post="Avantage indu (poste, salaire, admission) obtenu avec un diplôme falsifié.",
         reco="Sceau caché signé contenant les données officielles ; affichage côte à côte affiché / officiel ; contrôle au registre.",
         cs="CS-02", cs_name="Garantir l'intégrité du contenu"),
    dict(id="CA-03", nom="Présenter le diplôme d'un autre", prio="Élevée", misactor="Imposteur, Destinataire indélicat",
         access="Aucun (copie récupérée)", entry="Copie partagée ayant fuité, POST /api/verify", cia="I, C",
         soph="Faible", uc="Partager une copie, Vérifier un diplôme",
         desc="L'imposteur récupère une copie authentique (dossier qui a fuité, homonyme) et la présente comme la sienne. Le diplôme est vrai ; c'est le porteur qui ment.",
         pre="Une copie a circulé en dehors de son destinataire.", post="Usurpation de l'identité académique d'autrui.",
         reco="Copie empreintée par destinataire ; contrôle « copie destinée à mon organisation » ; alerte au titulaire ; expiration des partages.",
         cs="CS-03", cs_name="Lier chaque copie à son destinataire"),
    dict(id="CA-04", nom="Émettre un diplôme de complaisance", prio="Élevée", misactor="Agent corrompu ou compromis",
         access="Agent émetteur", entry="POST /api/diplomas, /api/diplomas/{id}/validate", cia="I",
         soph="Moyenne", uc="Préparer un diplôme, Valider et émettre",
         desc="Un agent crée et fait émettre un diplôme pour une personne qui ne l'a pas obtenu (« vrai faux »), ou un attaquant utilise le compte volé d'un agent.",
         pre="Accès à un compte d'agent émetteur.", post="Diplôme cryptographiquement « authentique » mais frauduleux ; atteinte grave à la confiance dans la plateforme.",
         reco="Double validation par un responsable distinct, MFA obligatoire pour les émetteurs, journal d'audit chaîné, révocation, alertes sur volumes anormaux.",
         cs="CS-04", cs_name="Contrôler et tracer l'émission"),
    dict(id="CA-05", nom="Prendre le contrôle d'un compte", prio="Élevée", misactor="Attaquant externe",
         access="Aucun", entry="POST /api/auth/login, /api/auth/reset, stockage du navigateur", cia="C, I",
         soph="Faible", uc="Se connecter",
         desc="Force brute ou réutilisation de mots de passe volés (credential stuffing), énumération des comptes via les messages d'erreur, ou vol de jeton dans le navigateur (XSS, poste partagé).",
         pre="Formulaire de connexion exposé.", post="Compte de titulaire (partages), d'agent (émission) ou de vérificateur (dossiers) usurpé.",
         reco="Limitation de débit, temporisation, mots de passe longs vérifiés contre les fuites, MFA, messages génériques, jetons en mémoire.",
         cs="CS-05", cs_name="Protéger l'authentification et les sessions"),
    dict(id="CA-06", nom="Accéder aux ressources d'autrui (IDOR)", prio="Élevée", misactor="Utilisateur malveillant (tout rôle)",
         access="Utilisateur authentifié", entry="GET /api/diplomas/{id}, /api/shares/{id}, /api/inbox/{id}", cia="C, I",
         soph="Faible", uc="Consulter son portefeuille, Gérer ses partages, Espace vérificateur",
         desc="Modification d'un identifiant dans l'URL pour lire le diplôme d'un autre titulaire, la liste de ses partages, ou les dossiers reçus par une autre organisation ; un agent tente d'agir sur un autre établissement.",
         pre="Posséder un compte valide.", post="Fuite de données personnelles et de dossiers ; émission pour un autre établissement.",
         reco="Contrôle d'appartenance et de rattachement à l'établissement côté serveur, refus par défaut, identifiants non prédictibles.",
         cs="CS-06", cs_name="Contrôler l'accès à chaque ressource"),
    dict(id="CA-07", nom="Neutraliser les marques ou abuser de la vérification", prio="Moyenne", misactor="Faussaire, Imposteur",
         access="Visiteur", entry="POST /api/verify, copie authentique", cia="I",
         soph="Élevée", uc="Vérification publique",
         desc="L'attaquant transforme une copie (recompression, recadrage, bruit) et interroge la vérification en boucle pour apprendre quand l'empreinte ou le filigrane disparaît (attaque par oracle), afin d'obtenir une copie « propre » ou un verdict ambigu.",
         pre="Disposer d'une copie authentique.", post="Copie dont l'empreinte est effacée (usurpation non détectée) ou verdict trompeur.",
         reco="Marques robustes et redondantes, verdict sans score, limitation de débit, « indéterminé » jamais présenté comme « authentique ».",
         cs="CS-07", cs_name="Rendre la vérification non exploitable"),
    dict(id="CA-08", nom="Injecter du code ou déposer un fichier piégé", prio="Élevée", misactor="Utilisateur malveillant, Attaquant externe",
         access="Visiteur ou authentifié", entry="Dépôt de visuel, POST /api/verify, champs texte (nom, motif, finalité)", cia="C, I, D",
         soph="Moyenne", uc="Préparer un diplôme, Vérification publique",
         desc="Dépôt d'un PDF contenant du JavaScript ou des fichiers embarqués, d'une image « bombe de décompression », d'un fichier polyglotte, ou saisie de &lt;script&gt; dans un champ réaffiché ; injection JPQL.",
         pre="Fonction de dépôt ou champ texte accessible.", post="Exécution de code chez d'autres utilisateurs, saturation du serveur, fuite de données.",
         reco="Rastérisation des PDF (aucun contenu actif conservé), signatures binaires, limites de taille/dimensions/pages, ré-encodage, encodage des sorties, CSP, requêtes paramétrées.",
         cs="CS-08", cs_name="Valider et neutraliser les entrées"),
    dict(id="CA-09", nom="Collecter des données personnelles en masse", prio="Moyenne", misactor="Attaquant externe",
         access="Visiteur", entry="POST /api/verify, éventuelle recherche par numéro", cia="C",
         soph="Faible", uc="Vérification publique",
         desc="L'attaquant tente d'énumérer les numéros de diplôme ou d'interroger le service pour constituer une base de noms, dates de naissance et parcours (revente, hameçonnage ciblé, usurpation).",
         pre="Service de vérification public.", post="Fuite massive de données personnelles (atteinte à la loi n° 2013-450).",
         reco="Vérification uniquement à partir du document lui-même (aucune recherche par nom ou numéro), limitation de débit, minimisation des données affichées.",
         cs="CS-09", cs_name="Protéger les données des titulaires"),
    dict(id="CA-10", nom="Nier une émission ou effacer ses traces", prio="Moyenne", misactor="Agent corrompu, Administrateur malveillant",
         access="Agent, responsable ou administrateur", entry="Journaux, base de données", cia="I",
         soph="Moyenne", uc="Valider et émettre, Révoquer, Consulter l'audit",
         desc="Un responsable nie avoir validé un diplôme de complaisance ; un administrateur supprime des lignes de journal ou réactive en base un diplôme révoqué.",
         pre="Journalisation incomplète ou modifiable.", post="Impossible d'établir les responsabilités ; fraude non sanctionnée.",
         reco="Signatures des émissions et révocations, journal chaîné par hachage, séparation administrateur / auditeur / émetteur, horloge synchronisée.",
         cs="CS-10", cs_name="Assurer la non-répudiation et l'audit"),
    dict(id="CA-11", nom="Rendre la vérification indisponible", prio="Moyenne", misactor="Attaquant externe",
         access="Aucun", entry="POST /api/verify, émission par lot", cia="D",
         soph="Faible", uc="Vérification publique, Émettre par lot",
         desc="Rafales de vérifications coûteuses (extraction DCT) ou de lots d'émission géants pour saturer le service, par exemple en pleine campagne de recrutement.",
         pre="Endpoints coûteux exposés.", post="Recruteurs incapables de vérifier ; perte de confiance dans le service.",
         reco="Quotas, limitation de débit, traitements asynchrones bornés, délais maximaux, supervision.",
         cs="CS-11", cs_name="Préserver la disponibilité"),
]

# --------------------------------------------------------------------------- risques
RISKS = [
    ("R-01", "CA-01", "Faux diplôme accepté par un recruteur", 3, 4),
    ("R-02", "CA-02", "Diplôme authentique retouché non détecté", 3, 4),
    ("R-03", "CA-03", "Usurpation du diplôme d'autrui non détectée", 3, 3),
    ("R-04", "CA-04", "Diplôme de complaisance émis par un initié", 2, 4),
    ("R-05", "CA-05", "Prise de contrôle d'un compte (agent ou titulaire)", 3, 4),
    ("R-06", "CA-06", "Accès aux diplômes, partages ou dossiers d'autrui", 3, 3),
    ("R-07", "CA-07", "Empreinte neutralisée par attaque oracle", 2, 3),
    ("R-08", "CA-08", "Fichier piégé ou injection", 3, 3),
    ("R-09", "CA-09", "Collecte massive de données personnelles", 2, 3),
    ("R-10", "CA-10", "Répudiation d'une émission / altération des journaux", 2, 3),
    ("R-11", "CA-11", "Indisponibilité de la vérification", 3, 2),
]

# --------------------------------------------------------------------------- catégories
CATS = [
    ("AUT", "Identification &amp; authentification", "Ch. 4", "Logiciel"),
    ("AUZ", "Autorisation (contrôle d'accès)", "Ch. 4", "Logiciel"),
    ("CON", "Confidentialité", "Ch. 3", "Logiciel"),
    ("INT", "Intégrité &amp; validation des données", "Ch. 3", "Logiciel"),
    ("NRP", "Non-répudiation", "Ch. 3–4", "Logiciel"),
    ("DIM", "Sécurité des services de dissimulation", "Ch. 2–3", "Logiciel (métier)"),
    ("PRV", "Informations privées (loi n° 2013-450, RGPD)", "Ch. 4", "Logiciel + organisation"),
    ("LOG", "Journalisation, audit &amp; détection d'intrusion", "Ch. 5", "Logiciel"),
    ("ERR", "Gestion des erreurs &amp; conditions exceptionnelles", "Ch. 5", "Logiciel"),
    ("DIS", "Résilience &amp; disponibilité", "Ch. 3 / 7", "Système"),
    ("TST", "Tests de sécurité", "Ch. 6", "Processus"),
    ("DEP", "Déploiement &amp; maintenance", "Ch. 7", "Système + processus"),
]

# --------------------------------------------------------------------------- exigences de sécurité
# (id, énoncé, origine, (R, C, F), vérification, OWASP 2025, ASVS 5.0)
SEC = [
 # ---- AUT
 ("SR-AUT-01", "Le mot de passe comporte <b>au moins 12 caractères</b> (jusqu'à 128), sans règle de composition imposée, et est refusé s'il figure dans une liste de 100 000 mots de passe compromis.",
  "CA-05", (3, 3, 3), "Test d'API : « Password123! » refusé", "A07", "V6"),
 ("SR-AUT-02", "Les mots de passe sont hachés avec <b>Argon2id</b> (m = 19 Mio, t = 2, p = 1), sel aléatoire de 16 octets par compte ; aucun mot de passe n'est stocké ni journalisé en clair.",
  "CA-05", (3, 3, 3), "Revue de code + inspection de la base", "A04", "V6, V11"),
 ("SR-AUT-03", "Le second facteur <b>TOTP</b> (RFC 6238, fenêtre ±1 pas de 30 s) est <b>obligatoire</b> pour les rôles Agent émetteur, Responsable émetteur, Administrateur et Auditeur, et proposé aux autres ; un code n'est accepté qu'une fois.",
  "CA-04, CA-05", (3, 3, 2), "Test : connexion d'un agent sans TOTP refusée ; rejeu refusé", "A07", "V6"),
 ("SR-AUT-04", "Après <b>5 échecs</b> de connexion sur un compte en 15 min, chaque tentative est retardée de façon exponentielle (jusqu'à 15 min) ; l'endpoint de connexion est limité à <b>20 requêtes/min par IP</b>.",
  "CA-05", (3, 3, 2), "Test automatisé de 30 tentatives → 429 et délai mesuré", "A07", "V6"),
 ("SR-AUT-05", "Les réponses de connexion, d'activation et de réinitialisation sont <b>identiques</b> (message et temps de réponse ±50 ms) que le compte existe ou non.",
  "CA-05, CA-09", (2, 3, 3), "Test d'API : e-mail existant / inexistant", "A07", "V6"),
 ("SR-AUT-06", "Les jetons d'activation et de réinitialisation font 128 bits aléatoires, sont stockés <b>hachés</b>, à usage unique, et expirent (72 h activation, 15 min réinitialisation) ; une réinitialisation invalide toutes les sessions.",
  "CA-05", (2, 3, 3), "Test : réutilisation du lien → refus", "A07", "V6"),
 ("SR-AUT-07", "Le jeton d'accès est un JWT signé <b>ES256</b>, valide <b>10 min</b>, conservé uniquement en mémoire dans la SPA ; le jeton de rafraîchissement (8 h, rotatif, révocable) est un cookie <b>HttpOnly, Secure, SameSite=Strict</b>.",
  "CA-05", (3, 3, 2), "Inspection du navigateur : aucun jeton dans localStorage/sessionStorage", "A07", "V7, V9"),
 ("SR-AUT-08", "Les opérations sensibles (valider une émission, révoquer, changer de mot de passe ou d'e-mail, désactiver le MFA, changer un rôle) exigent une <b>ré-authentification</b> de moins de 5 min.",
  "CA-04, CA-05", (3, 2, 2), "Test d'API avec authentification ancienne → 403", "A07", "V6, V7"),
 ("SR-AUT-09", "La déconnexion et la suspension d'un compte <b>révoquent</b> immédiatement le jeton de rafraîchissement ; un jeton d'accès révoqué est refusé au plus tard à son expiration (10 min).",
  "CA-05", (2, 3, 3), "Test : refresh après logout → 401", "A07", "V7"),
 # ---- AUZ
 ("SR-AUZ-01", "Le contrôle d'accès est <b>refusé par défaut</b> : chaque ressource Jakarta REST déclare explicitement ses rôles (@RolesAllowed / @PermitAll / @DenyAll) ; un test fait échouer le build sinon.",
  "CA-06", (3, 3, 3), "Test d'architecture en CI (déjà en place : AccessControlDeclarationTest)", "A01", "V8"),
 ("SR-AUZ-02", "Tout accès à un diplôme, une copie, un partage ou un dossier reçu vérifie <b>côté serveur</b> l'appartenance (titulaire, établissement émetteur, organisation destinataire) ; sinon la réponse est <b>404</b>.",
  "CA-06", (3, 3, 2), "Tests d'API croisés entre comptes sur chaque endpoint", "A01", "V8"),
 ("SR-AUZ-03", "<b>Double validation</b> : un diplôme n'est émis qu'après validation par un Responsable émetteur <b>différent</b> de l'agent qui l'a préparé ; la même règle s'applique aux lots.",
  "CA-04", (3, 2, 2), "Test : auto-validation par le préparateur → 403", "A01, A06", "V8, V2"),
 ("SR-AUZ-04", "Un agent ou responsable n'agit que sur <b>son</b> établissement, et uniquement si celui-ci a été validé par l'Administrateur.",
  "CA-04, CA-06", (3, 3, 3), "Test d'API : émission pour un autre établissement → 404", "A01", "V8"),
 ("SR-AUZ-05", "L'Administrateur ne dispose <b>d'aucun endpoint</b> permettant de créer, modifier, valider ou réactiver un diplôme ; l'Auditeur a un accès en lecture seule aux journaux, que personne ne peut modifier via l'application.",
  "CA-04, CA-10", (2, 3, 3), "Revue de la matrice rôles × endpoints + tests d'API", "A01, A09", "V8, V16"),
 ("SR-AUZ-06", "Les identifiants exposés sont des <b>UUID v4</b> ; leur imprévisibilité est une défense en profondeur et ne remplace jamais SR-AUZ-02.",
  "CA-06", (1, 2, 3), "Revue de code", "A01", "V8"),
 ("SR-AUZ-07", "Des <b>quotas</b> sont appliqués côté serveur : 500 émissions/jour par établissement, 200 vérifications/jour par vérificateur, 30 partages actifs par diplôme.",
  "CA-04, CA-11", (2, 2, 3), "Tests de dépassement → 429", "A06", "V2"),
 # ---- CON
 ("SR-CON-01", "Toutes les communications utilisent <b>TLS 1.3</b> (TLS 1.2 toléré avec suites AEAD) ; HTTP redirige vers HTTPS (déjà en place) et l'en-tête <b>HSTS</b> (max-age 1 an) est envoyé.",
  "CA-05", (3, 3, 3), "Scan testssl.sh : note A minimum", "A04", "V12"),
 ("SR-CON-02", "Les documents (visuels, diplômes émis, copies) sont <b>chiffrés au repos</b> en AES-256-GCM avec une clé de données par établissement, elle-même chiffrée par une clé maître stockée dans le <b>credential store Elytron</b>.",
  "CA-06", (2, 2, 1), "Inspection du stockage : fichiers illisibles sans la clé", "A04", "V11, V14"),
 ("SR-CON-03", "Les clés privées de signature et les clés de filigrane des établissements, la clé de position du sceau et la table des partages sont chiffrées en base avec la même hiérarchie de clés ; elles ne quittent jamais le serveur.",
  "CA-01, CA-03", (3, 2, 2), "Revue de code + inspection de la base", "A04", "V11, V14"),
 ("SR-CON-04", "Le contenu du sceau caché est <b>chiffré</b> (AES-256-GCM) avant insertion : sans la clé, il est indistinguable de données aléatoires.",
  "CA-02, CA-09", (2, 1, 2), "Test statistique d'entropie sur le sceau extrait sans clé", "A04", "V11"),
 ("SR-CON-05", "Le Service Worker ne met en cache <b>que les ressources statiques</b> ; les réponses de /api/** sont en <b>NetworkOnly</b> (déjà configuré) et portent <b>Cache-Control: no-store</b>.",
  "CA-05", (2, 2, 3), "Test hors ligne après connexion → aucune donnée privée", "A02", "V3, V14"),
 # ---- INT
 ("SR-INT-01", "Un fichier déposé n'est accepté que si sa <b>signature binaire</b> est PDF, PNG ou JPEG, s'il fait ≤ <b>10 Mo</b>, ≤ <b>1 page</b> (PDF) et ≤ <b>7000 × 7000 px</b> (vérifié <b>avant</b> décodage), et s'il se décode entièrement.",
  "CA-08, CA-11", (3, 3, 2), "Jeu de tests : polyglotte, bombe d'image, faux MIME → rejet", "A05, A06", "V5"),
 ("SR-INT-02", "Les PDF déposés sont <b>rastérisés</b> à 300 dpi : JavaScript, formulaires, pièces jointes et liens du fichier d'origine ne sont jamais conservés ni servis ; le diplôme émis est un PDF reconstruit par la plateforme. La rastérisation ne protège pas le lecteur lui-même : l'analyse par <b>Apache PDFBox</b> s'exécute dans une tâche <b>isolée et bornée</b> (30 s, 512 Mo de tas, aucun accès réseau, répertoire temporaire dédié purgé), et PDFBox est maintenu à la dernière version corrective.",
  "CA-08", (3, 2, 2), "Test : PDF avec JavaScript → document émis sans contenu actif", "A05, A08", "V5"),
 ("SR-INT-03", "Chaque DTO d'entrée est validé par <b>Jakarta Validation</b> (types, longueurs, formats en liste blanche, dates cohérentes) ; toute requête non conforme est rejetée (400) avant traitement.",
  "CA-08", (3, 3, 3), "Tests d'API avec valeurs hors bornes", "A05", "V2"),
 ("SR-INT-04", "L'accès aux données se fait uniquement par <b>requêtes paramétrées</b> (Jakarta Data / JPA) ; toute concaténation dans du JPQL/SQL est interdite et détectée par le SAST.",
  "CA-08", (3, 3, 3), "Règle Semgrep / FindSecBugs bloquante", "A05", "V1"),
 ("SR-INT-05", "La SPA n'injecte jamais de HTML non maîtrisé ; une <b>CSP</b> stricte est envoyée : default-src 'self' ; script-src 'self' ; object-src 'none' ; frame-ancestors 'none' ; base-uri 'none'.",
  "CA-05, CA-08", (3, 3, 2), "Scan ZAP + charge utile XSS dans un nom", "A05", "V3"),
 ("SR-INT-06", "L'endpoint de rafraîchissement, seul à s'appuyer sur un cookie, exige un <b>jeton anti-CSRF</b> (double soumission) et vérifie l'en-tête Origin.",
  "CA-05", (2, 3, 3), "Test : requête intersite forgée → 403", "A01", "V3"),
 ("SR-INT-07", "Les dépendances sont figées (pom.xml, package-lock.json) et toute ressource tierce éventuelle est chargée avec <b>Subresource Integrity</b>.",
  "Chaîne d'approvisionnement", (2, 3, 3), "Revue de la CI et des fichiers de verrouillage", "A03, A08", "V15"),
 # ---- NRP
 ("SR-NRP-01", "Chaque émission produit un <b>certificat signé Ed25519</b> par la clé de l'établissement : SHA-256 du document, données officielles, identifiants du préparateur et du valideur, horodatage UTC.",
  "CA-01, CA-10", (3, 3, 2), "Vérification de signature hors ligne", "A08", "V11"),
 ("SR-NRP-02", "Chaque <b>révocation</b> est signée par le Responsable (motif, date) et rendue visible à toute vérification ultérieure ; une révocation est irréversible (on réémet un nouveau diplôme).",
  "CA-04, CA-10", (3, 2, 2), "Test : réactivation d'un diplôme révoqué impossible", "A08", "V11, V16"),
 ("SR-NRP-03", "Le journal d'audit est <b>chaîné</b> : chaque entrée contient le SHA-256 de la précédente ; un contrôle quotidien vérifie la chaîne et lève une alerte en cas de rupture.",
  "CA-10", (3, 2, 2), "Test : modification manuelle d'une ligne → alerte", "A09", "V16"),
 ("SR-NRP-04", "Chaque vérification produit un <b>rapport signé</b> par la plateforme (date, verdict, identifiant de copie, vérificateur s'il est authentifié).",
  "CA-03, CA-10", (2, 1, 2), "Vérification de la signature du rapport", "A09", "V16"),
 ("SR-NRP-05", "Les serveurs sont synchronisés par <b>NTP</b> ; tous les horodatages sont en UTC (ISO 8601).",
  "CA-10", (1, 2, 3), "Revue de configuration", "A09", "V16"),
 # ---- DIM
 ("SR-DIM-01", "Les trois couches (filigrane, sceau, empreinte) occupent des <b>ensembles disjoints de blocs DCT 8×8</b>, choisis par un générateur pseudo-aléatoire initialisé par une clé secrète ; l'insertion privilégie les blocs texturés (masquage perceptuel).",
  "CA-01, CA-02, CA-07", (2, 2, 2), "Test : chaque couche extraite sans erreur en présence des deux autres", "A06", "V11"),
 ("SR-DIM-02", "Le filigrane est généré avec une <b>clé secrète propre à chaque établissement</b> : impossible de produire un filigrane valide au nom d'un établissement sans sa clé.",
  "CA-01", (3, 2, 2), "Test : détection avec la clé d'un autre établissement → négatif", "A04", "V11"),
 ("SR-DIM-03", "Le sceau contient les données officielles, l'identifiant du diplôme et de l'établissement, <b>signés Ed25519</b> puis chiffrés, et protégés par un code correcteur ; une signature invalide rend le document « non authentique ».",
  "CA-02", (3, 2, 2), "Test : modification d'un octet du sceau → signature invalide", "A08", "V11"),
 ("SR-DIM-04", "Seuils de qualité : <b>PSNR ≥ 40 dB</b> pour l'ensemble des marques ; filigrane, sceau et empreinte lisibles après <b>JPEG qualité 75</b> et <b>redimensionnement à 75 %</b> (seuils à confirmer par le prototype J2). Avant toute extraction, une étape de <b>resynchronisation géométrique</b> estime l'échelle et le décalage (motif de référence inséré par la plateforme) et réaligne l'image sur la grille 8×8 ; sans elle, un simple redimensionnement désaligne les blocs DCT et rend les marques illisibles.",
  "CA-01, CA-02, CA-07", (3, 2, 1), "Banc de test sur 50 diplômes de référence", "A06", "V2"),
 ("SR-DIM-05", "Verdict de vérification : <b>« authentique »</b> seulement si filigrane détecté ET sceau à signature valide ET statut non révoqué ET (si disponible) concordance avec le registre ; <b>« indéterminé »</b> si une marque est illisible ; sinon <b>« non authentique »</b>.",
  "CA-01, CA-02, CA-07", (3, 2, 2), "Tests de décision sur une matrice de cas", "A06, A10", "V2"),
 ("SR-DIM-06", "Les codes d'empreinte sont des valeurs <b>aléatoires de 64 bits</b>, sans lien calculable avec le titulaire ou le destinataire, protégées par un code correcteur ; aucune attribution n'est rendue sous un <b>seuil de confiance</b> défini (sinon « indéterminé »).",
  "CA-03, CA-07", (2, 2, 2), "Tests de robustesse JPEG Q75 + taux de faux positifs nul sur le banc", "A04, A06", "V11"),
 ("SR-DIM-07", "Aucun fichier sans empreinte ne sort de la plateforme : téléchargement du titulaire et partages produisent toujours une copie empreintée ; l'original n'est jamais servi.",
  "CA-03", (3, 2, 3), "Test : tous les endpoints de téléchargement renvoient une copie empreintée", "A01", "V8"),
 ("SR-DIM-08", "La vérification publique <b>ne révèle jamais</b> le destinataire d'une copie (« copie partagée — destinataire non divulgué ») ; seuls le titulaire et l'organisation destinataire le voient.",
  "CA-03, CA-09", (2, 3, 3), "Test d'API anonyme sur une copie partagée", "A01", "V8, V14"),
 ("SR-DIM-09", "La vérification publique est limitée à <b>10 requêtes/heure par IP</b> et répond par un verdict <b>sans score</b> ni détail de corrélation, pour empêcher l'attaque par oracle.",
  "CA-07, CA-09", (3, 2, 3), "Test : 11 requêtes → 429 ; revue du format de réponse", "A06", "V2, V4"),
 ("SR-DIM-10", "Une copie vérifiée par une organisation authentifiée qui n'en est pas destinataire, ou après expiration ou révocation du partage, déclenche un avertissement explicite et une <b>notification au titulaire</b> sous 1 min.",
  "CA-03", (3, 2, 2), "Scénario de test « copie hors contexte »", "A06", "V2"),
 # ---- PRV
 ("SR-PRV-01", "Seules les données nécessaires sont collectées (<b>minimisation</b>) : nom, prénoms, date de naissance, données du diplôme, e-mail ; les métadonnées EXIF/GPS des fichiers sont supprimées.",
  "Loi n° 2013-450, RGPD", (2, 3, 3), "Revue du modèle de données + exiftool", "A04", "V14"),
 ("SR-PRV-02", "Il n'existe <b>aucune recherche</b> publique de diplôme par nom, date de naissance ou numéro : la vérification part toujours du document lui-même.",
  "CA-09", (3, 3, 3), "Revue de l'API : aucun endpoint de recherche public", "A01", "V8, V14"),
 ("SR-PRV-03", "Les journaux ne contiennent <b>jamais</b> de mot de passe, jeton, secret TOTP, clé ni date de naissance ; les personnes y sont désignées par leur identifiant interne.",
  "CA-09, Loi n° 2013-450", (3, 3, 3), "Recherche automatique de motifs sensibles dans les logs de test", "A09", "V14, V16"),
 ("SR-PRV-04", "Le titulaire consulte l'<b>historique des vérifications</b> de ses copies (date, organisation si authentifiée) et peut exporter ses données ; les journaux sont conservés 12 mois.",
  "Loi n° 2013-450, RGPD", (2, 3, 2), "Test fonctionnel d'export et d'historique", "—", "V14"),
 ("SR-PRV-05", "Avant toute mise en production réelle, le traitement est <b>déclaré auprès de l'ARTCI</b> (autorité ivoirienne de protection des données) et une mention d'information est présentée aux titulaires.",
  "Loi n° 2013-450", (1, 3, 2), "Dossier de conformité archivé dans docs/", "—", "—"),
 # ---- LOG
 ("SR-LOG-01", "Sont journalisés : connexions réussies/échouées, MFA, préparations, validations, émissions, révocations, partages, vérifications, refus d'accès, fichiers rejetés, actions d'administration.",
  "CA-04, CA-06, CA-10", (3, 3, 2), "Test : chaque événement produit une entrée", "A09", "V16"),
 ("SR-LOG-02", "Chaque entrée est en <b>JSON</b> (horodatage UTC, corrélation, acteur, IP, action, ressource, résultat) ; retours à la ligne et caractères de contrôle neutralisés (anti-injection de logs).",
  "CA-10", (2, 3, 3), "Test : nom avec \\r\\n → entrée unique", "A09", "V16"),
 ("SR-LOG-03", "Des <b>alertes</b> sont levées vers l'Auditeur : ≥ 10 échecs de connexion sur un compte en 5 min ; émissions d'un établissement &gt; 3 fois sa moyenne quotidienne ; ≥ 20 refus d'accès d'un même compte en 10 min ; rupture de la chaîne d'audit.",
  "CA-04, CA-05, CA-06", (3, 2, 2), "Scénarios simulés → alerte visible", "A09", "V16"),
 ("SR-LOG-04", "Les journaux d'audit sont écrits sur un stockage distinct, en ajout seul, et sauvegardés quotidiennement.",
  "CA-10", (2, 2, 2), "Revue de déploiement", "A09", "V16"),
 # ---- ERR
 ("SR-ERR-01", "Un <b>ExceptionMapper</b> global renvoie des erreurs au format <b>RFC 9457</b> (application/problem+json), message générique et identifiant de corrélation, sans trace de pile ni version.",
  "CA-08", (2, 3, 3), "Test : erreur 500 provoquée → corps générique", "A10, A02", "V16"),
 ("SR-ERR-02", "Le système échoue en <b>mode sûr</b> : toute exception pendant une vérification de droits, de signature ou d'extraction aboutit à un refus ou à « indéterminé », jamais à « authentique ».",
  "CA-01, CA-06, CA-07", (3, 2, 2), "Tests d'injection de fautes", "A10", "V16"),
 ("SR-ERR-03", "Les conditions exceptionnelles métier (document illisible, page multiple, capacité insuffisante, délai dépassé, quota atteint) produisent un message explicite et un <b>état cohérent</b> (transaction annulée, aucun fichier partiel).",
  "CA-08, CA-11", (2, 3, 2), "Tests unitaires des cas limites", "A10", "V16"),
 # ---- DIS
 ("SR-DIS-01", "Les opérations coûteuses (émission, extraction, vérification) sont limitées à <b>10 par minute et par compte</b> en plus des quotas journaliers.",
  "CA-11", (3, 2, 3), "Test de charge : 11<super>e</super> requête → 429", "A06", "V2"),
 ("SR-DIS-02", "Les traitements d'image s'exécutent dans un <b>ManagedExecutorService</b> (Jakarta Concurrency) à file bornée, avec un délai maximal de <b>30 s</b> par document ; les lots sont traités en tâche de fond.",
  "CA-11", (2, 2, 2), "Test : document lourd → arrêt à 30 s", "A06", "V15"),
 ("SR-DIS-03", "WildFly limite la taille des requêtes (max-post-size 12 Mo, 50 Mo pour les lots) et le nombre de connexions simultanées par client.",
  "CA-08, CA-11", (2, 2, 3), "Test : envoi de 20 Mo → 413", "A02", "V13"),
 ("SR-DIS-04", "Base de données, documents chiffrés et clés sont <b>sauvegardés quotidiennement</b> ; une restauration est testée à chaque release (RPO 24 h, RTO 4 h).",
  "Disponibilité", (2, 2, 2), "Exercice de restauration documenté", "—", "V14"),
 ("SR-DIS-05", "Des sondes de santé (live / ready) permettent le redémarrage automatique du conteneur applicatif.",
  "CA-11", (1, 1, 3), "Test : arrêt de la base → ready = DOWN", "—", "V13"),
 # ---- TST
 ("SR-TST-01", "Chaque pull request déclenche une analyse <b>SAST</b> (SpotBugs + FindSecBugs, Semgrep) ; le merge est bloqué en présence d'une alerte de sévérité haute.",
  "Processus", (2, 3, 3), "Pipeline GitHub Actions", "A06", "V15"),
 ("SR-TST-02", "Une analyse de composition (<b>SCA</b> : OWASP Dependency-Check, npm audit, Dependabot) bloque le build pour toute vulnérabilité CVSS ≥ 7.",
  "Chaîne d'approvisionnement", (3, 3, 3), "Pipeline GitHub Actions", "A03", "V15"),
 ("SR-TST-03", "Une analyse <b>DAST</b> (OWASP ZAP) est exécutée sur l'environnement de recette avant chaque release ; aucune alerte haute ne doit subsister.",
  "Processus", (2, 3, 2), "Rapport ZAP archivé dans docs/", "A02, A05", "—"),
 ("SR-TST-04", "Chaque cas d'abus (CA-01 à CA-11) est couvert par <b>au moins un test automatisé</b> qui démontre l'échec de l'attaque.",
  "Tous les CA", (3, 3, 2), "Matrice de traçabilité CA → test", "A06", "—"),
 ("SR-TST-05", "Une recherche de <b>secrets</b> (gitleaks) est exécutée à chaque push ; tout secret détecté bloque le pipeline.",
  "Chaîne d'approvisionnement", (2, 3, 3), "Pipeline GitHub Actions", "A02", "V13"),
 ("SR-TST-06", "Un <b>banc de robustesse</b> automatisé (recompression JPEG, redimensionnement, recadrage léger, conversion PDF ↔ image) est exécuté à chaque modification du moteur de dissimulation.",
  "CA-07", (2, 2, 2), "Rapport du banc en CI", "A06", "—"),
 # ---- DEP
 ("SR-DEP-01", "WildFly est <b>durci</b> : interface de management liée à 127.0.0.1, aucun compte par défaut, sous-systèmes inutiles retirés, en-têtes Server / X-Powered-By supprimés, exécution non root.",
  "A02", (3, 3, 2), "Revue de configuration + scan de ports", "A02", "V13"),
 ("SR-DEP-02", "Aucun secret n'est présent dans le dépôt Git ; ils sont fournis par le credential store Elytron ou des variables d'environnement du conteneur.",
  "A02", (3, 3, 3), "gitleaks + revue", "A02", "V13"),
 ("SR-DEP-03", "Les en-têtes de sécurité sont envoyés sur toutes les réponses : HSTS, CSP, X-Content-Type-Options: nosniff, Referrer-Policy: no-referrer, Permissions-Policy restrictive.",
  "CA-05, CA-08", (2, 3, 3), "Scan securityheaders / ZAP", "A02", "V3"),
 ("SR-DEP-04", "Les images de conteneur sont minimales, exécutées sans root et analysées (Trivy) avant publication ; aucune vulnérabilité critique tolérée.",
  "Chaîne d'approvisionnement", (2, 2, 2), "Rapport Trivy en CI", "A03", "V13"),
 ("SR-DEP-05", "Les dépendances sont mises à jour <b>au moins une fois par mois</b> ; un correctif de sécurité critique est déployé sous <b>7 jours</b> ; les clés d'établissement sont renouvelables sans invalider les diplômes déjà émis.",
  "Processus", (2, 2, 2), "Historique Dependabot + procédure de rotation testée", "A03", "V15, V11"),
]

AHP_CRITERIA = ["Risque couvert (R)", "Obligation (C)", "Facilité (F)"]
AHP_MATRIX = [[1, 3, 5], [1 / 3, 1, 3], [1 / 5, 1 / 3, 1]]

# --------------------------------------------------------------------------- récits (backlog GitHub)
STORIES = [
    ("CA-01", "En tant que faussaire, je peux reproduire le modèle d'un diplôme de l'ESATIC pour me faire recruter.",
     "En tant que recruteur, je veux savoir en quelques secondes si un diplôme a vraiment été émis par l'établissement indiqué.", "SR-DIM-02/05, SR-NRP-01"),
    ("CA-02", "En tant que titulaire fraudeur, je peux changer « Passable » en « Bien » sur ma copie.",
     "En tant que vérificateur, je veux voir les données officielles à côté du document pour repérer toute retouche.", "SR-DIM-03/05, SR-CON-04"),
    ("CA-03", "En tant qu'imposteur, je peux présenter le diplôme d'un homonyme récupéré dans un dossier qui a fuité.",
     "En tant que titulaire, je veux être alerté si une copie que j'ai partagée est présentée ailleurs.", "SR-DIM-06/07/10"),
    ("CA-04", "En tant qu'agent corrompu, je peux émettre un diplôme pour quelqu'un qui n'a pas réussi.",
     "En tant que responsable d'établissement, je veux qu'aucun diplôme ne soit émis sans ma validation, et que tout soit tracé.", "SR-AUZ-03, SR-AUT-03, SR-LOG-03"),
    ("CA-05", "En tant qu'attaquant, je peux tester des milliers de mots de passe sur le compte d'un agent.",
     "En tant qu'agent, je veux que mon compte soit protégé par un second facteur et contre la force brute.", "SR-AUT-01/03/04"),
    ("CA-06", "En tant qu'utilisateur malveillant, je peux changer l'identifiant dans /api/shares/{id} pour voir les partages d'un autre.",
     "En tant que titulaire, je veux que personne d'autre que moi ne voie mes diplômes et mes partages.", "SR-AUZ-01/02"),
    ("CA-07", "En tant que faussaire, je peux interroger la vérification en boucle pour savoir quand l'empreinte disparaît.",
     "En tant qu'exploitant, je veux une vérification qui ne renseigne pas l'attaquant.", "SR-DIM-09, SR-ERR-02"),
    ("CA-08", "En tant qu'attaquant, je peux déposer un PDF contenant du JavaScript pour attaquer les vérificateurs.",
     "En tant que vérificateur, je veux que tout document affiché soit inoffensif.", "SR-INT-01/02/05"),
    ("CA-09", "En tant qu'attaquant, je peux énumérer les numéros de diplôme pour récupérer noms et dates de naissance.",
     "En tant que titulaire, je veux que mes données ne soient jamais consultables sans le document.", "SR-PRV-02, SR-DIM-08/09"),
    ("CA-10", "En tant qu'administrateur malveillant, je peux réactiver en base un diplôme révoqué et effacer la trace.",
     "En tant qu'auditeur, je veux détecter toute altération des émissions, révocations et journaux.", "SR-NRP-02/03, SR-AUZ-05"),
    ("CA-11", "En tant qu'attaquant, je peux saturer la vérification en pleine campagne de recrutement.",
     "En tant que recruteur, je veux que la vérification reste disponible.", "SR-DIS-01/02, SR-AUZ-07"),
]


def ahp_weights():
    import numpy as np
    A = np.array(AHP_MATRIX, dtype=float)
    vals, vecs = np.linalg.eig(A)
    k = int(np.argmax(vals.real))
    w = np.abs(vecs[:, k].real); w = w / w.sum()
    lmax = vals[k].real; n = len(A)
    ci = (lmax - n) / (n - 1); ri = 0.58
    return w, lmax, ci, ci / ri


def prioritized():
    w, *_ = ahp_weights()
    out = []
    for r in SEC:
        R, C, Fa = r[3]
        score = round(w[0] * R + w[1] * C + w[2] * Fa, 2)
        prio = "P1" if score >= 2.5 else ("P2" if score >= 1.9 else "P3")
        out.append((r, score, prio))
    return out


def export_csv(path):
    import csv, re
    cat = {c[0]: c for c in CATS}
    clean = lambda s: re.sub("<[^>]+>", "", s).replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    with open(path, "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f, delimiter=";")
        wr.writerow(["id", "categorie", "chapitre", "enonce", "origine", "R", "C", "F", "score_ahp", "priorite",
                     "verification", "owasp_2025", "asvs_5", "statut", "version"])
        for r, s, p in prioritized():
            c = cat[r[0].split("-")[1]]
            wr.writerow([r[0], clean(c[1]), c[2], clean(r[1]), r[2], *r[3], s, p, clean(r[4]), r[5], r[6], "Spécifiée", VERSION])

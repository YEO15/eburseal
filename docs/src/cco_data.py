"""Données du cahier conceptuel (phase 2) : modèle de menaces STRIDE contextualisé et notation OWASP Risk Rating.

Chaque menace est rattachée à un élément du diagramme de flux (DFD), à un cas d'abus de la phase 1 (CA-xx),
à une référence CAPEC / CWE quand elle existe, et aux exigences de sécurité SR-xx qui la traitent.

Facteurs OWASP Risk Rating (échelles officielles 0-9) :
  vraisemblance = (SK compétence, MO motivation, OP opportunité, SZ taille du groupe,
                   ED facilité de découverte, EE facilité d'exploitation, AW notoriété, ID détection d'intrusion)
  impact technique = (C, I, A, AC traçabilité)    impact métier = (FD financier, RD réputation, NC conformité, PV vie privée)
Les valeurs décrivent le risque INHÉRENT : l'application telle qu'elle serait sans les contre-mesures prévues.
"""

VERSION = "1.1"
DATE = "16/11/2026"

# --------------------------------------------------------------------------- éléments du DFD
ELEMENTS = [
    ("E1", "Entité externe", "Navigateur (PWA/SPA) des utilisateurs et des visiteurs", "TB1"),
    ("P1", "Processus", "API Jakarta REST + Jakarta Security / Elytron (authentification, JWT, RBAC)", "TB1"),
    ("P2", "Processus", "Services CDI métier : émission, partage, vérification", "—"),
    ("P3", "Processus", "Rastérisation des PDF (Apache PDFBox, 300 dpi) et décodage des images", "TB3"),
    ("P4", "Processus", "Moteur EburSeal DCT 8×8 : filigrane, sceau caché, empreinte", "TB3"),
    ("P5", "Processus", "Signature Ed25519 et chiffrement AES-256-GCM (JCA, Java 25)", "TB4"),
    ("DS1", "Stockage", "PostgreSQL : registre des diplômes, partages, clés chiffrées", "TB2"),
    ("DS2", "Stockage", "Documents chiffrés (visuels, diplômes, copies)", "TB2"),
    ("DS3", "Stockage", "Journal d'audit chaîné, en ajout seul", "TB2"),
    ("DS4", "Stockage", "Credential store Elytron (clé maître)", "TB4"),
    ("X1", "Chaîne de production", "Dépôt GitHub, CI GitHub Actions, dépendances Maven / npm", "—"),
]

BOUNDARIES = [
    ("TB1", "Internet ↔ serveur WildFly", "Tout ce qui vient du navigateur est non fiable : identité, paramètres, fichiers, jetons."),
    ("TB2", "Application ↔ données", "La base, le stockage et les journaux ne font confiance qu'à l'application, avec un compte au moindre privilège."),
    ("TB3", "Traitement de fichiers non fiables", "Les PDF et images déposés sont décodés dans une file bornée (temps, mémoire, taille), isolée du reste."),
    ("TB4", "Secrets", "Les clés ne quittent jamais le serveur : elles ne sont manipulées que par P5, à partir du credential store."),
]

# --------------------------------------------------------------------------- menaces
# id, lettre STRIDE, élément, titre, description contextualisée, technique d'attaque, réf. CAPEC/CWE, cas d'abus,
# contre-mesures natives (Jakarta EE / WildFly / Java), contre-mesures applicatives, exigences, facteurs OWASP, risque résiduel
T = []


def threat(id, s, el, titre, desc, tech, ref, ca, nat, app, sr, L, It, Ib, resid):
    T.append(dict(id=id, s=s, el=el, titre=titre, desc=desc, tech=tech, ref=ref, ca=ca, nat=nat, app=app, sr=sr,
                  L=L, It=It, Ib=Ib, resid=resid))


# ---------------- S — Spoofing (authentification)
threat("T-S1", "S", "P1", "Hameçonnage d'un Responsable émetteur",
       "Un réseau de faussaires envoie à un directeur des études une fausse page de connexion EburSeal, récupère son mot de passe "
       "et son code TOTP en temps réel, puis valide des diplômes de complaisance préparés par un complice.",
       "Page clonée + relais en temps réel du code TOTP (proxy d'hameçonnage)", "CAPEC-98", "CA-04, CA-05",
       "Jakarta Security (HttpAuthenticationMechanism), Elytron (realm, TOTP)",
       "TOTP obligatoire ; ré-authentification pour valider ; double validation par une autre personne ; alerte de volume ; évolution prévue vers WebAuthn (résistant à l'hameçonnage)",
       "SR-AUT-03, SR-AUT-08, SR-AUZ-03, SR-LOG-03",
       (6, 9, 7, 9, 7, 5, 6, 8), (2, 7, 1, 7), (3, 9, 5, 3), "Moyen")
threat("T-S2", "S", "P1", "Bourrage d'identifiants sur /api/auth/login",
       "Un attaquant rejoue des millions de couples e-mail / mot de passe issus de fuites d'autres sites pour prendre le contrôle "
       "de comptes de titulaires (partages) ou d'agents (préparation de diplômes).",
       "Listes de fuites publiques + outils automatisés", "CAPEC-600", "CA-05",
       "Undertow (filtre de limitation des requêtes)",
       "Mots de passe refusés s'ils figurent dans une liste de fuites ; ralentissement exponentiel ; réponses identiques ; MFA pour les rôles sensibles ; hachage Argon2id (m = 19 Mio, t = 2, p = 1, sel de 16 octets), pour qu'une fuite de la base n'alimente pas d'autres attaques",
       "SR-AUT-01, SR-AUT-02, SR-AUT-04, SR-AUT-05, SR-AUT-03",
       (5, 4, 9, 9, 9, 9, 9, 8), (6, 5, 1, 9), (3, 5, 5, 5), "Faible")
threat("T-S3", "S", "P1", "Forge d'un jeton JWT (confusion d'algorithme)",
       "L'attaquant modifie l'en-tête du JWT (alg = none, ou HS256 en utilisant la clé publique ES256 comme secret HMAC) et "
       "s'attribue le groupe « Responsable » pour valider des diplômes.",
       "Altération de l'en-tête et des claims du jeton", "CAPEC-196", "CA-05",
       "Vérification JWT du serveur (algorithme imposé, clé publique de confiance)",
       "Algorithme ES256 imposé en liste blanche ; vérification iss, aud, exp ; rôles relus en base pour les opérations sensibles ; jeton de 10 min",
       "SR-AUT-07, SR-AUT-08, SR-AUZ-01",
       (3, 9, 9, 9, 7, 5, 9, 9), (7, 7, 1, 9), (3, 9, 5, 7), "Faible")
threat("T-S4", "S", "P4", "Greffe des marques d'un vrai diplôme sur un faux (copy attack)",
       "Le faussaire estime le filigrane d'un diplôme authentique de l'établissement (différence avec une version lissée) et le "
       "réinjecte dans un faux, pour que le document « se fasse passer » pour une émission de l'établissement.",
       "Estimation puis réinsertion du signal de filigrane", "— (attaque propre au watermarking)", "CA-01",
       "—",
       "Le filigrane seul ne suffit jamais : le verdict exige aussi un sceau signé Ed25519 lié aux données officielles du diplôme et sa présence au registre",
       "SR-DIM-02, SR-DIM-03, SR-DIM-05",
       (3, 9, 9, 9, 3, 3, 4, 9), (2, 7, 1, 9), (3, 9, 5, 3), "Faible")

threat("T-S5", "S", "P5", "Compromission de la clé de signature d'un établissement",
       "La clé privée Ed25519 d'un établissement est volée (sauvegarde mal protégée, ancien serveur) ou n'est jamais renouvelée : tous les sceaux qu'elle signe "
       "deviennent contrefaisables, et l'on ne peut plus distinguer les diplômes légitimes des faux signés avec elle.",
       "Vol ou exposition prolongée d'une clé de signature", "CWE-320, CWE-324", "CA-01, CA-04",
       "JCA de Java 25 (Ed25519) ; credential store Elytron",
       "Clés chiffrées par la clé maître et jamais exportées ; identifiant de version de clé inscrit dans le sceau ; rotation planifiée et révocation d'une clé compromise, avec réémission des diplômes concernés (exigence à ajouter au recueil v1.1)",
       "SR-CON-03, SR-NRP-01, SR-DIS-04",
       (5, 9, 4, 2, 3, 5, 4, 9), (7, 9, 1, 9), (7, 9, 7, 7), "Moyen")
threat("T-S6", "S", "P1", "Requête forgée sur l'endpoint de rafraîchissement (CSRF)",
       "Une page piégée visitée par un titulaire connecté déclenche à son insu un appel à /api/auth/refresh, seul endpoint authentifié par cookie, "
       "pour obtenir un jeton d'accès au nom de la victime.",
       "Requête intersite forgée", "CAPEC-62", "CA-05",
       "Cookie SameSite=Strict, HttpOnly, Secure (Undertow / Elytron)",
       "Jeton anti-CSRF en double soumission ; vérification de l'en-tête Origin ; aucun autre endpoint ne repose sur un cookie",
       "SR-INT-06",
       (5, 4, 7, 6, 7, 5, 9, 8), (6, 3, 1, 7), (3, 5, 5, 3), "Faible")

# ---------------- T — Tampering (intégrité)
threat("T-T1", "T", "P4", "Effacement du filigrane ou de l'empreinte par traitement du signal",
       "Un titulaire recompresse sa copie en JPEG, la redimensionne, la recadre ou l'imprime puis la rescanne, pour faire disparaître "
       "l'empreinte (copie non traçable) ou rendre le verdict ambigu. Jusqu'aux seuils de SR-DIM-04 (JPEG qualité 75, redimensionnement à 75 %), "
       "les marques doivent rester lisibles ; au-delà (par exemple JPEG qualité 60 ou impression-numérisation), l'attaque peut réussir à effacer, "
       "mais jamais à faire paraître authentique.",
       "Recompression, redimensionnement, recadrage, impression-numérisation", "— (attaque propre au watermarking)", "CA-07",
       "—",
       "Insertion par QIM (modulation d'indice de quantification) dans les coefficients DCT de moyenne fréquence des blocs 8×8, avec un pas de quantification Δ calibré au prototype J2 pour rester lisible après JPEG qualité 75 tout en garantissant PSNR ≥ 40 dB ; redondance et code correcteur ; resynchronisation géométrique avant extraction ; au-delà des seuils, verdict « indéterminé », jamais « authentique » ; banc de robustesse à chaque modification du moteur",
       "SR-DIM-04, SR-DIM-05, SR-ERR-02, SR-TST-06",
       (6, 9, 9, 9, 7, 5, 9, 9), (2, 7, 1, 9), (3, 9, 5, 3), "Moyen")
threat("T-T2", "T", "P4", "Retouche locale de la mention en préservant les blocs marqués",
       "Le titulaire remplace « Passable » par « Bien » en ne touchant qu'aux pixels de la mention : le filigrane, réparti ailleurs, reste détectable.",
       "Retouche ciblée dans un logiciel d'édition d'image", "— (attaque propre au domaine)", "CA-02",
       "—",
       "Sceau caché contenant les données officielles signées ; affichage côte à côte du contenu affiché et du contenu officiel ; contrôle au registre",
       "SR-DIM-03, SR-DIM-05",
       (6, 9, 7, 6, 7, 5, 9, 9), (2, 7, 1, 9), (3, 9, 5, 3), "Faible")
threat("T-T3", "T", "P4", "Collusion de copies pour neutraliser l'empreinte",
       "Plusieurs titulaires (ou un titulaire disposant de plusieurs copies partagées) comparent ou moyennent leurs copies pour localiser les blocs portant l'empreinte et les brouiller.",
       "Comparaison ou moyennage de copies empreintées", "— (attaque propre au fingerprinting)", "CA-03, CA-07",
       "—",
       "Positions des blocs tirées par une clé secrète ; code d'empreinte aléatoire de 64 bits avec code correcteur ; limite de 30 partages actifs par diplôme ; codes anti-collusion (Tardos) étudiés en évolution",
       "SR-DIM-01, SR-DIM-06, SR-AUZ-07",
       (3, 4, 7, 6, 3, 3, 4, 9), (2, 3, 1, 9), (1, 5, 2, 3), "Moyen (accepté)")
threat("T-T4", "T", "DS1", "Réactivation d'un diplôme révoqué par affectation de masse",
       "Un agent ajoute le champ « statut »: « EMIS » dans la requête JSON de modification d'un diplôme révoqué, en espérant que l'entité JPA soit liée directement au corps de la requête.",
       "Affectation de masse (mass assignment) ou concaténation JPQL", "CWE-915, CAPEC-66", "CA-10",
       "JSON-B vers des DTO dédiés ; Jakarta Validation ; Jakarta Data / JPA paramétrés",
       "Aucun champ de statut dans les DTO d'entrée ; révocation irréversible et signée ; aucune entité exposée directement",
       "SR-INT-03, SR-INT-04, SR-NRP-02, SR-AUZ-05",
       (3, 9, 7, 6, 7, 5, 9, 8), (7, 9, 5, 7), (3, 9, 7, 7), "Faible")
threat("T-T5", "T", "X1", "Compromission d'une dépendance Maven ou npm",
       "Une version piégée d'une bibliothèque (par exemple un plugin de build ou une dépendance transitive de la PWA) exécute du code malveillant à la compilation ou dans le navigateur.",
       "Manipulation d'une bibliothèque open source", "CAPEC-538", "—",
       "Versions figées dans pom.xml et package-lock.json",
       "Analyse de composition à chaque pull request (Dependency-Check, npm audit, actifs) ; alertes Dependabot et push protection (actives) ; versions verrouillées ; mises à jour mensuelles",
       "SR-TST-02, SR-INT-07, SR-DEP-05",
       (1, 4, 4, 9, 3, 3, 6, 9), (9, 9, 7, 9), (3, 9, 7, 7), "Faible")

# ---------------- R — Repudiation (non-répudiation)
threat("T-R1", "R", "P2", "Un Responsable nie avoir validé un diplôme de complaisance",
       "Mis en cause, le directeur des études affirme que la validation a été faite « par le système » ou par un collègue qui connaissait son mot de passe.",
       "Contestation a posteriori", "—", "CA-10",
       "Jakarta Security (identité de l'appelant)",
       "Certificat d'émission signé Ed25519 indiquant le préparateur et le validateur ; ré-authentification juste avant la validation ; horodatage UTC synchronisé",
       "SR-NRP-01, SR-AUT-08, SR-NRP-05",
       (9, 4, 4, 4, 7, 9, 6, 8), (2, 3, 1, 9), (1, 5, 5, 3), "Faible")
threat("T-R2", "R", "DS3", "Altération des journaux par un administrateur",
       "Un administrateur supprime en base les lignes d'audit d'une émission frauduleuse, puis remet le diplôme au statut « émis ».",
       "Manipulation des journaux d'audit", "CAPEC-268", "CA-10",
       "—",
       "Journal chaîné par SHA-256 et contrôlé chaque jour ; stockage distinct en ajout seul ; l'administrateur n'a aucun droit sur les diplômes ; l'auditeur est un rôle séparé",
       "SR-NRP-03, SR-LOG-04, SR-AUZ-05",
       (5, 4, 4, 2, 7, 5, 6, 9), (2, 7, 1, 9), (3, 9, 5, 5), "Faible")
threat("T-R3", "R", "DS3", "Injection de fausses entrées dans le journal",
       "L'attaquant insère des retours à la ligne dans le motif d'un partage pour fabriquer une ligne de journal qui semble être une vérification réussie.",
       "Injection CRLF dans un champ journalisé", "CAPEC-93", "CA-10",
       "—",
       "Journal structuré en JSON ; neutralisation des caractères de contrôle ; validation des champs texte",
       "SR-LOG-02, SR-INT-03",
       (5, 4, 7, 6, 7, 5, 9, 8), (2, 3, 1, 7), (1, 4, 2, 3), "Faible")

# ---------------- I — Information disclosure (confidentialité)
threat("T-I1", "I", "P2", "Révélation du destinataire d'une copie par la vérification publique",
       "Un curieux soumet une copie trouvée en ligne et apprend, par la réponse, à quelle entreprise le titulaire a postulé.",
       "Exploitation de la réponse du service de vérification", "CWE-200", "CA-03, CA-09",
       "—",
       "La vérification publique n'affiche jamais le destinataire (« copie partagée — destinataire non divulgué ») ; seuls le titulaire et l'organisation destinataire le voient",
       "SR-DIM-08, SR-PRV-04",
       (9, 4, 9, 9, 7, 9, 6, 8), (6, 1, 1, 9), (1, 5, 5, 3), "Faible")
threat("T-I2", "I", "P2", "Collecte massive de données personnelles",
       "Un robot interroge le service pour constituer une base « nom, date de naissance, diplôme » revendue pour l'hameçonnage ciblé.",
       "Énumération et interrogation automatisée", "CAPEC-54", "CA-09",
       "Undertow (limitation des requêtes)",
       "Aucune recherche par nom ou numéro : la vérification part toujours du document ; 10 requêtes/heure par IP ; minimisation des données affichées",
       "SR-PRV-02, SR-DIM-09, SR-PRV-01",
       (5, 4, 9, 9, 9, 9, 9, 8), (7, 1, 1, 9), (3, 9, 7, 7), "Faible")
threat("T-I3", "I", "P1", "Fuite d'informations techniques par les erreurs",
       "Une requête malformée renvoie une trace de pile Java révélant les classes, la version de WildFly et la structure de la base, utiles pour cibler une attaque.",
       "Provocation d'erreurs et lecture des réponses", "CWE-209", "CA-08",
       "ExceptionMapper Jakarta REST ; Undertow (suppression des en-têtes Server / X-Powered-By)",
       "Réponses d'erreur RFC 9457 génériques avec identifiant de corrélation ; aucun détail technique côté client",
       "SR-ERR-01, SR-DEP-01",
       (6, 4, 9, 9, 9, 9, 9, 8), (2, 1, 1, 7), (1, 1, 2, 3), "Faible")
threat("T-I4", "I", "DS4", "Fuite des clés de filigrane ou de signature",
       "Une clé d'établissement apparaît dans un journal, une variable d'environnement affichée, un dépôt Git ou un fichier de vidage mémoire (heap dump) écrit en clair après un plantage.",
       "Récupération de secrets dans les artefacts d'exploitation", "CWE-312, CWE-532", "CA-01, CA-04",
       "Credential store Elytron ; JCA (clés manipulées en mémoire uniquement)",
       "Clés chiffrées en base par la clé maître ; aucune clé ni secret dans les journaux ; recherche de secrets et push protection ; vidages mémoire désactivés ou écrits sur un volume chiffré",
       "SR-CON-03, SR-PRV-03, SR-DEP-02, SR-TST-05",
       (5, 9, 4, 2, 3, 5, 4, 9), (9, 9, 1, 9), (7, 9, 7, 7), "Faible")
threat("T-I5", "I", "E1", "Vol du jeton d'accès par une faille XSS",
       "Un nom d'organisation contenant un script est réaffiché dans l'espace d'un titulaire ; le script lit le jeton et l'envoie à l'attaquant.",
       "Script injecté dans un champ réaffiché", "CAPEC-63", "CA-05, CA-08",
       "—",
       "Jeton d'accès conservé en mémoire seulement ; React n'insère pas de HTML brut ; CSP stricte sans script en ligne",
       "SR-AUT-07, SR-INT-05, SR-DEP-03",
       (3, 4, 7, 6, 7, 5, 9, 9), (7, 5, 1, 7), (3, 5, 5, 3), "Faible")
threat("T-I6", "I", "E1", "Données personnelles laissées dans le cache d'un poste partagé",
       "Un titulaire consulte son portefeuille dans un cybercafé ; le Service Worker a mis en cache les réponses de l'API, que l'utilisateur suivant peut relire.",
       "Lecture du cache du navigateur", "CWE-524", "CA-09",
       "—",
       "Le Service Worker ne met en cache que les ressources statiques ; /api/** en NetworkOnly avec Cache-Control: no-store",
       "SR-CON-05",
       (9, 1, 4, 4, 3, 5, 4, 9), (6, 1, 1, 9), (1, 4, 5, 3), "Faible")

threat("T-I7", "I", "P5", "Réutilisation d'un nonce AES-GCM pour chiffrer les sceaux",
       "Le sceau de chaque diplôme est chiffré en AES-256-GCM avec la clé de l'établissement. Si deux sceaux sont chiffrés avec le même nonce (compteur remis à zéro "
       "après un redémarrage, générateur défaillant), un attaquant qui possède les deux diplômes récupère le XOR des contenus et peut forger des étiquettes d'authentification.",
       "Exploitation d'un nonce réutilisé (perte de confidentialité et d'intégrité)", "CWE-323", "CA-01, CA-02",
       "JCA de Java 25 (AES/GCM/NoPadding, SecureRandom DRBG)",
       "Nonce de 96 bits tiré par SecureRandom à chaque chiffrement et stocké avec le sceau ; jamais de compteur réinitialisable ; test unitaire d'unicité des nonces",
       "SR-CON-04, SR-CON-02",
       (3, 9, 4, 9, 3, 3, 6, 9), (7, 7, 1, 9), (3, 9, 5, 3), "Faible")
threat("T-I8", "I", "DS2", "Exfiltration des documents stockés ou de leurs sauvegardes",
       "Un attaquant accède au volume de stockage ou à une sauvegarde quotidienne (SR-DIS-04) et copie les visuels et diplômes émis, avec les données personnelles qu'ils contiennent.",
       "Accès direct au stockage ou aux sauvegardes", "CWE-311, CWE-530", "CA-09",
       "JCA (AES-256-GCM) ; credential store Elytron",
       "Documents chiffrés au repos avec une clé de données par établissement, elle-même chiffrée par la clé maître ; sauvegardes chiffrées, clé maître jamais sauvegardée avec les données",
       "SR-CON-02, SR-DIS-04",
       (5, 4, 4, 2, 3, 5, 4, 9), (7, 1, 1, 9), (3, 9, 7, 7), "Faible")

# ---------------- D — Denial of service (disponibilité)
threat("T-D1", "D", "P3", "Saturation de la heap par un PDF « bombe de rastérisation »",
       "Un anonyme soumet au portail de vérification un PDF de quelques Ko déclarant une page de 20 000 × 20 000 points. Rastérisée à 300 dpi, elle exige plusieurs Go : "
       "la JVM lève une OutOfMemoryError et l'instance WildFly ne répond plus à personne.",
       "Fichier forgé à coût de décodage démesuré", "CAPEC-130", "CA-08, CA-11",
       "Jakarta Concurrency (ManagedExecutorService à file bornée) ; options JVM (-Xmx, -XX:+ExitOnOutOfMemoryError)",
       "Dimensions de la page lues avant le rendu et rejet au-delà de 7000 × 7000 px à 300 dpi ; une seule page ; 10 Mo maximum ; rendu isolé et borné (30 s, 512 Mo) ; redémarrage automatique",
       "SR-INT-01, SR-INT-02, SR-DIS-02, SR-DIS-05",
       (5, 4, 9, 9, 7, 5, 9, 8), (2, 1, 9, 9), (3, 5, 2, 3), "Faible")
threat("T-D2", "D", "P3", "Bombe de décompression PNG",
       "Une image PNG de 50 Ko annonce 50 000 × 50 000 pixels : son décodage complet alloue près de 10 Go.",
       "Image fortement compressée aux dimensions démesurées", "CAPEC-130, CWE-409", "CA-08, CA-11",
       "javax.imageio (lecture de l'en-tête IHDR par ImageReader avant décodage)",
       "Contrôle de la signature binaire et des dimensions avant tout décodage ; ré-encodage systématique ; file de traitement bornée",
       "SR-INT-01, SR-DIS-02",
       (5, 4, 9, 9, 9, 9, 9, 8), (2, 1, 7, 9), (3, 5, 2, 3), "Faible")
threat("T-D3", "D", "P4", "Rafales de vérifications coûteuses",
       "En pleine campagne de recrutement, un script envoie des milliers de vérifications : chaque extraction DCT occupe un cœur de calcul et la file sature.",
       "Inondation de requêtes coûteuses", "CAPEC-125", "CA-11",
       "Undertow (max-post-size, connexions par client) ; Jakarta Concurrency",
       "10 vérifications/heure par IP publique ; 10 opérations coûteuses/min par compte ; quotas journaliers ; délai maximal de 30 s par document",
       "SR-DIM-09, SR-DIS-01, SR-DIS-03, SR-AUZ-07",
       (6, 4, 9, 9, 9, 9, 9, 8), (2, 1, 7, 7), (3, 5, 2, 3), "Faible")
threat("T-D4", "D", "P1", "Épuisement des connexions (requêtes lentes)",
       "L'attaquant ouvre des centaines de connexions et envoie les en-têtes HTTP octet par octet, pour occuper tous les fils d'entrée d'Undertow.",
       "Requêtes HTTP volontairement lentes (type Slowloris)", "CAPEC-469", "CA-11",
       "Undertow (délais read-timeout et no-request-timeout, limite de connexions par client)",
       "Supervision par les sondes de santé ; frontal avec délais courts envisagé au déploiement",
       "SR-DIS-03, SR-DIS-05",
       (6, 1, 9, 9, 9, 9, 9, 8), (2, 1, 7, 9), (3, 5, 2, 3), "Faible")

# ---------------- E — Elevation of privilege (autorisation)
threat("T-E1", "E", "P2", "Accès au diplôme ou aux partages d'autrui (IDOR)",
       "Un titulaire remplace l'identifiant dans GET /api/wallet/{id}/copy par celui d'un autre diplôme ; un agent tente de préparer un diplôme pour un autre établissement.",
       "Modification d'un identifiant dans l'URL ou le corps", "CWE-639", "CA-06",
       "Jakarta Security (@RolesAllowed), intercepteurs CDI",
       "Contrôle d'appartenance et de rattachement à l'établissement côté serveur pour chaque ressource ; identifiants UUID v4 (défense en profondeur seulement)",
       "SR-AUZ-02, SR-AUZ-04, SR-AUZ-06",
       (6, 4, 7, 6, 7, 5, 9, 8), (7, 5, 1, 7), (3, 5, 5, 7), "Faible")
threat("T-E2", "E", "P1", "Endpoint REST oublié sans contrôle d'accès",
       "Un développeur ajoute une ressource Jakarta REST d'administration et oublie l'annotation de rôle : elle devient accessible à tout visiteur.",
       "Découverte d'endpoints par exploration de l'API", "CWE-862", "CA-06",
       "Jakarta Security (@RolesAllowed, @DenyAll)",
       "Refus par défaut ; test automatisé qui fait échouer le build si une ressource ne déclare pas ses rôles (déjà en place)",
       "SR-AUZ-01, SR-TST-04",
       (5, 4, 9, 9, 9, 9, 6, 9), (7, 7, 1, 9), (3, 9, 5, 7), "Faible")
threat("T-E3", "E", "P2", "Contournement de la double validation",
       "Un agent fait valider son propre diplôme en se connectant avec un second compte, ou obtient un rôle de Responsable auprès d'un administrateur complaisant.",
       "Abus de privilèges et de comptes multiples", "CAPEC-122", "CA-04",
       "Jakarta Security (identité de l'appelant)",
       "Validateur différent du préparateur (contrôle sur la personne, pas seulement sur le compte) ; changement de rôle sous ré-authentification et journalisé ; alerte de volume",
       "SR-AUZ-03, SR-AUT-08, SR-LOG-03",
       (9, 9, 4, 4, 7, 9, 6, 8), (2, 7, 1, 7), (3, 9, 5, 3), "Moyen")
threat("T-E4", "E", "P1", "Exécution de code par désérialisation Java",
       "Un objet Java sérialisé et piégé (gadget chain) est envoyé à un point d'entrée qui le désérialise, ce qui exécute des commandes sur le serveur.",
       "Charge sérialisée malveillante", "CAPEC-586", "CA-08",
       "JSON-B / JSON-P uniquement ; filtre de désérialisation de la JVM (jdk.serialFilter, JEP 290)",
       "Aucun usage d'ObjectInputStream sur des données externes ; détection par l'analyse CodeQL du dépôt (active) ; SAST dans la CI prévu au chapitre 6",
       "SR-INT-03, SR-TST-01",
       (3, 9, 9, 9, 3, 3, 9, 9), (9, 9, 9, 9), (7, 9, 7, 7), "Faible")
threat("T-E5", "E", "P1", "Console de management WildFly exposée",
       "L'interface de management (port 9990) est joignable depuis Internet avec un compte par défaut : l'attaquant déploie sa propre application sur le serveur.",
       "Accès à l'interface d'administration du serveur d'application", "CWE-1188", "CA-08",
       "WildFly (interface de management liée à 127.0.0.1, realm de management)",
       "Aucun compte par défaut ; sous-systèmes inutiles retirés ; conteneur sans root ; analyse d'image (Trivy)",
       "SR-DEP-01, SR-DEP-04",
       (5, 9, 9, 9, 9, 5, 9, 9), (9, 9, 9, 9), (7, 9, 7, 7), "Faible")


# --------------------------------------------------------------------------- OWASP Risk Rating
def level(x):
    return "Faible" if x < 3 else ("Moyen" if x < 6 else "Élevé")


SEVERITY = {  # (impact, vraisemblance) -> sévérité (matrice OWASP)
    ("Élevé", "Faible"): "Moyenne", ("Élevé", "Moyen"): "Élevée", ("Élevé", "Élevé"): "Critique",
    ("Moyen", "Faible"): "Faible", ("Moyen", "Moyen"): "Moyenne", ("Moyen", "Élevé"): "Élevée",
    ("Faible", "Faible"): "Note", ("Faible", "Moyen"): "Faible", ("Faible", "Élevé"): "Moyenne",
}
ORDER = {"Critique": 0, "Élevée": 1, "Moyenne": 2, "Faible": 3, "Note": 4}


def rate(t):
    L = sum(t["L"]) / 8
    It = sum(t["It"]) / 4
    Ib = sum(t["Ib"]) / 4
    I = max(It, Ib)  # on retient l'impact le plus défavorable (technique ou métier)
    return L, It, Ib, I, SEVERITY[(level(I), level(L))]


# --------------------------------------------------------------------------- complément vie privée (LINDDUN ciblé)
LINDDUN = [
    ("Linkability", "Relier les vérifications de plusieurs copies d'un même titulaire pour reconstituer son parcours de candidature.",
     "Codes d'empreinte aléatoires sans lien calculable ; historique visible seulement par le titulaire", "SR-DIM-06, SR-DIM-08"),
    ("Identifiability", "Identifier une personne à partir du service public (nom + date de naissance).",
     "Aucune recherche par nom ou numéro ; données affichées minimales", "SR-PRV-01, SR-PRV-02"),
    ("Unawareness", "Le titulaire ignore quelles organisations ont vérifié ses copies.",
     "Historique des vérifications et export des données pour le titulaire", "SR-PRV-04"),
    ("Non-compliance", "Traitement de données personnelles non conforme à la loi ivoirienne n° 2013-450.",
     "Déclaration à l'ARTCI et mention d'information avant toute mise en production", "SR-PRV-05"),
]

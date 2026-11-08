"""Recueil des besoins fonctionnels et de sécurité (SRE) EburSeal."""
import sys, pathlib, re
from collections import Counter, defaultdict
from vmpdf import Doc, W
from reportlab.lib import colors
import data as D

HERE = pathlib.Path(__file__).parent
out = sys.argv[1] if len(sys.argv) > 1 else str(HERE.parent / "recueil-des-besoins.pdf")
d = Doc(out, "Recueil des besoins", "Besoins fonctionnels et ingénierie des exigences de sécurité (SRE)", D.VERSION, "rdb")
PRIO = {r[0]: (s, p) for r, s, p in D.prioritized()}
NA, NS, NF = len(D.ABUSE), len(D.SEC), len(D.FUNC)
lvl = lambda s: "Élevé" if s >= 9 else ("Moyen" if s >= 5 else "Faible")

d.cover([
    ("Projet", "EburSeal — délivrance et vérification de diplômes infalsifiables (Côte d'Ivoire)"),
    ("Équipe (binôme)", D.TEAM),
    ("Formation", "SUP'COM — 3<super>e</super> année cycle ingénieur, option CySeD"),
    ("Module / encadrant", "Sécurité Applicative — Dr. Ing. Mohamed-Becha Kaâniche"),
    ("Approche SRE", "SQUARE adapté (ossature) + cas d'abus / cas de sécurité + récits d'abus / de sécurité + arbres d'attaque et STRIDE"),
    ("Contenu", f"{NF} besoins fonctionnels · {NA} cas d'abus · {NS} exigences de sécurité priorisées et tracées"),
    ("Version / date", f"v{D.VERSION} — {D.DATE} (document évolutif : voir § 11)"),
], [[D.VERSION, D.DATE, "O. Yacouba, Y. T. Daouda", "Version initiale : SQUARE étapes 1 à 9, catalogue des exigences, traçabilité"]])
d.h1_break = False

# =====================================================================
d.H1("Introduction", newpage=True)
d.H2("Objet du document")
d.P("Ce document recense les <b>besoins fonctionnels</b> d'EburSeal et ses <b>exigences de sécurité</b>, obtenues par une démarche d'ingénierie des exigences de sécurité "
    "(IES / <i>Security Requirements Engineering</i>, SRE). Il complète le cahier des charges, qui décrit le projet, son périmètre et son architecture.")
d.P("Conformément à l'énoncé, il <b>justifie l'approche SRE choisie</b> (§ 2) et <b>recense en détail</b> les besoins de sécurité (§ 8). Conformément au cours, une exigence de sécurité "
    "est une exigence <b>non fonctionnelle</b> et <b>négative</b> (ce que le système <b>ne doit pas</b> permettre). Elle est donc rédigée <b>séparément</b> des besoins fonctionnels, "
    "pour être examinée et testée séparément.")
d.H2("Références")
d.table([["Réf.", "Document"],
         ["[COURS]", "M.-B. Kaâniche, <i>Sécurité Applicative</i>, ch. 1 et 2 — SUP'COM, 2026"],
         ["[ENONCE]", "Énoncé de l'atelier : cahier des charges PWA/SPA Jakarta EE 11 — WildFly 42 / Java 25"],
         ["[SQUARE]", "N. Mead, T. Stehney, <i>Security Quality Requirements Engineering (SQUARE) Methodology</i>, CMU/SEI-2005-TR-009"],
         ["[OWASP-T10]", "OWASP Top 10 — édition 2025"],
         ["[ASVS]", "OWASP Application Security Verification Standard 5.0.0 (mai 2025) — niveau cible : <b>2</b>"],
         ["[LOI-CI]", "Loi n° 2013-450 du 19 juin 2013 relative à la protection des données à caractère personnel (Côte d'Ivoire) ; autorité de contrôle : ARTCI"],
         ["[RGPD]", "Règlement (UE) 2016/679 — référence de bonnes pratiques (titulaires de la diaspora, vérificateurs européens)"],
         ["[RFC]", "RFC 6238 (TOTP), RFC 7519 (JWT), RFC 8446 (TLS 1.3), RFC 8032 (Ed25519), RFC 9457 (Problem Details)"]],
        [2.6, 14.8])
d.H2("Conventions")
d.table([["Préfixe", "Signification", "Exemple"],
         ["BF-&lt;module&gt;-nn", "Besoin fonctionnel (MoSCoW : M = Must, S = Should, C = Could)", "BF-EMI-02"],
         ["A<i>n</i> / OS-<i>n</i>", "Actif à protéger / objectif de sécurité", "A1, OS-1"],
         ["CA-nn", "Cas d'abus (point de vue de l'attaquant)", "CA-03"],
         ["CS-nn", "Cas d'utilisation de sécurité, qui <i>mitigates</i> le cas d'abus de même numéro", "CS-03"],
         ["R-nn", "Risque évalué (vraisemblance × impact)", "R-03"],
         ["SR-&lt;cat&gt;-nn", "Exigence de sécurité, priorité P1 / P2 / P3 issue de l'AHP", "SR-DIM-10"]],
        [3.6, 10.6, 3.2])

# =====================================================================
d.H1("Justification de l'approche SRE choisie", newpage=True)
d.H2("Ce que notre contexte exige d'une approche")
d.P("Le cours présente deux familles d'approches IES/SRE : les approches <b>dérivées</b> (cas d'abus, cas d'utilisation de sécurité, récits d'abus) et les approches <b>dédiées</b> "
    "(SQUARE, OCTAVE). L'énoncé y ajoute les arbres d'attaque, UMLsec/SecureUML et SERA. Nous avons d'abord fixé les critères imposés par notre situation :")
d.table([["Critère", "Pourquoi il compte pour EburSeal"],
         ["K1 — Recueillir le fonctionnel <b>et</b> le non fonctionnel", "L'énoncé demande un document recensant les besoins <b>fonctionnels et SRE</b>"],
         ["K2 — Supporter des exigences qui <b>changent</b>", "L'énoncé prévoit que le recueil « pourra évoluer tout au long du cours »"],
         ["K3 — Résoudre ambiguïtés et <b>conflits</b>", "Plusieurs objectifs se contredisent (vérification publique ↔ vie privée, traçage ↔ minimisation)"],
         ["K4 — Adopter la <b>perspective de l'attaquant</b>", "Objectif fondamental de l'énoncé ; nos fraudeurs (faussaire, imposteur, agent corrompu) sont variés"],
         ["K5 — Être <b>traçable</b> et testable", "Suivi sur GitHub ; chaque exigence doit être vérifiée dans le code"],
         ["K6 — Rester <b>praticable par un binôme</b>", "Charge limitée ; intégration au backlog agile (issues, PR)"],
         ["K7 — Fournir un niveau de sécurité élevé", "Le service produit des <b>preuves</b> : une faille ruine la confiance dans tous les diplômes"]],
        [6.2, 11.2])
d.H2("Évaluation des approches du cours")
d.P("Le tableau reprend les <b>valeurs des tableaux comparatifs du cours</b> (Comparaison des approches IES/SRE, 1 à 4) pour chacun de nos critères.")
d.table([["Critère (source : tableaux du cours)", "Cas d'utilisation", "Récits", "SQUARE", "OCTAVE"],
         ["K1 — Exigences autres que sécurité", "Non fonct. seulement", "Non supporté", "<b>Fonct. + non fonct.</b>", "Non fonct. seulement"],
         ["K2 — Support des exigences changeantes", "Non supporté", "Non supporté", "<b>Modéré–Élevé</b>", "Non supporté"],
         ["K3 — Résolution des ambiguïtés", "Faible", "Faible", "<b>Élevé</b>", "Aucun"],
         ["K3 — Prévention des conflits", "Prévention définie", "Non supporté", "<b>Prévention définie</b>", "Faible"],
         ["K4 — Support de l'élicitation", "<b>Élevé</b>", "Modéré–Élevé", "Faible–Modéré", "Modéré–Élevé"],
         ["K5 — Traçabilité", "Faible", "<b>Élevé</b>", "Faible", "Modéré"],
         ["K5 — Base pour vérification / validation", "Modéré", "Faible", "<b>Modéré–Élevé</b>", "Modéré"],
         ["K6 — Facilité pour un novice", "<b>Facile</b>", "<b>Facile</b>", "Modéré", "Difficile"],
         ["K6 — Facilité de modification", "<b>Facile</b>", "<b>Facile</b>", "Modéré", "Difficile"],
         ["K7 — Niveau de sécurité de la spécification", "Modéré", "Faible", "<b>Modéré–Élevé</b>", "Modéré"],
         ["Cohérence de la spécification", "Modéré", "Faible", "<b>Modéré–Élevé</b>", "Faible"]],
        [6.2, 2.8, 2.6, 3.0, 2.8])
d.P("<b>Lecture.</b> Aucune approche ne satisfait seule tous les critères. <b>SQUARE</b> est la seule qui couvre K1, K2 et K3 (les trois demandes explicites de l'énoncé) "
    "et donne la spécification la plus sûre (K7). Ses faiblesses sont la <b>traçabilité</b> (K5) et le <b>support de l'élicitation</b> (K4), qui sont précisément les points forts "
    "des <b>récits</b> et des <b>cas d'abus</b>. OCTAVE est écartée : difficile à modifier, aucune résolution d'ambiguïté, pas de support des exigences changeantes, et orientée "
    "organisation plutôt que logiciel.")
d.H2("Approches complémentaires citées dans l'énoncé")
d.table([["Approche", "Décision", "Justification"],
         ["Arbres d'attaque / modélisation des menaces (STRIDE)", "<b>Retenue</b> (étapes 3–4)", "Décompose les buts du fraudeur (K4) ; alimente l'évaluation des risques de SQUARE"],
         ["Récits d'abus / récits de sécurité", "<b>Retenue</b> (backlog)", "Traçabilité élevée (K5) ; intégrés aux issues GitHub et à la « Definition of Done »"],
         ["Cas d'abus / cas d'utilisation de sécurité", "<b>Retenue</b> (étape 3)", "Élicitation élevée (K4) ; c'est l'artefact « misuse cases » prévu par l'étape 3 de SQUARE"],
         ["OCTAVE", "Non retenue", "Évaluation organisationnelle des risques ; trop lourde à modifier pour un recueil évolutif (K2, K6)"],
         ["UMLsec / SecureUML", "Non retenue (v1)", "Ingénierie dirigée par les modèles, coûteuse en outillage pour un binôme ; les contraintes RBAC sont exprimées dans une matrice rôles × ressources"],
         ["SERA", "Non retenue", "Analyse de risque par chaînes de missions (systèmes multi-organisations complexes) : surdimensionnée pour la v1"]],
        [4.6, 2.8, 10.0])
d.H2("Décision : SQUARE adapté comme ossature")
d.P("Nous adoptons <b>SQUARE comme processus</b> (ses 9 étapes structurent ce document) et plaçons dans ses étapes les approches dérivées, là où elles compensent ses faiblesses :")
d.img(str(HERE / "diagrams" / "square.png"), W, "Figure 1 — Processus SQUARE adapté suivi dans ce document (§ 4 à § 10)")
d.table([["Faiblesse de SQUARE (cours)", "Compensation retenue"],
         ["Support de l'élicitation faible à modéré", "Étape 3 : <b>cas d'abus</b> (élicitation élevée) + arbres d'attaque ; étape 5 : checklists OWASP ASVS / Top 10 2025"],
         ["Traçabilité faible", "<b>Récits d'abus / de sécurité</b> dans les issues GitHub + identifiants dans chaque commit + matrice CA → R → CS → SR → test (§ 10)"],
         ["« Utile uniquement pour les grands projets »", "SQUARE <b>allégé</b> : étapes 1–2 et 6–7 fusionnées dans des tableaux uniques ; référentiel unique qui régénère PDF et CSV"],
         ["Spécification semi-formelle", "Exigences <b>SMART</b> : seuils chiffrés, algorithmes nommés, méthode de vérification pour chacune"]],
        [6.0, 11.4])
d.box("SQUARE est retenu car c'est la seule approche du cours qui recueille le fonctionnel et le non fonctionnel, supporte les exigences changeantes et résout les ambiguïtés. "
      "Ce sont les trois demandes explicites de l'énoncé. Ses deux faiblesses (élicitation, traçabilité) sont comblées par les cas d'abus et les récits, qui excellent sur ces critères.",
      "Synthèse de la justification", kind="ok")

# =====================================================================
d.H1("Besoins fonctionnels", newpage=True)
d.P("Comme le prévoit l'élicitation en IES (« analyser les exigences fonctionnelles du système »), les besoins fonctionnels sont établis en premier : ce sont eux que les cas d'abus menacent. "
    "Ce sont des exigences <b>positives</b> : ce que le système <b>doit</b> faire.")
for mod in D.MODULES:
    d.H3(f"Module {mod}")
    d.table([["ID", "Besoin", "Description", "Prio", "Critère d'acceptation"]] +
            [[f[0], f"<b>{f[2]}</b>", f[3], f[4], f[5]] for f in D.FUNC if f[1] == mod],
            [2.1, 2.8, 6.2, 1.1, 5.2], small=True)
c = Counter(f[4] for f in D.FUNC)
d.P(f"<b>Répartition MoSCoW</b> : {c['M']} Must, {c['S']} Should, {c['C']} Could. Les besoins « Could » sont abandonnés en premier en cas de retard ; ils n'ont aucun impact sur la sécurité.")

# =====================================================================
d.H1("SQUARE étapes 1–2 : définitions, actifs et objectifs", newpage=True)
d.H2("Étape 1 — Définitions communes")
d.P("La première étape consiste à s'accorder sur le vocabulaire, pour que chaque exigence ait un sens unique. Les définitions génériques s'appuient sur l'ISO/IEC 27000 et l'IEEE ; "
    "les définitions métier sont propres à EburSeal.")
d.table([["Terme", "Définition retenue"],
         ["Actif", "Élément ayant de la valeur pour les titulaires, les établissements ou la plateforme, et qui doit être protégé (§ 4.2)"],
         ["Menace / vulnérabilité / risque", "Menace : cause potentielle d'un incident ; vulnérabilité : faiblesse exploitable ; risque : combinaison de la vraisemblance d'un scénario et de son impact"],
         ["Mal-acteur", "Acteur qui cherche à abuser du système (cas d'abus) ; 6 profils au § 5.1"],
         ["Diplôme émis", "Document produit par la plateforme après double validation, portant filigrane et sceau, accompagné d'un certificat d'émission"],
         ["Copie", "Fichier dérivé d'un diplôme émis, portant en plus une empreinte propre à son destinataire (ou au titulaire)"],
         ["Registre", "Base des diplômes émis et de leur statut (émis, révoqué), tenue par la plateforme pour le compte des établissements"],
         ["Filigrane (watermark)", "Marque invisible et robuste, identique sur tous les diplômes d'un établissement, générée avec la clé secrète de cet établissement"],
         ["Sceau caché", "Données officielles du diplôme, signées puis chiffrées, dissimulées par stéganographie dans le document"],
         ["Empreinte (fingerprint)", "Code aléatoire de 64 bits, différent pour chaque copie, dissimulé dans la copie"],
         ["DCT", "Transformée en cosinus discrète par blocs 8×8 (utilisée par JPEG) : domaine d'insertion des trois couches"],
         ["PSNR", "Rapport signal/bruit de crête (dB) entre le visuel déposé et le diplôme émis ; mesure l'imperceptibilité des marques"],
         ["Robustesse", "Capacité d'une marque à rester lisible après transformation (recompression JPEG, redimensionnement)"],
         ["Verdict", "Résultat d'une vérification : « authentique », « non authentique » ou « indéterminé » (§ 8, SR-DIM-05)"],
         ["Copie hors contexte", "Copie vérifiée par une organisation qui n'en est pas le destinataire, ou après expiration ou révocation du partage"],
         ["Collusion", "Plusieurs destinataires comparent leurs copies pour effacer l'empreinte (hors périmètre v1)"],
         ["Double validation", "Principe des « quatre yeux » : le valideur d'une émission est une personne différente du préparateur"]],
        [4.2, 13.2], small=True)
d.H2("Étape 2 — Actifs et besoins C-I-D")
d.P("Chaque actif est coté de 1 (faible) à 4 (critique) sur la confidentialité (C), l'intégrité (I) et la disponibilité (D). Pour EburSeal, l'<b>intégrité</b> domine : "
    "le service vend de la confiance, et une seule fausse preuve suffit à la ruiner.")
d.table([["ID", "Actif", "Description", "C", "I", "D"]] + [[a[0], f"<b>{a[1]}</b>", a[2], a[3], a[4], a[5]] for a in D.ASSETS],
        [1.0, 4.4, 9.0, 1.0, 1.0, 1.0])
d.H2("Objectifs de sécurité")
d.table([["ID", "Objectif de sécurité", "Actifs", "Propriété"],
         ["OS-1", "Un document ne peut être déclaré « authentique » que s'il a réellement été émis par l'établissement indiqué", "A1, A2, A5", "I"],
         ["OS-2", "Toute modification du contenu d'un diplôme émis est détectée", "A3, A5", "I"],
         ["OS-3", "Une copie présentée hors de son contexte est signalée, sans jamais accuser à tort", "A6, A3", "I"],
         ["OS-4", "Aucun diplôme ne peut être émis par une seule personne, ni hors de son établissement", "A1, A4", "I"],
         ["OS-5", "Les comptes, en particulier ceux des émetteurs, résistent à la prise de contrôle", "A4", "C, I"],
         ["OS-6", "Les données personnelles des titulaires ne sont accessibles qu'à partir du document lui-même ou par les ayants droit", "A8, A6", "C"],
         ["OS-7", "Toute émission, révocation et vérification est imputable, et toute altération des traces est détectée", "A7, A5", "I"],
         ["OS-8", "Le service de vérification reste disponible, y compris en période de recrutement", "A9", "D"]],
        [1.3, 11.6, 2.2, 2.3])

# =====================================================================
d.H1("SQUARE étape 3 : artefacts — la perspective de l'attaquant", newpage=True)
d.H2("Mal-acteurs")
d.table([["Mal-acteur", "Profil et moyens"]] + [list(m) for m in D.MIS_ACTORS], [4.6, 12.8])
d.H2("Diagramme des cas d'utilisation, d'abus et de sécurité")
d.P("Le diagramme suit la notation du cours : les cas d'abus (en noir) <b>« threatens »</b> les cas d'utilisation qu'ils menacent ; les cas d'utilisation de sécurité (en gris clair) "
    "<b>« mitigates »</b> les cas d'abus et sont <b>« include »</b> par les cas d'utilisation qu'ils protègent. Les cas d'abus CA-07 à CA-11, transverses, sont détaillés dans les fiches.")
d.img(str(HERE / "diagrams" / "usecases.png"), W, "Figure 2 — Cas d'utilisation, cas d'abus et cas de sécurité principaux")
d.H2("Fiches des cas d'abus")
d.P("Chaque fiche reprend le <b>modèle de fiche de cas d'abus du cours</b>. Les 8 étapes du cours ont été suivies : brainstorming, analyse des cas d'utilisation du § 3, point de vue de l'adversaire, "
    "identification des mal-acteurs, définition des cas d'abus, recherche d'au moins un cas d'abus par cas d'utilisation sensible, puis vérification de la granularité, de "
    "l'exhaustivité et de la minimalité (aucun cas d'abus n'en duplique un autre).")
for a in D.ABUSE:
    d.H3(f"{a['id']} — {a['nom']}")
    d.kv([("Priorité / sophistication", f"{a['prio']} / {a['soph']}"),
          ("Mal-acteur(s) · niveau d'accès", f"{a['misactor']} · {a['access']}"),
          ("Point d'entrée", a["entry"]),
          ("Attributs de sécurité affectés", a["cia"]),
          ("Description", a["desc"]),
          ("Pré-condition / post-condition", f"<b>Pré :</b> {a['pre']}<br/><b>Post (si succès) :</b> {a['post']}"),
          ("Cas d'utilisation menacés", a["uc"]),
          ("Recommandation architecturale", a["reco"]),
          ("Cas de sécurité « mitigates »", f"<b>{a['cs']} — {a['cs_name']}</b>")], w1=4.6)

d.H2("Cas d'utilisation de sécurité")
d.P("Selon le cours, un cas d'utilisation de sécurité est <b>dérivé d'un cas d'abus</b> et fixe les exigences qui le contrent. Il décrit <b>ce qui doit être garanti</b>, "
    "pas le mécanisme (qui apparaît dans les exigences SR).")
bycs = defaultdict(list)
for r in D.SEC:
    for ca in re.findall(r"CA-\d+", r[2]):
        bycs["CS-" + ca[3:]].append(r[0])
CS_TXT = {
    "CS-01": "Le système garantit qu'un document n'est déclaré authentique que s'il porte la marque, impossible à imiter, de l'établissement qui l'a émis.",
    "CS-02": "Le système garantit que toute différence entre le contenu affiché et le contenu officiellement émis est rendue visible au vérificateur.",
    "CS-03": "Le système garantit que chaque copie est liée à un destinataire, et qu'une présentation hors contexte est signalée au vérificateur et au titulaire.",
    "CS-04": "Le système garantit qu'aucune personne seule ne peut émettre un diplôme, et que toute émission est imputable.",
    "CS-05": "Le système garantit qu'une identité ne peut être usurpée par essais répétés ou par vol de session.",
    "CS-06": "Le système garantit que chaque ressource n'est servie qu'à ses ayants droit, et chaque action limitée à l'établissement de son auteur.",
    "CS-07": "Le système garantit que la vérification ne donne aucune information exploitable pour neutraliser les marques.",
    "CS-08": "Le système garantit qu'aucun contenu déposé ou saisi ne peut être interprété comme du code.",
    "CS-09": "Le système garantit que les données d'un titulaire ne peuvent être obtenues sans disposer du document.",
    "CS-10": "Le système garantit que toute émission, révocation et vérification est prouvable, et que toute altération des traces est détectée.",
    "CS-11": "Le système garantit que la consommation de ressources d'un acteur est bornée et n'affecte pas les autres.",
}
d.table([["CS", "Nom", "« mitigates »", "Ce qui est garanti", "Exigences SR"]] +
        [[a["cs"], f"<b>{a['cs_name']}</b>", a["id"], CS_TXT[a["cs"]], ", ".join(x.replace("SR-", "") for x in bycs[a["cs"]])] for a in D.ABUSE],
        [1.3, 3.3, 1.7, 6.4, 4.7], small=True, keep=False)
d.H3("Comparaison cas d'abus / cas de sécurité (rappel du cours, appliqué à EburSeal)")
d.table([["Critère", "Cas d'abus (CA)", "Cas d'utilisation de sécurité (CS)"],
         ["Utilisation", "Spécifier les menaces", "Spécifier les exigences de sécurité"],
         ["Critère d'évaluation", "Réussite du fraudeur (post-condition « si succès »)", "Réussite des mesures (test SR-TST-04 démontrant l'échec de l'attaque)"],
         ["Créé par / pris en charge par", "Binôme en rôle « équipe sécurité »", "Créé par l'équipe sécurité, pris en charge par l'équipe des exigences (même binôme, revue croisée)"],
         ["Acteur", "Mal-acteur (§ 5.1)", "Utilisateur légitime / système"],
         ["Piloté par", "Analyse des menaces (STRIDE, arbres d'attaque)", "Cas d'abus"]],
        [4.0, 6.3, 7.1])

d.H2("Récits d'abus et récits de sécurité (backlog GitHub)")
d.P("Chaque cas d'abus est réécrit en <b>récit d'abus</b> (« En tant que &lt;mal-acteur&gt;, je peux … ») et en <b>récit de sécurité</b> (« En tant que &lt;acteur&gt;, je veux … »). "
    "Ces récits deviennent des issues GitHub (modèles abuse-story et security-story du dépôt) : la sécurité entre dans le backlog et dans la « Definition of Done ».")
d.table([["CA", "Récit d'abus", "Récit de sécurité", "Exigences"]] + [list(s) for s in D.STORIES], [1.3, 6.4, 6.0, 3.7], small=True, keep=False)

d.H2("Arbres d'attaque")
d.P("Les arbres d'attaque décomposent un <b>but du fraudeur</b> en sous-buts. Un nœud « OU » est atteint si l'une des branches réussit ; un nœud « ET » exige toutes ses branches. "
    "Les feuilles vertes sont couvertes par une exigence ; les feuilles jaunes sont des risques résiduels assumés.")
d.img(str(HERE / "diagrams" / "attacktree_fake.png"), W * 0.85, "Figure 3 — Arbre d'attaque : faire accepter un diplôme non obtenu (objectifs OS-1, OS-2, OS-4)")
d.P("<b>Enseignement</b> : la branche la plus dangereuse est l'<b>OU 4</b>. Un diplôme de complaisance est cryptographiquement parfait, et aucune marque ne peut le détecter. "
    "Seuls les contrôles organisationnels inscrits dans l'application (double validation, MFA des émetteurs, alertes de volume, audit chaîné) le rendent difficile et traçable.")
d.img(str(HERE / "diagrams" / "attacktree_usurp.png"), W * 0.8, "Figure 4 — Arbre d'attaque : présenter le diplôme d'un autre (objectif OS-3)")
d.P("<b>Enseignement</b> : un imposteur qui vise un vérificateur <b>anonyme</b> n'est pas confondu par le contrôle du destinataire, puisque la vérification publique ne révèle pas "
    "le destinataire (SR-DIM-08). Le risque résiduel est réduit par le message de la vérification publique, qui invite le recruteur à demander un <b>partage EburSeal</b> nominatif. "
    "Il est aussi réduit par l'alerte envoyée au titulaire à chaque vérification de ses copies.")

# =====================================================================
d.H1("SQUARE étape 4 : évaluation des risques", newpage=True)
d.H2("Analyse STRIDE par composant")
d.P("STRIDE classe les menaces en six familles : <b>S</b>poofing (usurpation), <b>T</b>ampering (altération), <b>R</b>epudiation (répudiation), <b>I</b>nformation disclosure (divulgation), "
    "<b>D</b>enial of service (déni de service), <b>E</b>levation of privilege (élévation de privilège). Chaque menace est rattachée à un cas d'abus, ce qui garantit l'exhaustivité des fiches.")
d.table([["Composant", "S", "T", "R", "I", "D", "E"],
         ["SPA / PWA", "Vol de jeton (CA-05)", "XSS modifiant un verdict affiché (CA-08)", "—", "Cache SW sur poste partagé (CA-05)", "—", "Script agissant au nom d'un émetteur (CA-08)"],
         ["API + authentification", "Force brute sur un agent (CA-05)", "Paramètres altérés, JPQL (CA-08)", "Négation d'une validation (CA-10)", "Énumération de comptes (CA-05)", "Rafales (CA-11)", "IDOR, autre établissement (CA-06)"],
         ["Service d'émission", "Faux établissement (CA-04)", "Diplôme de complaisance (CA-04)", "Validation niée (CA-10)", "—", "Lots géants (CA-11)", "Auto-validation (CA-04)"],
         ["Moteur de dissimulation", "Filigrane imité (CA-01)", "Retouche, greffe de marques (CA-02)", "—", "Sceau lu sans clé (CA-09)", "Image bombe (CA-08)", "—"],
         ["Vérification publique", "Copie usurpée (CA-03)", "Empreinte effacée (CA-07)", "—", "Oracle, collecte (CA-07, CA-09)", "Saturation (CA-11)", "—"],
         ["Base / stockage", "—", "Réactivation d'un révoqué (CA-10)", "—", "Vol de base, clés (CA-06)", "Saturation", "Accès direct par initié (CA-10)"],
         ["Journaux d'audit", "—", "Suppression de lignes (CA-10)", "Traces effacées (CA-10)", "Données personnelles en clair (CA-09)", "Saturation des logs", "Admin modifiant l'audit (CA-10)"]],
        [3.2, 2.37, 2.37, 2.37, 2.37, 2.36, 2.36], small=True)
d.H2("Matrice des risques")
d.P("Vraisemblance (V) et impact (I) sont cotés de 1 à 4 ; niveau = <b>V × I</b> : ≥ 9 élevé, 5 à 8 moyen, ≤ 4 faible. Tolérance retenue : <b>aucun risque élevé ne doit subsister</b> "
    "après traitement, et tout risque moyen doit être réduit par au moins une exigence P1 ou P2.")
d.table([["Risque", "CA", "Scénario", "V", "I", "V×I", "Niveau"]] +
        [[r[0], r[1], r[2], r[3], r[4], r[3] * r[4], f"<b>{lvl(r[3] * r[4])}</b>"] for r in D.RISKS],
        [1.4, 1.4, 9.2, 0.9, 0.9, 1.2, 2.4])
grid = [["V \\ I", "1 — mineur", "2 — modéré", "3 — grave", "4 — critique"]]
spans = []
for ri, v in enumerate([4, 3, 2, 1], start=1):
    row = [f"<b>{v}</b>"]
    for ci, i in enumerate([1, 2, 3, 4], start=1):
        row.append(", ".join(r[0] for r in D.RISKS if r[3] == v and r[4] == i))
        s = v * i
        col = colors.HexColor("#F5C6C2") if s >= 9 else colors.HexColor("#FCE8B2") if s >= 5 else colors.HexColor("#D9EFDD")
        spans.append(("BACKGROUND", (ci, ri), (ci, ri), col))
    grid.append(row)
d.table(grid, [2.2, 3.8, 3.8, 3.8, 3.8], spans=spans)
hi = [r[0] for r in D.RISKS if r[3] * r[4] >= 9]
d.P(f"{len(hi)} risques sont <b>élevés</b> ({', '.join(hi)}) : les trois fraudes métier, la prise de contrôle de compte, l'accès aux ressources d'autrui et les fichiers piégés. "
    "Ils donnent le poids le plus fort au critère « risque couvert » dans la priorisation (§ 9). R-04 (diplôme de complaisance) n'est « que » moyen en vraisemblance, mais son impact est critique. "
    "C'est pourquoi il bénéficie d'exigences P1 dédiées (double validation, MFA des émetteurs).")

# =====================================================================
d.H1("SQUARE étape 5 : techniques d'élicitation retenues")
d.P("SQUARE demande de choisir les techniques selon les objectifs, l'expertise des participants, le niveau de sécurité visé et le rapport coût/bénéfice. Les participants sont le binôme "
    "(parties prenantes, ingénieur des exigences, expert sécurité) et l'encadrant (rôle de client).")
d.table([["Technique", "Usage", "Justification (coût / bénéfice)"],
         ["Brainstorming et tableau blanc (binôme)", "Cas d'abus, récits d'abus", "Technique recommandée par le cours pour les cas d'abus ; coût nul ; adaptée à 2 participants"],
         ["Analyse des cas d'utilisation", "Point de départ (§ 3)", "Première action de l'élicitation selon le cours"],
         ["Analyse de cas réels de fraude", "Réalisme des mal-acteurs", "Affaires de faux diplômes rapportées par la presse ivoirienne : faux complets, usurpations, complicités internes"],
         ["Modélisation des menaces (STRIDE, arbres d'attaque)", "Exhaustivité", "Garantit qu'aucune famille de menace n'est oubliée sur un composant"],
         ["Checklists (OWASP Top 10 2025, ASVS 5.0 niveau 2)", "Contrôle de couverture", "Rattrape les exigences omises (faiblesse de SQUARE à l'élicitation)"],
         ["Revue documentaire", "Security drivers", "Énoncé, cours, loi n° 2013-450, RGPD, RFC"],
         ["Entretien avec l'encadrant (client)", "Validation du périmètre", "À mener en séance : périmètre binôme et niveau de détail attendus ; retours intégrés en v1.1"]],
        [4.8, 3.4, 9.2])

# =====================================================================
d.H1("SQUARE étapes 6–7 : exigences de sécurité élicitées et catégorisées", newpage=True)
d.H2("Principes de rédaction")
d.P("Chaque exigence respecte les critères <b>SMART</b> du cours : <b>S</b>pécifique (algorithme, seuil, endpoint nommés), <b>M</b>esurable (méthode de vérification indiquée), "
    "<b>A</b>ctionnable, <b>R</b>éaliste (outillage Jakarta EE / WildFly disponible) et <b>T</b>emporellement priorisée (P1/P2/P3, chapitre du cours). Elles sont classées dans les deux catégories du cours :")
d.L(["<b>exigences de sécurité fonctionnelles</b>, liées au métier : AUT, AUZ, CON, INT, NRP, DIM, LOG, ERR, DIS ;",
     "<b>directives de sécurité (security drivers)</b>, issues de lois, normes et politiques : loi n° 2013-450 et RGPD (PRV), OWASP ASVS niveau 2 (référence transverse), "
     "pratiques imposées par l'énoncé et le cours (TST, DEP)."])
d.P("L'étape 7 de SQUARE distingue aussi le <b>niveau</b> (système, logiciel, processus) et sépare les vraies exigences des simples contraintes :")
cc = Counter(r[0].split("-")[1] for r in D.SEC)
d.table([["Code", "Catégorie", "Chapitre du cours", "Niveau", "Nb"]] + [[c[0], c[1], c[2], c[3], cc[c[0]]] for c in D.CATS] +
        [["", "<b>Total</b>", "", "", f"<b>{NS}</b>"]], [1.4, 8.4, 2.6, 3.8, 1.2])
d.box("le socle Jakarta EE 11 / WildFly 42 / Java 25 et le type d'application PWA/SPA, imposés par l'énoncé, encadrent les exigences sans en être.", "Contraintes (non-exigences)", kind="info")
INTRO = {
    "AUT": "Protègent l'identité des acteurs, en priorité celle des émetteurs : un compte d'agent volé permet d'émettre des diplômes (OS-5, CA-05).",
    "AUZ": "Garantissent que chaque acteur n'agit que sur ce qui lui revient, et qu'aucune émission ne dépend d'une seule personne (OS-4, CA-04, CA-06).",
    "CON": "Protègent les clés, les documents et la table des partages ; les clés ne quittent jamais le serveur (CA-01, CA-03, CA-06).",
    "INT": "Empêchent l'injection de contenu malveillant, en particulier par les PDF déposés (CA-08).",
    "NRP": "Rendent chaque émission, révocation et vérification prouvable (OS-7, CA-10).",
    "DIM": "Exigences propres au métier : elles protègent le filigrane, le sceau et l'empreinte, et fixent la règle du verdict (OS-1, OS-2, OS-3).",
    "PRV": "Directives issues de la loi n° 2013-450 et du RGPD : minimisation, absence de recherche publique, transparence envers le titulaire (OS-6).",
    "LOG": "Permettent de détecter les fraudes internes et de reconstituer les faits (OS-7) ; détaillées au chapitre 5.",
    "ERR": "Couvrent la catégorie A10:2025 : ne rien révéler et échouer en mode sûr, un « indéterminé » ne devient jamais « authentique ».",
    "DIS": "Garantissent la disponibilité de la vérification face aux abus (OS-8, CA-11).",
    "TST": "Exigences de processus : elles vérifient en continu que les autres exigences sont respectées (chapitre 6).",
    "DEP": "Exigences de déploiement et de maintenance : durcissement, secrets, correctifs, rotation des clés (chapitre 7).",
}
for c in D.CATS:
    rows = [r for r in D.SEC if r[0].split("-")[1] == c[0]]
    d.H2(f"{c[1]} ({c[0]}) — {c[2]}")
    d.P(INTRO[c[0]])
    d.table([["ID", "Exigence", "Origine", "Prio", "Vérification", "OWASP / ASVS"]] +
            [[r[0], r[1], r[2], f"<b>{PRIO[r[0]][1]}</b>", r[4], f"{r[5]}<br/>{r[6]}"] for r in rows],
            [2.05, 7.05, 1.7, 1.0, 3.6, 2.0], small=True, keep=False)

# =====================================================================
d.H1("SQUARE étape 8 : priorisation (AHP)", newpage=True)
d.P("Le cours cite trois méthodes de priorisation pour SQUARE : <b>AHP</b>, Triage et Win-Win. Nous utilisons l'<b>AHP</b> (<i>Analytic Hierarchy Process</i>) pour fixer objectivement "
    "le <b>poids des critères</b>, puis un <b>triage</b> en trois classes. L'AHP compare les critères deux à deux sur l'échelle de Saaty (1 = importance égale, 3 = modérément plus important, "
    "5 = nettement plus important).")
d.H2("Critères et matrice de comparaison")
w, lmax, ci, cr = D.ahp_weights()
M = D.AHP_MATRIX
fmt = lambda x: f"{x:.0f}" if abs(x - round(x)) < 1e-9 else f"1/{round(1 / x)}"
d.table([["", "R — risque couvert", "C — obligation", "F — facilité", "Poids w"]] +
        [[D.AHP_CRITERIA[i]] + [fmt(M[i][j]) for j in range(3)] + [f"<b>{w[i]:.3f}</b>"] for i in range(3)],
        [5.2, 3.2, 3.0, 3.0, 3.0])
d.L(["<b>R — risque couvert</b> : 3 si l'exigence traite un risque élevé, 2 si moyen, 1 si faible ou indirect ;",
     "<b>C — obligation</b> : 3 si imposée par une loi, par le cours ou par l'ASVS niveau 2, 2 si recommandée, 1 si choix de l'équipe ;",
     "<b>F — facilité</b> : 3 si native dans Jakarta EE / WildFly, 2 si quelques jours de travail, 1 si effort important."])
d.P(f"Les poids sont obtenus par le vecteur propre principal : λ<sub>max</sub> = {lmax:.3f}, indice de cohérence CI = {ci:.3f}, <b>ratio de cohérence CR = {cr:.3f}</b> "
    "(indice aléatoire RI = 0,58 pour n = 3). CR &lt; 0,10 : les jugements sont <b>cohérents</b>. Le risque pèse près des deux tiers de la décision : c'est une priorisation "
    "<b>fondée sur le risque</b>, comme celle que recommande OWASP SAMM (chapitre 1).")
d.H2("Règle de triage et résultat")
d.P("Score = w<sub>R</sub>·R + w<sub>C</sub>·C + w<sub>F</sub>·F (entre 1 et 3). <b>P1</b> si score ≥ 2,50 (implémentée au chapitre correspondant, bloquante pour la release) ; "
    "<b>P2</b> si 1,90 ≤ score &lt; 2,50 (implémentée avant la fin du module) ; <b>P3</b> sinon (implémentée si le temps le permet, sinon reportée et documentée).")
pr = D.prioritized(); pc = Counter(p for _, _, p in pr)
d.table([["Classe", "Nombre", "Exigences"]] +
        [[f"<b>{k}</b>", pc[k], ", ".join(r[0].replace("SR-", "") for r, s, p in pr if p == k)] for k in ["P1", "P2", "P3"]],
        [1.6, 1.6, 14.2], small=True)
d.P("Le détail des notes (R, C, F) et du score de chaque exigence figure dans <b>docs/exigences.csv</b>, ce qui permet de rejouer la priorisation à chaque évolution. "
    "Une exigence P3 n'est jamais supprimée : elle reste au référentiel avec son statut.")

# =====================================================================
d.H1("SQUARE étape 9 : inspection et traçabilité", newpage=True)
d.H2("Inspection des exigences")
d.P("Chaque exigence est relue par le membre du binôme qui ne l'a pas rédigée (revue par les pairs, inspiration Fagan), selon la grille suivante :")
d.table([["Point de contrôle", "Question posée", "Résultat v1.0"],
         ["Non-ambiguïté", "Deux développeurs l'implémenteraient-ils de la même façon ?", "Formulations vagues reprises avec des seuils (ex. « contrôler l'émission » → « valideur différent du préparateur »)"],
         ["Testabilité", "Une méthode de vérification est-elle donnée ?", f"{NS}/{NS} exigences avec méthode de vérification"],
         ["Traçabilité", "Est-elle rattachée à un CA, un risque, un actif ou un driver ?", f"{NS}/{NS} rattachées (colonne « Origine »)"],
         ["Non-généricité", "Est-elle propre à EburSeal (critère de l'énoncé) ?", "Exigences génériques remplacées par des règles métier précises"],
         ["Absence de mécanisme dans les CS", "Les CS décrivent-ils le « quoi » et non le « comment » ?", "Conforme : mécanismes uniquement dans les SR"],
         ["Conflits", "Contredit-elle une autre exigence ou un besoin fonctionnel ?", "6 conflits identifiés et résolus (ci-dessous)"]],
        [3.6, 6.0, 7.8])
d.H3("Conflits détectés et décisions")
d.table([["Conflit", "Décision et justification"],
         ["Vérification publique ouverte à tous (BF-VER-01) <b>vs</b> protection des données (OS-6) et anti-oracle",
          "Vérification maintenue, mais <b>uniquement à partir du document</b> (SR-PRV-02), limitée à 10/h/IP et sans score (SR-DIM-09)"],
         ["Détection des copies hors contexte (BF-FP-03) <b>vs</b> confidentialité du destinataire",
          "Le destinataire n'est jamais révélé publiquement (SR-DIM-08) ; seuls le titulaire et l'organisation destinataire le voient"],
         ["Traçage des fuites (fingerprinting) <b>vs</b> minimisation (SR-PRV-01)",
          "La table des partages ne contient que ce qui est nécessaire (destinataire, finalité, dates) et est chiffrée (SR-CON-03)"],
         ["Fermeture du compte titulaire (BF-CPT-05) <b>vs</b> conservation du registre",
          "Le diplôme reste au registre de l'établissement (obligation de l'émetteur) ; seuls le compte, les partages et l'historique du titulaire sont supprimés"],
         ["MFA obligatoire pour tous <b>vs</b> ergonomie (OM-4)",
          "MFA <b>obligatoire</b> pour émetteurs, administrateur, auditeur ; <b>proposé</b> aux titulaires et vérificateurs (SR-AUT-03)"],
         ["Échec en mode sûr (SR-ERR-02) <b>vs</b> disponibilité (OS-8)",
          "La sécurité prime : en cas de doute, « indéterminé ». La disponibilité est assurée en amont par les quotas et délais maximaux (SR-DIS-01, 02)"]],
        [7.0, 10.4], small=True)
d.H2("Matrice de traçabilité")
d.P("La matrice relie chaque menace à ses exigences et au test qui démontre l'échec de l'attaque (SR-TST-04). Elle est complétée à chaque séance avec les liens vers les tests du dépôt.")
risk_of = {r[1]: r for r in D.RISKS}
CH = {"CA-01": "3", "CA-02": "3", "CA-03": "3", "CA-04": "4", "CA-05": "4", "CA-06": "4", "CA-07": "3", "CA-08": "3", "CA-09": "4", "CA-10": "5", "CA-11": "3"}
d.table([["CA", "Risque (niveau)", "CS", "Exigences P1", "Autres exigences", "Test d'abus prévu", "Ch."]] +
        [[a["id"], f"{risk_of[a['id']][0]} ({lvl(risk_of[a['id']][3] * risk_of[a['id']][4])})", a["cs"],
          ", ".join(x.replace("SR-", "") for x in bycs[a["cs"]] if PRIO[x][1] == "P1") or "—",
          ", ".join(x.replace("SR-", "") for x in bycs[a["cs"]] if PRIO[x][1] != "P1") or "—",
          f"AbuseCase{a['id'][3:]}IT", CH[a["id"]]] for a in D.ABUSE],
        [1.3, 2.3, 1.2, 4.2, 4.2, 2.9, 1.3], small=True, keep=False)
d.H2("Couverture de l'OWASP Top 10 2025")
d.P("Contrôle de couverture (checklist de l'étape 5) : chaque catégorie de l'OWASP Top 10 2025 est traitée par au moins une exigence.")
T10 = [("A01", "Broken Access Control"), ("A02", "Security Misconfiguration"), ("A03", "Software Supply Chain Failures"),
       ("A04", "Cryptographic Failures"), ("A05", "Injection"), ("A06", "Insecure Design"), ("A07", "Authentication Failures"),
       ("A08", "Software or Data Integrity Failures"), ("A09", "Security Logging &amp; Alerting Failures"), ("A10", "Mishandling of Exceptional Conditions")]
d.table([["Catégorie 2025", "Nb", "Exigences"]] +
        [[f"{c} — {n}", len([r for r in D.SEC if c in r[5]]), ", ".join(r[0].replace("SR-", "") for r in D.SEC if c in r[5])] for c, n in T10],
        [5.6, 1.0, 10.8], small=True)

# =====================================================================
d.H1("Gestion des exigences (évolution du recueil)")
d.P("Le cours fait de la <b>gestion</b> la quatrième phase de l'IES, avec une erreur à éviter : des exigences non priorisées ou mal planifiées. L'énoncé précise que ce recueil évoluera. "
    "Nous appliquons donc le processus suivant :")
d.L(["<b>Déclencheur</b> : nouveau chapitre, nouvelle menace, test en échec, résultat du prototype ou retour de l'encadrant → issue GitHub (modèle security-story) ;",
     "<b>Analyse d'impact</b> : actifs, cas d'abus, autres exigences et tests concernés ; vérification de l'absence de conflit (§ 10.1) ;",
     "<b>Mise à jour du référentiel unique</b> (docs/src/data.py) : ajout, modification ou passage au statut « Obsolète » (une exigence n'est jamais effacée) ;",
     "<b>Régénération</b> des PDF et du CSV (docs/src/build.sh), nouvelle version (1.1, 1.2…) et ligne d'historique ;",
     "<b>Revue</b> par l'autre membre via pull request, puis tag de séance."])
d.table([["Statut", "Signification"],
         ["Proposée", "Issue ouverte, pas encore analysée"],
         ["Spécifiée", "Rédigée, inspectée et priorisée (statut de toutes les exigences en v1.0)"],
         ["Implémentée", "Code fusionné sur develop, référencé dans la PR"],
         ["Vérifiée", "Test automatisé vert ; lien vers le test dans la matrice de traçabilité"],
         ["Obsolète", "Remplacée ou sans objet ; conservée pour l'historique avec sa justification"]],
        [3.2, 14.2])
d.box("les seuils de SR-DIM-04 (PSNR, robustesse) seront confirmés ou ajustés par le prototype du moteur au jalon J2 ; ce sera la première évolution du recueil (v1.1). "
      "Les exigences P1 de chaque chapitre doivent passer « Vérifiées » avant le tag de ce chapitre.", "Engagement", kind="ok")

d.build()
D.export_csv(str(HERE.parent / "exigences.csv"))
print("OK", out)

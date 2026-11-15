"""Cahier conceptuel (phase 2) — conception sécurisée et modélisation des menaces d'EburSeal."""
import sys, pathlib
from vmpdf import Doc, W
import data as D
import cco_data as C
import re

HERE = pathlib.Path(__file__).parent
out = sys.argv[1] if len(sys.argv) > 1 else str(HERE.parent / "cahier_conceptuel.pdf")
d = Doc(out, "Cahier conceptuel", "Conception sécurisée et modélisation des menaces", C.VERSION, "cco")

d.cover([
    ("Projet", "EburSeal — plateforme de délivrance et de vérification de diplômes infalsifiables (Côte d'Ivoire)"),
    ("Équipe (binôme)", D.TEAM),
    ("Formation", "SUP'COM — 3<super>e</super> année cycle ingénieur, option Cybersecurity and Defense (CySeD)"),
    ("Module / encadrant", "Sécurité Applicative — Dr. Ing. Mohamed-Becha Kaâniche"),
    ("Phase de l'atelier", "Phase 2 — Conception sécurisée (séance 2 du cours : modélisation des menaces)"),
    ("Documents d'entrée", "docs/cahier_des_charges.pdf · docs/recueil_des_besoins.pdf · docs/exigences.csv"),
    ("Version / date", f"v{C.VERSION} — {C.DATE}"),
], [["1.0", "15/11/2026", "Y. T. Daouda", "Premier jet"], [C.VERSION, C.DATE, "O. Yacouba, Y. T. Daouda", "Corrections suite à la relecture croisée de O. Yacouba (8 points) : Argon2id et QIM, seuils de T-T1, verdicts, articulation AHP, état réel de la CI, menaces sur P5, DS2 et CSRF, DFD complété"]])
d.h1_break = False

N = len(C.T)
crit = sum(1 for t in C.T if C.rate(t)[4] == "Critique")

# =====================================================================
d.H1("Objectifs de la conception sécurisée", newpage=True)
d.H2("Objet du document")
d.P("La phase 1 a spécifié <b>ce que</b> EburSeal doit garantir : 11 cas d'abus, 71 exigences de sécurité SMART priorisées par AHP. "
    "Ce cahier conceptuel décrit <b>comment</b> la conception y répond : il décompose l'application, identifie méthodiquement les menaces "
    "qui pèsent sur sa pile technique (Java 25, Jakarta EE 11, WildFly 42) et sur son moteur de dissimulation, évalue leur risque, "
    "puis associe à chacune des contre-mesures natives ou applicatives et les patrons de conception qui les portent.")
d.P(f"Résultat : <b>{N} menaces contextualisées</b>, chacune rattachée à un élément du diagramme de flux, à un cas d'abus de la phase 1, "
    "à une référence CAPEC ou CWE lorsqu'elle existe, et aux exigences SR-xx qui la traitent. La traçabilité phase 1 → phase 2 est donc complète.")
d.H2("Objectifs de sécurité")
d.L(["<b>Origine</b> : seul un établissement validé peut produire un diplôme jugé authentique (cas d'abus CA-01, CA-04) ;",
     "<b>Intégrité</b> : toute modification du contenu d'un diplôme émis est détectée (CA-02) ;",
     "<b>Traçabilité des copies</b> : chaque copie est liée à son destinataire, sans exposer la vie privée du titulaire (CA-03, CA-09) ;",
     "<b>Responsabilité</b> : chaque émission, validation et révocation est imputable et non répudiable (CA-10) ;",
     "<b>Disponibilité</b> : la vérification résiste aux fichiers piégés et aux rafales de requêtes (CA-08, CA-11)."])
d.H2("Actifs à protéger (repris de la phase 1)")
d.table([["Actif", "Description", "C", "I", "D"]] +
        [[f"{a[0]} — {a[1]}", a[2], str(a[3]), str(a[4]), str(a[5])] for a in D.ASSETS],
        [4.6, 10.4, 0.8, 0.8, 0.8])
d.P("Échelle de besoin de 1 (faible) à 4 (critique). Les actifs A2 (clés), A4 (identifiants) et A6 (table des partages) "
    "sont les plus exposés : leur compromission rendrait toute marque contrefaisable ou toute copie intraçable.")

# =====================================================================
d.H1("Revue de l'application")
d.H2("Décomposition : diagramme de flux de données")
d.P("La revue part de l'architecture du cahier des charges, redessinée sous forme de diagramme de flux de données (DFD). "
    "Chaque élément y est un candidat à l'analyse STRIDE ; chaque flux qui franchit une <b>frontière de confiance</b> (pointillés) "
    "est un point où l'attaquant peut injecter, intercepter ou usurper.")
d.img(str(HERE / "diagrams" / "dfd.png"), W * 0.9, "Figure 1 — Diagramme de flux de données d'EburSeal et frontières de confiance")
d.table([["Élément", "Type", "Rôle", "Frontière"]] + [[e[0], e[1], e[2], e[3]] for e in C.ELEMENTS], [1.4, 3.0, 11.2, 1.8])
d.H2("Frontières de confiance")
d.table([["Frontière", "Limite", "Règle de conception"]] + [[b[0], b[1], b[2]] for b in C.BOUNDARIES], [1.8, 5.0, 10.6])
d.H2("Points d'entrée")
d.L(["<b>Authentification</b> : /api/auth/{activate, login, refresh, logout, reset, mfa} — exposés à Internet (TB1) ;",
     "<b>Émission</b> : /api/diplomas, …/{id}/validate, …/{id}/revoke, /api/batches — dépôt de fichiers (TB3) ;",
     "<b>Vérification</b> : /api/verify — public, anonyme, coûteux en calcul : le point d'entrée le plus exposé ;",
     "<b>Titulaire et vérificateur</b> : /api/wallet, /api/shares, /api/inbox, /api/reports — accès à des ressources nominatives ;",
     "<b>Administration</b> : /api/admin/**, /api/audit/** — et l'interface de management de WildFly (port 9990), à ne jamais exposer ;",
     "<b>Chaîne de production</b> : dépôt GitHub, pull requests, dépendances Maven et npm (X1)."])

# =====================================================================
d.H1("Méthode d'analyse des menaces")
d.H2("Choix de la méthode")
d.P("Nous retenons <b>STRIDE appliqué élément par élément</b> du DFD (le modèle présenté en cours), complété par les références "
    "<b>CAPEC</b> (profils d'attaque) et <b>CWE</b> (faiblesses), et par un passage <b>LINDDUN</b> ciblé sur la vie privée (section 8).")
d.table([["Méthode", "Ce qu'elle apporte", "Décision pour EburSeal"],
         ["STRIDE", "Couverture systématique des 6 propriétés (authentification, intégrité, non-répudiation, confidentialité, disponibilité, autorisation) sur chaque élément",
          "<b>Retenue</b> comme méthode principale"],
         ["CAPEC / CWE", "Ancrage de chaque menace dans une base de connaissance mondiale, et donc vérifiable",
          "<b>Retenue</b> en référence de chaque menace"],
         ["PASTA", "7 étapes centrées sur le risque métier et la simulation d'attaques",
          "Non retenue : l'alignement métier est déjà assuré par SQUARE et les cas d'abus (phase 1), et l'impact métier est noté par OWASP Risk Rating ; PASTA serait disproportionné pour un binôme"],
         ["LINDDUN", "Menaces sur la vie privée", "<b>Retenue en complément</b>, limitée à l'actif A8 (données des titulaires)"]],
        [2.6, 7.2, 7.6])
d.H2("Format de documentation d'une menace")
d.P("Chaque menace suit le modèle du cours : description, cible, technique d'attaque, cote de risque, contre-mesures. "
    "La cote est laissée vide à l'identification (section 4) et calculée à l'évaluation (section 5).")
d.box("une menace est rejetée si elle ne nomme pas un élément précis d'EburSeal, une technique d'attaque réaliste et une conséquence "
      "sur un actif identifié. Les formulations génériques (« mot de passe faible », « sécuriser l'API ») sont exclues.",
      "Règle de rédaction")

# =====================================================================
d.H1("Matrice STRIDE contextualisée")
d.H2("Vue d'ensemble : menaces par élément")
letters = ["S", "T", "R", "I", "D", "E"]
rows = [["Élément"] + letters]
for e in C.ELEMENTS:
    ids = [", ".join(t["id"].replace("T-", "") for t in C.T if t["el"] == e[0] and t["s"] == L) or "—" for L in letters]
    rows.append([e[0]] + ids)
d.table(rows, [2.0] + [2.566] * 6)
d.P("Lecture : S = usurpation, T = falsification, R = répudiation, I = divulgation, D = déni de service, E = élévation de privilèges. "
    "Les cases vides ont été examinées : aucune menace réaliste n'y a été retenue.", "note")

names = {"S": "Spoofing — usurpation d'identité (authentification)", "T": "Tampering — falsification (intégrité)",
         "R": "Repudiation — répudiation (non-répudiation)", "I": "Information disclosure — divulgation (confidentialité)",
         "D": "Denial of service — déni de service (disponibilité)", "E": "Elevation of privilege — élévation de privilèges (autorisation)"}
for L in letters:
    d.H2(names[L])
    d.table([["ID", "Menace (description, cible)", "Technique d'attaque", "Réf. / CA"]] +
            [[t["id"], f"<b>{t['titre']}</b> ({t['el']}). {t['desc']}", t["tech"], f"{t['ref']}<br/>{t['ca']}"]
             for t in C.T if t["s"] == L],
            [1.3, 10.0, 3.4, 2.7], keep=False, small=True)

# =====================================================================
d.H1("Évaluation et priorisation des risques")
d.H2("Pourquoi DREAD n'est pas retenu")
d.P("Le cours présente DREAD (Dommages, Reproductibilité, Exploitabilité, utilisateurs Affectés, Découvrabilité), noté de 1 à 3 sur chaque critère. "
    "Nous l'écartons pour cinq raisons :")
d.L(["<b>Subjectivité</b> : les niveaux ne sont pas définis par des critères observables ; deux analystes notent différemment la même menace, "
     "et un même analyste varie d'une séance à l'autre. Le score n'est donc pas reproductible ;",
     "<b>Découvrabilité</b> : le critère récompense l'obscurité. Une faille « difficile à trouver » voit son risque baisser, alors qu'un attaquant "
     "motivé (ici, un réseau de faussaires) finira par la trouver : c'est de la sécurité par l'obscurité ;",
     "<b>Mélange des dimensions</b> : la somme additionne des critères de vraisemblance (R, E, D) et d'impact (D, A) avec le même poids, "
     "au lieu de croiser vraisemblance et impact comme le prévoit la formule du cours (cote = probabilité × dommages) ;",
     "<b>Échelle saturée</b> : avec 5 critères notés de 1 à 3, la plupart des menaces sérieuses tombent en « High ». Dans l'exemple du cours, "
     "l'écoute réseau (12) et l'injection SQL (14) reçoivent la même cote, ce qui n'aide pas à prioriser ;",
     "<b>Abandon par son créateur</b> : Microsoft, qui avait introduit DREAD, a cessé de l'utiliser dans son propre cycle de développement sécurisé. "
     "La méthode est considérée comme obsolète."])
d.H2("Méthode retenue : OWASP Risk Rating")
d.P("OWASP Risk Rating répond à ces défauts : chaque facteur est noté de 0 à 9 sur une <b>échelle décrite</b>, la vraisemblance et l'impact "
    "sont évalués <b>séparément</b>, puis croisés dans une matrice. Surtout, il intègre l'<b>impact métier</b> (réputation, conformité, vie privée), "
    "décisif pour EburSeal : une seule fraude réussie détruit la confiance dans tous les diplômes de la plateforme.")
d.table([["Dimension", "Facteurs (notés de 0 à 9)"],
         ["Vraisemblance — agent de menace", "Compétence requise (SK), motivation (MO), opportunité (OP), taille du groupe d'attaquants (SZ)"],
         ["Vraisemblance — vulnérabilité", "Facilité de découverte (ED), facilité d'exploitation (EE), notoriété (AW), détection d'intrusion (ID)"],
         ["Impact technique", "Confidentialité (C), intégrité (I), disponibilité (A), traçabilité (AC)"],
         ["Impact métier", "Financier (FD), réputation (RD), non-conformité (NC), atteinte à la vie privée (PV)"]],
        [5.0, 12.4])
d.P("Vraisemblance = moyenne des 8 facteurs ; impact = moyenne de l'impact technique et de l'impact métier, en retenant le plus défavorable des deux. "
    "Chaque moyenne est classée Faible (&lt; 3), Moyen (3 à &lt; 6) ou Élevé (≥ 6), puis la sévérité est lue dans la matrice OWASP :")
d.table([["Impact \\ Vraisemblance", "Faible", "Moyenne", "Élevée"],
         ["Élevé", "Moyenne", "Élevée", "Critique"],
         ["Moyen", "Faible", "Moyenne", "Élevée"],
         ["Faible", "Note", "Faible", "Moyenne"]], [5.0, 4.13, 4.13, 4.13])
d.box("les notes décrivent le risque <b>inhérent</b>, c'est-à-dire l'application sans les contre-mesures prévues, car c'est ce risque qui justifie "
      "chaque contre-mesure. La colonne « risque résiduel » donne le niveau attendu une fois les exigences SR-xx implémentées ; il sera "
      "confirmé par les tests d'abus (SR-TST-04).", "Risque inhérent et risque résiduel")

ex = next(t for t in C.T if t["id"] == "T-D1")
Lx, Itx, Ibx, Ix, Sx = C.rate(ex)
d.H2("Exemple détaillé : T-D1, saturation de la heap par un PDF piégé")
lab = ["SK", "MO", "OP", "SZ", "ED", "EE", "AW", "ID"]
just = ["outil public pour forger le PDF", "nuire, sans gain direct", "portail public, aucun compte", "tout Internet",
        "comportement de PDFBox documenté", "un fichier suffit", "attaque connue", "erreur visible, pas d'alerte dédiée"]
d.table([["Facteur", "Note", "Justification"]] + [[lab[i], str(ex["L"][i]), just[i]] for i in range(8)] +
        [["<b>Vraisemblance</b>", f"<b>{Lx:.2f}</b>", f"<b>{C.level(Lx)}</b>"]], [3.0, 2.0, 12.4], keep=True)
d.table([["Impact", "Notes", "Moyenne"],
         ["Technique (C, I, A, AC)", " / ".join(map(str, ex["It"])), f"{Itx:.2f}"],
         ["Métier (FD, RD, NC, PV)", " / ".join(map(str, ex["Ib"])), f"{Ibx:.2f}"],
         ["<b>Impact retenu</b>", "le plus défavorable", f"<b>{Ix:.2f} — {C.level(Ix)}</b>"]], [5.0, 6.4, 6.0])
d.P(f"Vraisemblance {C.level(Lx).lower()} × impact {C.level(Ix).lower()} → sévérité inhérente <b>{Sx}</b>. "
    "Les contre-mesures (dimensions lues avant le rendu, file bornée, redémarrage automatique) ramènent le risque résiduel à <b>faible</b>.")

d.H2("Résultats pour l'ensemble des menaces")
rated = sorted(C.T, key=lambda t: (C.ORDER[C.rate(t)[4]], -C.rate(t)[0]))
d.table([["ID", "Menace", "Vrais.", "Impact", "Sévérité inhérente", "Résiduel"]] +
        [[t["id"], t["titre"], f"{C.rate(t)[0]:.1f}", f"{C.rate(t)[3]:.1f}", C.rate(t)[4], t["resid"]] for t in rated],
        [1.3, 8.4, 1.5, 1.5, 2.6, 2.1], keep=False, small=True)
crit_names = ", ".join(f"{t['id']} ({t['titre'][0].lower() + t['titre'][1:]})" for t in rated if C.rate(t)[4] == "Critique")
nres = sum(1 for t in C.T if t["resid"].startswith("Moyen"))
d.P(f"{crit} menaces sont critiques avant contre-mesures : {crit_names}. Elles sont traitées en priorité, dès le chapitre 3 du cours. "
    f"{nres} risques résiduels restent <b>moyens</b> : ils sont discutés en section 9.")

d.H2("Articulation avec la priorisation AHP de la phase 1")
d.P("Les deux méthodes ne notent pas la même chose. L'<b>AHP</b> de la phase 1 classe les <b>exigences</b> (P1, P2, P3) selon trois critères pondérés : "
    "risque couvert (0,637), obligation (0,258) et facilité (0,105), avec un ratio de cohérence de 0,033. <b>OWASP Risk Rating</b> note ici les <b>menaces</b>. "
    "Elles s'articulent ainsi : la sévérité d'une menace alimente le critère « risque couvert » des exigences qui la traitent. "
    "Règle de cohérence : toute menace de sévérité critique ou élevée doit être couverte par au moins une exigence P1.")
PR = {r[0]: p for r, sc, p in D.prioritized()}
chk = []
for t in rated:
    if C.rate(t)[4] in ("Critique", "Élevée"):
        ids = re.findall(r"SR-[A-Z]+-\d+", t["sr"])
        best = min((PR.get(i, "P3") for i in ids), default="—")
        chk.append((t, ids, best))
gaps = [(t, ids, b) for t, ids, b in chk if b != "P1"]
d.P(f"Vérification : {len(chk) - len(gaps)} des {len(chk)} menaces critiques ou élevées respectent cette règle. Les écarts sont :")
d.table([["Menace", "Sévérité", "Exigences et priorité AHP", "Décision"]] +
        [[t["id"] + " " + t["titre"], C.rate(t)[4], ", ".join(f"{i} ({PR.get(i, '?')})" for i in ids),
          "Reclasser " + ids[0] + " en P1"] for t, ids, b in gaps],
        [6.0, 2.2, 5.6, 3.6])
d.P("Ces reclassements, reportés dans le recueil v1.1, illustrent la gestion des exigences : la modélisation des menaces de la phase 2 "
    "corrige la priorisation de la phase 1.")
d.H2("Et CVSS ?")
d.P("CVSS note une <b>vulnérabilité existante</b> dans un logiciel déployé (vecteur d'attaque, complexité, privilèges requis…). Il ne mesure pas "
    "l'impact métier et s'applique mal à une menace de conception, qui n'a pas encore de code. Nous l'utilisons donc là où il est pertinent : "
    "dans la CI, l'analyse des dépendances bloque toute bibliothèque affectée d'une vulnérabilité de score CVSS ≥ 7 (SR-TST-02), et les failles "
    "trouvées en tests de sécurité (chapitre 6) seront notées en CVSS.")

# =====================================================================
d.H1("Contre-mesures")
d.P("Pour chaque menace, on distingue les contre-mesures <b>natives</b>, fournies par la plateforme (Jakarta EE 11, WildFly 42, Java 25), "
    "et les contre-mesures <b>applicatives</b>, que nous développons. Privilégier le natif réduit le code de sécurité écrit à la main, donc les erreurs.")
d.table([["ID", "Natives (plateforme)", "Applicatives (EburSeal)", "Exigences"]] +
        [[t["id"], t["nat"], t["app"], t["sr"]] for t in C.T],
        [1.3, 4.6, 8.3, 3.2], keep=False, small=True)
d.H2("Mécanismes natifs de la pile mobilisés")
d.table([["Mécanisme", "Composant", "Menaces traitées"],
         ["@RolesAllowed / @DenyAll, HttpAuthenticationMechanism", "Jakarta Security 4.0", "T-S1, T-S3, T-E1, T-E2"],
         ["Realms, TLS, credential store", "WildFly Elytron", "T-S1, T-I4"],
         ["max-post-size, délais, limitation des requêtes", "Undertow (WildFly)", "T-S2, T-D3, T-D4"],
         ["Validation déclarative des DTO", "Jakarta Validation 3.1", "T-T4, T-R3, T-E4"],
         ["Requêtes paramétrées, référentiels", "Jakarta Persistence 3.2 / Jakarta Data 1.0", "T-T4"],
         ["ManagedExecutorService à file bornée", "Jakarta Concurrency 3.1", "T-D1, T-D2, T-D3"],
         ["Sérialisation JSON sans désérialisation Java", "Jakarta JSON Binding / JSON Processing", "T-E4"],
         ["Ed25519, AES-256-GCM, SecureRandom", "JCA de Java 25", "T-S4, T-R1, T-I4"],
         ["Filtre de désérialisation (JEP 290), -XX:+ExitOnOutOfMemoryError", "JVM Java 25", "T-E4, T-D1"],
         ["Lecture d'en-tête avant décodage (ImageReader)", "javax.imageio", "T-D2"]],
        [6.2, 5.2, 6.0])

# =====================================================================
d.H1("Conception architecturale détaillée")
d.H2("Défense en profondeur, couche par couche")
d.P("Le cours rappelle qu'une sécurité à un seul niveau ne suffit pas. Chaque couche d'EburSeal porte ses propres contrôles, "
    "de sorte qu'une défaillance isolée ne suffit pas à compromettre un diplôme.")
d.table([["Couche", "Contrôles", "Exigences"],
         ["Navigateur (PWA)", "Jeton en mémoire, CSP stricte, aucun HTML injecté, cache limité aux ressources statiques", "SR-AUT-07, INT-05, CON-05"],
         ["Transport", "TLS 1.3, HSTS, anti-CSRF sur le seul endpoint à cookie", "SR-CON-01, INT-06"],
         ["Serveur (WildFly / Undertow)", "Taille des requêtes, délais, management sur 127.0.0.1, en-têtes de sécurité", "SR-DIS-03, DEP-01, DEP-03"],
         ["API (Jakarta REST + Security)", "Refus par défaut, rôles déclarés, limitation de débit, erreurs RFC 9457", "SR-AUZ-01, DIS-01, ERR-01"],
         ["Services métier", "Contrôle d'appartenance, double validation, quotas, verdict en mode sûr", "SR-AUZ-02 à 04, ERR-02"],
         ["Moteur de dissimulation", "File bornée, trois couches sur blocs disjoints, signature + chiffrement du sceau", "SR-DIS-02, DIM-01 à 06"],
         ["Données", "Chiffrement au repos, clés chiffrées par la clé maître, requêtes paramétrées, journal chaîné", "SR-CON-02, 03, INT-04, NRP-03"],
         ["Chaîne de production", "<b>Actifs</b> : revue croisée, CI (build et tests, Dependency-Check, npm audit, gitleaks), protection de main, Dependabot, CodeQL, push protection. <b>Prévus au chapitre 6</b> : SAST dans la CI (SpotBugs + FindSecBugs), DAST", "SR-TST-01 à 05"]],
        [3.8, 9.6, 4.0])
d.H2("Patrons de conception de sécurité")
d.table([["Patron", "Problème traité", "Mise en œuvre dans EburSeal", "Menaces"],
         ["Point d'accès unique (Single Access Point)", "Multiplication des chemins d'authentification", "Un seul HttpAuthenticationMechanism (JWT ES256) pour toute l'API", "T-S3"],
         ["Refus par défaut (Fail-safe defaults)", "Endpoint oublié", "@DenyAll au niveau de la classe, rôles explicites ; test de build", "T-E2"],
         ["Point d'application de la politique (Policy Enforcement Point)", "Contrôle d'appartenance dispersé ou oublié", "Intercepteur CDI @OwnershipCheck appliqué à toutes les ressources nominatives", "T-E1"],
         ["Double contrôle (Four-eyes / séparation des tâches)", "Émission frauduleuse par un initié", "Validateur ≠ préparateur ; administrateur sans droit d'émission ; auditeur en lecture seule", "T-E3, T-R2"],
         ["Objet de transfert de données (DTO)", "Affectation de masse", "Records Java en entrée, sans champ statut, propriétaire ni rôle", "T-T4"],
         ["Filtre d'interception (Intercepting Filter)", "Contrôles transverses oubliés", "ContainerRequestFilter : limitation de débit, identifiant de corrélation", "T-S2, T-D3"],
         ["Cloison étanche (Bulkhead)", "Un traitement coûteux bloque tout le serveur", "Pool d'exécution dédié et borné pour l'image, séparé des fils HTTP", "T-D1, T-D2, T-D3"],
         ["Désarmement et reconstruction (CDR)", "Contenu actif caché dans un fichier", "Rastérisation du PDF : seul un nouveau fichier reconstruit est conservé", "T-D1, T-I5"],
         ["Chiffrement d'enveloppe", "Fuite de la base", "Clé de données par établissement, chiffrée par la clé maître du credential store", "T-I4"],
         ["Journal sécurisé (Secure Logger)", "Effacement ou falsification des traces", "Entrées JSON chaînées par SHA-256, stockage en ajout seul", "T-R2, T-R3"],
         ["Échec sécurisé (Fail securely)", "Erreur interprétée comme succès", "Toute exception pendant une vérification donne « indéterminé », jamais « authentique »", "T-T1"]],
        [3.7, 3.6, 7.6, 2.5], keep=False, small=True)
d.H2("Chaîne de vérification sécurisée")
d.P("La vérification publique est le point d'entrée le plus exposé. Ses contrôles s'enchaînent du moins coûteux au plus coûteux : "
    "un fichier piégé est rejeté avant d'atteindre le décodeur, et toute erreur conduit à un refus.")
d.img(str(HERE / "diagrams" / "verify_pipeline.png"), W * 0.95, "Figure 2 — Ordre des contrôles de la vérification")
d.H2("Garantie à la compilation : le verdict en Java 25")
d.P("SR-DIM-05 définit trois verdicts : authentique, non authentique, indéterminé ; un diplôme révoqué est « non authentique », motif affiché (BF-EMI-04). "
    "Pour que « indéterminé » ne puisse jamais être traité comme « authentique » (SR-ERR-02), le verdict est un type scellé. "
    "Le compilateur de Java 25 impose alors de traiter chaque cas dans un switch : un cas oublié est une erreur de compilation, pas une faille.")
code = ["sealed interface Verdict permits Authentique, NonAuthentique, Indetermine {}",
        "record Authentique(UUID diplome, Instant emission) implements Verdict {}",
        "record NonAuthentique(Motif motif) implements Verdict {}  // MARQUES_ABSENTES, SIGNATURE_INVALIDE, REVOQUE…",
        "record Indetermine(String raison) implements Verdict {}",
        "",
        "String libelle = switch (verdict) {        // exhaustif, vérifié à la compilation",
        "    case Authentique a    -&gt; \"Diplôme authentique\";",
        "    case NonAuthentique n -&gt; \"Diplôme non authentique : \" + n.motif().libelle();",
        "    case Indetermine i    -&gt; \"Vérification impossible : document à contrôler\";",
        "};"]
d.box('<font name="M" size="8.3">' + "<br/>".join(l.replace(" ", "&nbsp;") for l in code) + "</font>", None)

# =====================================================================
d.H1("Complément vie privée (LINDDUN ciblé)")
d.P("EburSeal traite des données personnelles (actif A8) soumises à la loi ivoirienne n° 2013-450. STRIDE couvre la confidentialité, "
    "mais pas les atteintes propres à la vie privée ; nous appliquons donc LINDDUN aux seules catégories pertinentes.")
d.table([["Catégorie", "Menace", "Contre-mesure", "Exigences"]] + [list(x) for x in C.LINDDUN], [2.8, 5.8, 5.8, 3.0])

# =====================================================================
d.H1("Risques résiduels et suite")
d.H2("Risques résiduels")
d.table([["Menace", "Pourquoi le risque reste moyen", "Décision"],
         ["T-S1 Hameçonnage", "Un relais d'hameçonnage en temps réel peut intercepter un code TOTP", "Accepté pour le prototype ; WebAuthn (clé liée au domaine) prévu en évolution"],
         ["T-T1 Effacement des marques", "Une dégradation très forte (impression-numérisation de mauvaise qualité) peut rendre une marque illisible", "Accepté : le verdict devient « indéterminé », jamais « authentique » ; seuils mesurés au prototype"],
         ["T-T3 Collusion", "Une collusion de nombreuses copies peut brouiller une empreinte", "Accepté : limite de 30 partages ; codes de Tardos étudiés"],
         ["T-E3 Double validation", "Deux initiés complices peuvent émettre ensemble", "Accepté : alertes de volume et audit ; hors de portée d'un contrôle technique seul"],
         ["T-S5 Clé de signature", "Une clé volée avant sa rotation permet de signer des faux jusqu'à sa révocation", "Accepté : rotation planifiée, version de clé dans le sceau, procédure de révocation"]],
        [3.4, 7.0, 7.0])
d.box("pendant la phase 1, l'analyse des dépendances Java de la CI a échoué plusieurs heures car l'API de la NVD répondait HTTP 503. "
      "La chaîne de production dépend donc elle aussi de services externes. Mesures retenues : mise en cache de la base NVD dans la CI, "
      "et pluralité des sources (Dependency-Check, npm audit, Dependabot). Toute fusion malgré ce contrôle est justifiée par écrit dans la pull request.",
      "Incident observé")
d.H2("Décisions de conception à reporter dans le recueil (v1.1)")
d.table([["Décision", "Origine", "Effet sur la phase 1"],
         ["Insertion des marques par QIM, pas Δ calibré au prototype J2", "T-T1, relecture croisée", "Préciser le mécanisme dans SR-DIM-01 et SR-DIM-04"],
         ["Rotation et révocation des clés de signature d'établissement", "T-S5", "Nouvelle exigence SR-CON-06"],
         ["Nonce AES-GCM aléatoire de 96 bits, unicité testée", "T-I7", "Préciser SR-CON-04"],
         ["Reclassements en P1 issus de la vérification AHP (§ 5)", ", ".join(t["id"] for t, i, b in gaps), "Reclasser " + ", ".join(i[0] for t, i, b in gaps) + " : notes R à mettre à jour dans data.py"],
         ["Trois verdicts confirmés ; révocation = non authentique avec motif", "Relecture croisée", "Aucun changement : SR-DIM-05 inchangée"]],
        [6.6, 3.6, 7.2])
d.H2("Traçabilité et prochaines étapes")
d.L(["chaque menace T-xx devient une issue GitHub liée à son cas d'abus et à ses exigences, et ne sera close qu'avec un test d'abus (SR-TST-04) ;",
     "chapitre 3 : implémentation des contre-mesures des menaces critiques et du moteur DCT, avec le banc de robustesse ;",
     "chapitre 4 : authentification, autorisation (T-S1 à T-S3, T-E1 à T-E3) ;",
     "le modèle de menaces est revu à chaque nouvelle fonctionnalité et à chaque incident."])

d.build()
print("OK", out)

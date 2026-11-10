# 📑 Fiche d'Attribution, d'Intégrité Académique et d'Usage de l'IA

Ce document doit être obligatoirement complété, signé numériquement par chaque membre de l'équipe, et maintenu à jour à la racine du dépôt GitHub à chaque jalon.

> **Jalon couvert :** Phase 1 — Spécification & conception (tag `v0.2-ch2`), mise à jour du 09/11/2026.

---

## 👥 1. Identification de l'Équipe & Rôles

* **Établissement :** École Supérieure des Communications de Tunis (SUP'COM)
* **Année universitaire :** 2026–2027
* **Groupe / Trinôme ou Binôme N° :** Binôme 9
* **Nom de l'Application Métier :** EburSeal

### Membres de l'équipe :
1. **OUATTARA Yacouba** - Email : `yacouba.outtara@supcom.tn` - Rôle principal : Conception métier (sujet EburSeal), spécification SRE (cahier des charges, recueil des besoins, référentiel des exigences), squelette applicatif et CI initiale
2. **YEO Tanna Daouda** - Email : `tanna.yeo@supcom.tn` - Rôle principal : Revue croisée et assurance qualité, gestion du dépôt GitHub, CI/CD SecDevOps et configuration de sécurité du dépôt

---

## 📜 2. Déclaration d'Intégrité et d'Anti-Plagiat

Par la présente, nous certifions sur l'honneur que :
* L'architecture, la conception logicielle et l'implémentation métier de cette application sont le fruit de notre propre travail d'équipe.
* Aucun copier-coller de code, de diagrammes ou de documentations provenant d'un autre groupe de l'atelier n'a été effectué.
* Toute source externe (bibliothèques open-source, articles de recherche, documentation WildFly/Jakarta EE) a été correctement citée dans la documentation technique.

---

## 🤖 3. Déclaration de l'Usage des Intelligences Artificielles (IA)

Conformément aux directives de l'atelier, l'usage de l'IA (ChatGPT, Claude, GitHub Copilot, etc.) est autorisé exclusivement comme **assistant à la réflexion, à la structuration ou au débogage**, et non comme substitut à la production intellectuelle.

### 📊 Tableau de transparence IA (À compléter obligatoirement)

| Composant / Phase | IA utilisée (Nom/Version) | Pourcentage estimé de contenu généré | Rôle précis de l'IA & Prompts clés utilisés |
| :--- | :--- | :--- | :--- |
| **Choix et cadrage du sujet** (Y. Ouattara) | Claude Opus 5.5 (Anthropic) | ~5 % | L'idée (lutte contre la falsification des diplômes en Côte d'Ivoire) vient de l'équipe ; l'IA a aidé à faire ressortir le fingerprinting. Prompt : *« Comment mon sujet pourrait-il faire ressortir l'aspect Fingerprinting ? »* (→ un code aléatoire différent pour chaque copie et chaque destinataire). |
| **Phase 1 : Exigences (SRE)** (Y. Ouattara) | Claude Opus 5.5 (Anthropic) | ~30 % | Aide au choix de la méthodologie et brainstorming des exigences. Prompts : *« Sur quels critères doit-on se baser pour choisir une bonne méthodologie »* ; *« Quelles exigences peut-on avoir, faisons un brainstorming »*. |
| **Phase 1 : Modélisation initiale des menaces** (cas d'abus, récits d'abus, STRIDE, arbres d'attaque — intégrés au recueil) (Y. Ouattara) | Claude Opus 5.5 (Anthropic) | ~40 % | L'équipe a orienté les scénarios vers les fraudes réelles (faux complet, retouche, usurpation) et vérifié leur cohérence. Prompts : *« À partir de ces fraudes réelles, comment déterminer les cas d'abus et les récits d'abus ? »* ; *« C'est quoi le threat modelling de façon simple »* ; *« En considérant les attaques ? Justifie tes propositions. »* |
| **Cahier des charges** (Y. Ouattara) | Claude Opus 5.5 (Anthropic) | ~60 % | Rédaction et mise en page (génération PDF via Python/ReportLab). |
| **Squelette backend / frontend / CI** (Y. Ouattara) | Claude Opus 5.5 (Anthropic) | ~60 % | Explication de la CI GitHub Actions et des modèles d'issues, puis génération du squelette Jakarta EE 11, du test SR-AUZ-01, de la PWA minimale, de la CI et des modèles d'issues. Prompts : *« C'est quoi la CI GitHub Actions et des modèles d'issues ? Comment les implémenter ? »* |
| **Revue croisée et corrections de la spécification** (T. D. Yeo) | Claude Opus 5.5 (Anthropic) | ~75 % | Relecture critique du dépôt ; vérification d'un fait cité (affaire des douanes, par recherche web) ; rédaction des 6 corrections (SR-DIM-04/ENF-04 resynchronisation, SR-INT-02 isolation PDFBox, encadré « pourquoi c'est de la stéganographie », sources, schéma d'architecture). Décision de retenir EburSeal et validation des corrections par l'équipe. Une proposition alternative générée par l'IA (« TraceMark ») a été **abandonnée** au profit d'EburSeal. Prompts : *« Yacouba m'a envoyé une proposition »* (avec son dépôt) ; *« Tu dois me dire quoi lui expliquer concrètement pour le convaincre »* ; *« L'objectif est que je comprenne le projet dans les moindres détails, ce qui est demandé, ce que j'ai fait jusqu'à présent, comment et pourquoi, car je dois pouvoir l'expliquer de A à Z sans ambiguïté »*. |
| **CI/CD et sécurité du dépôt** (T. D. Yeo) | Claude Opus 5.5 (Anthropic) | ~60 % | Ajout du job OWASP Dependency-Check ; diagnostic des échecs CI à partir des journaux (faille haute Vite → 6.4.5, permission `pull-requests: read` pour gitleaks, clé NVD en secret) ; choix des protections GitHub (protection de `main`, Dependabot, CodeQL, push protection, signalement privé des failles). Modifications appliquées et poussées par T. D. Yeo. Prompts : journaux d'erreur de la CI collés tels quels pour diagnostic ; *« Je ne comprends pas : comment j'ouvre `.github/workflows/ci.yml` ? »* ; *« Il y a beaucoup d'options, dis-moi ce que je fais »*. |
| **Mise en page des documents** (T. D. Yeo) | Claude Opus 5.5 (Anthropic) | ~80 % | Réécriture du module `docs/src/vmpdf.py` d'après le modèle de rapport SUP'COM fourni par l'équipe (page de garde, Times 12, palette sobre) ; diagrammes en niveaux de gris. Prompts : *« Est-ce possible que je t'envoie un modèle avec le logo de SUP'COM et aussi la police Times New Roman taille 12 ? »* ; *« Je veux des modèles comme ça, bien faits et bien organisés, et évite les couleurs bizarres »* (avec le rapport modèle en pièce jointe). |
| **Gestion Git/GitHub et mises à jour du 09/11** (T. D. Yeo) | Claude Opus 5.5 (Anthropic) | ~40 % | Accompagnement pas à pas (branches, pull requests, fusion, tag, incidents Git sous Windows). Corrections du 09/11 (dépôt public, `SECURITY.md`, CSV standard, `build.sh`) éditées à la main par T. D. Yeo sur indications de l'IA. Prompts : *« Allons étape par étape, du début à la fin, sinon je risque de me perdre »* ; *« En attendant, est-ce qu'il y a quelque chose à corriger ? »*. |
| **Moteur de dissimulation** | — | 0 % | Non commencé (jalon J2). L'IA a seulement signalé une erreur de conception (LSB détruit par la compression JPEG → choix du domaine DCT). |

### 🛠️ Exemple de Prompt Clé (Le plus significatif utilisé par l'équipe) :
> *« Ceci est une idée que j'aimerais développer et déployer pour mon pays et je trouve pertinente et adéquate avec ce projet : concevoir une application permettant de lutter contre la falsification des diplômes en CI, un problème qui prend de plus en plus de l'ampleur. Alors, pourquoi serait-elle pertinente dans ce contexte ? »* — OUATTARA Yacouba

---

## ✍️ 4. Signatures des membres
En inscrivant votre nom ci-dessous dans le commit de validation, vous signez électroniquement ce document et vous engagez sur l'exactitude des informations fournies.

* **YEO Tanna Daouda** : Engagé / 09/11/2026
* **OUATTARA Yacouba** : Engagé / 10/11/2026

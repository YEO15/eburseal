# EburSeal

**Le sceau invisible des diplômes ivoiriens** — plateforme PWA de délivrance et de vérification de diplômes infalsifiables.

> *Ebur* : « ivoire » en latin, racine d'« Éburnie », nom poétique de la Côte d'Ivoire. *Seal* : le sceau.

Projet de l'atelier *Sécurité Applicative* — SUP'COM, 3ᵉ année cycle ingénieur, option CySeD (2026-2027).
Binôme : **OUATTARA Yacouba** · **YEO Tanna Daouda** (responsabilités partagées, revue croisée obligatoire).
Encadrant : Dr. Ing. Mohamed-Becha Kaâniche.

> 🌐 Dépôt **public** (à la demande de l'encadrant, pour l'évaluation outillée). Tous droits réservés (voir [LICENSE](LICENSE)).

## Le problème

En Côte d'Ivoire, la fraude aux diplômes est récurrente (faux diplômes dans la fonction publique, les écoles de formation, les
concours). EburSeal permet à quiconque de savoir **en quelques secondes** si un diplôme est **authentique, intact et présenté
par son vrai titulaire**.

| Fraude | Technique de dissimulation | Ce qu'elle prouve |
|---|---|---|
| Faux complet | **Watermarking** — filigrane invisible lié à la clé de l'établissement | **Qui** a émis le diplôme |
| Diplôme retouché | **Stéganographie** — données officielles signées cachées dans le document | **Ce qui** a été émis |
| Diplôme usurpé | **Fingerprinting** — empreinte unique par copie partagée | **À qui** la copie a été remise |

## Documents (séance 2 — spécification & conception)

- 📄 [Cahier des charges](docs/cahier_des_charges.pdf)
- 📄 [Recueil des besoins fonctionnels et SRE](docs/recueil_des_besoins.pdf) — **SQUARE adapté** + cas d'abus, récits d'abus, arbres d'attaque, STRIDE, priorisation AHP
- 📊 [Référentiel des exigences de sécurité (CSV)](docs/exigences.csv)

## Documents (phase 2 — conception sécurisée)

- 📄 [Cahier conceptuel](docs/cahier_conceptuel.pdf) — DFD et frontières de confiance, **STRIDE par élément** (31 menaces contextualisées, CAPEC/CWE), critique de DREAD, notation **OWASP Risk Rating**, contre-mesures natives / applicatives, patrons de conception, complément LINDDUN

## Socle technique

| Couche | Technologie |
|---|---|
| Serveur | **Jakarta EE 11** sur **WildFly 42**, **Java 25** |
| Client | SPA React + TypeScript (Vite), **PWA** (vite-plugin-pwa) |
| Documents | Apache PDFBox (rastérisation), moteur DCT 8×8 (filigrane, sceau, empreinte) |
| Données | PostgreSQL |
| CI | GitHub Actions : build, tests, SCA, recherche de secrets |

## Structure du dépôt

```
backend/     Projet Maven multi-modules : commun, crypto, moteur, banc, api (WAR Jakarta EE 11, API REST sous /api)
frontend/    SPA PWA
docs/        PDF remis + sources (docs/src) pour régénérer les documents
.github/     CI, modèles d'issues (feature, abuse-story, security-story), modèle de PR
```

## Démarrer

```bash
# Back-end (JDK 25 + Maven) → backend/api/target/api-1.0.war
mvn -f backend/pom.xml verify
cp backend/api/target/api-1.0.war $WILDFLY_HOME/standalone/deployments/
$WILDFLY_HOME/bin/standalone.sh
curl -k https://localhost:8443/api-1.0/api/info       # {"application":"EburSeal","status":"up"}

# Front-end (Node 22)
cd frontend && npm ci && npm run dev
```

## Démarche de sécurité

Toutes les exigences sont spécifiées dès la séance 2 (*Shift-Left*), puis implémentées chapitre par chapitre. Chaque
fonctionnalité a ses **cas d'abus rédigés avant d'être développée** et chaque cas d'abus est couvert par un test qui
démontre l'échec de l'attaque.

| Tag | Chapitre | Contenu |
|---|---|---|
| `v0.2-ch2` | Spécification & conception | Documents, squelette déployable, test SR-AUZ-01 (refus par défaut) |
| `v0.3-ch3` | Confidentialité, intégrité, disponibilité | Moteur DCT, signatures, chiffrement au repos, validation des fichiers |
| `v0.4-ch4` | Authentification, autorisation, vie privée | Argon2id, TOTP, JWT, RBAC, double validation |
| `v0.5-ch5` | Journalisation & erreurs | Audit chaîné, alertes, RFC 9457 |
| `v0.6-ch6` | Tests de sécurité | SAST, SCA, DAST (ZAP), tests d'abus, banc de robustesse |
| `v0.7-ch7` | Déploiement & maintenance | WildFly durci, conteneurs, sauvegardes, rotation des clés |

Signaler une vulnérabilité : voir [SECURITY.md](SECURITY.md).

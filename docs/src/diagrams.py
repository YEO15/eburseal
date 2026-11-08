"""Génère les diagrammes (Graphviz) utilisés dans les documents EburSeal."""
import subprocess, pathlib
import data as D

OUT = pathlib.Path(__file__).parent / "diagrams"
OUT.mkdir(exist_ok=True)
FONT = 'fontname="Liberation Serif"'


def render(name, dot):
    (OUT / f"{name}.dot").write_text(dot, encoding="utf-8")
    subprocess.run(["dot", "-Tpng", "-Gdpi=200", "-o", str(OUT / f"{name}.png"), str(OUT / f"{name}.dot")], check=True)


# 1. Cas d'utilisation + cas d'abus + cas de sécurité
render("usecases", f"""
digraph G {{
 rankdir=LR; graph[{FONT}, fontsize=11, nodesep=0.18, ranksep=0.45]; node[{FONT}, fontsize=9]; edge[{FONT}, fontsize=7.5];
 T [label="Titulaire", shape=box, style="rounded,filled", fillcolor="#F2F2F2"];
 E [label="Agent /\\nResponsable émetteur", shape=box, style="rounded,filled", fillcolor="#F2F2F2"];
 V [label="Vérificateur /\\nVisiteur", shape=box, style="rounded,filled", fillcolor="#F2F2F2"];
 {{rank=min; T; E; V;}}
 subgraph cluster_s {{ label="« system » EburSeal"; style="rounded"; color="#333333"; fontcolor="#333333";
  node[shape=ellipse, style=filled, fillcolor="white", color="#333333"];
  uc1 [label="Se connecter"]; uc2 [label="Valider et émettre\\nun diplôme"]; uc3 [label="Partager une\\ncopie traçable"];
  uc4 [label="Vérifier un diplôme"]; uc5 [label="Consulter son\\nportefeuille"];
  node[shape=ellipse, style=filled, fillcolor="#D9D9D9", fontcolor="black", color="#333333", penwidth=1.4];
  cs1 [label="CS-01 Garantir l'origine"]; cs2 [label="CS-02 Garantir l'intégrité"]; cs3 [label="CS-03 Lier copie\\net destinataire"];
  cs4 [label="CS-04 Contrôler l'émission"]; cs5 [label="CS-05 Protéger\\nl'authentification"]; cs6 [label="CS-06 Contrôler l'accès"];
  node[shape=ellipse, style=filled, fillcolor="#222222", fontcolor="white", color="#222222"];
  ca1 [label="CA-01 Faire accepter\\nun faux diplôme"]; ca2 [label="CA-02 Retoucher un\\ndiplôme authentique"];
  ca3 [label="CA-03 Présenter le\\ndiplôme d'un autre"]; ca4 [label="CA-04 Émettre un diplôme\\nde complaisance"];
  ca5 [label="CA-05 Prendre le contrôle\\nd'un compte"]; ca6 [label="CA-06 Accéder aux\\nressources d'autrui"];
 }}
 F [label="Faussaire / titulaire fraudeur /\\nimposteur", shape=box, style="rounded,filled", fillcolor="#BFBFBF"];
 X [label="Agent corrompu /\\nattaquant externe", shape=box, style="rounded,filled", fillcolor="#BFBFBF"];
 T -> {{uc1 uc3 uc5}} [arrowhead=none]; E -> {{uc1 uc2}} [arrowhead=none]; V -> uc4 [arrowhead=none];
 {{ca1 ca2 ca3}} -> F [arrowhead=none]; {{ca4 ca5 ca6}} -> X [arrowhead=none];
 edge[style=dashed, color="#000000", fontcolor="#000000", label="«threatens»", constraint=false];
 ca1 -> uc4; ca2 -> uc4; ca3 -> uc3; ca3 -> uc4; ca4 -> uc2; ca5 -> uc1; ca6 -> uc5;
 edge[style=dashed, color="#333333", fontcolor="#333333", label="«mitigates»", constraint=true];
 cs1 -> ca1; cs2 -> ca2; cs3 -> ca3; cs4 -> ca4; cs5 -> ca5; cs6 -> ca6;
 edge[style=dotted, color="#333333", fontcolor="#333333", label="«include»", constraint=true];
 uc4 -> cs1; uc4 -> cs2; uc3 -> cs3; uc2 -> cs4; uc1 -> cs5; uc5 -> cs6;
}}""")

# 2. Architecture
render("architecture", f"""
digraph G {{
 rankdir=TB; graph[{FONT}, fontsize=10, nodesep=0.3, ranksep=0.5]; node[{FONT}, fontsize=8.5, shape=box, style="rounded,filled", fillcolor="white", color="#333333"]; edge[{FONT}, fontsize=7.5, color="#333333"];
 subgraph cluster_c {{ label="Navigateur (PWA / SPA)"; style="rounded,filled"; fillcolor="#F2F2F2"; color="#555555";
  ui [label="Interface React + TypeScript\\n(titulaire, émetteur, vérificateur)"]; sw [label="Service Worker\\n(cache statique uniquement)"]; }}
 subgraph cluster_s {{ label="WildFly 42 — Jakarta EE 11 / Java 25"; style="rounded,filled"; fillcolor="#FAFAFA"; color="#333333";
  rest [label="Jakarta REST\\n/api/**"]; sec [label="Jakarta Security + Elytron\\nJWT ES256, RBAC, MFA"];
  svc [label="Services CDI\\nÉmission · Partage · Vérification"];
  eng [label="Moteur EburSeal (DCT 8×8)\\nfiligrane · sceau caché · empreinte", fillcolor="#E6E6E6"];
  pdf [label="Rastérisation PDF\\n(Apache PDFBox, 300 dpi)"]; sig [label="Signatures Ed25519\\n+ certificats"];
  exe [label="Jakarta Concurrency\\n(file bornée, 30 s)"]; aud [label="Audit chaîné"]; cs [label="Credential store\\n(clé maître)"]; }}
 db [label="PostgreSQL\\nregistre, partages,\\nclés chiffrées", shape=cylinder];
 st [label="Stockage documents\\n(chiffré AES-GCM)", shape=cylinder]; lg [label="Journaux\\n(ajout seul)", shape=cylinder];
 ui -> rest [label="HTTPS TLS 1.3\\nJWT en mémoire"]; sw -> ui [style=dashed];
 rest -> sec; rest -> svc; svc -> pdf; svc -> eng; svc -> sig; eng -> exe; svc -> aud; svc -> db; svc -> st; aud -> lg; sig -> cs [style=dashed]; eng -> cs [style=dashed];
}}""")

# 3. Arbre d'attaque : faire accepter un faux ou un diplôme retouché
render("attacktree_fake", f"""
digraph G {{
 rankdir=LR; graph[{FONT}, fontsize=10, nodesep=0.12, ranksep=0.35]; node[{FONT}, fontsize=8, shape=box, style="rounded,filled", fillcolor="white", color="#333333"]; edge[color="#555555", arrowhead=none];
 root [label="BUT : faire accepter comme authentique\\nun diplôme que l'on n'a pas obtenu", fillcolor="#222222", fontcolor="white"];
 o1 [label="OU 1 — Fabriquer un faux"]; o2 [label="OU 2 — Greffer les marques\\nd'un vrai sur un faux"]; o3 [label="OU 3 — Retoucher un vrai"];
 o4 [label="OU 4 — Obtenir un vrai\\nde complaisance"]; o5 [label="OU 5 — Tromper l'outil\\nde vérification"];
 root -> {{o1 o2 o3 o4 o5}};
 a1 [label="Aucun filigrane valide sans la clé\\nde l'établissement → SR-DIM-02, 05", fillcolor="#FFFFFF"];
 a2 [label="Le sceau signé ne correspond plus\\nau contenu affiché → SR-DIM-03, BF-STG-02", fillcolor="#FFFFFF"];
 a3 [label="Données officielles affichées côte à côte\\n+ registre → SR-DIM-05", fillcolor="#FFFFFF"];
 a4 [label="Double validation + MFA + alertes\\nde volume → SR-AUZ-03, SR-AUT-03, SR-LOG-03", fillcolor="#FFFFFF"];
 a5 [label="Vérificateur qui ne vérifie pas\\n(hors périmètre : sensibilisation)", fillcolor="#E6E6E6"];
 a6 [label="Oracle / erreur interprétée comme succès\\n→ SR-DIM-09, SR-ERR-02", fillcolor="#FFFFFF"];
 o1 -> a1; o2 -> a2; o3 -> a3; o4 -> a4; o5 -> {{a5 a6}};
}}""")

# 4. Arbre d'attaque : usurper le diplôme d'un autre
render("attacktree_usurp", f"""
digraph G {{
 rankdir=LR; graph[{FONT}, fontsize=10, nodesep=0.12, ranksep=0.35]; node[{FONT}, fontsize=8, shape=box, style="rounded,filled", fillcolor="white", color="#333333"]; edge[color="#555555", arrowhead=none];
 root [label="BUT : présenter le diplôme d'un autre\\nsans être détecté", fillcolor="#222222", fontcolor="white"];
 e1 [label="ET 1 — Obtenir une copie"]; e2 [label="ET 2 — Échapper à la détection"];
 root -> {{e1 e2}};
 b1 [label="Fuite chez un destinataire\\n(copie tracée → SR-DIM-06, 10)", fillcolor="#FFFFFF"];
 b2 [label="Lire les partages d'autrui (IDOR)\\n→ SR-AUZ-02", fillcolor="#FFFFFF"];
 b3 [label="Voler le compte du titulaire\\n→ SR-AUT-01 à 04", fillcolor="#FFFFFF"];
 c1 [label="Effacer l'empreinte\\n→ robustesse + seuil (SR-DIM-04, 06)", fillcolor="#FFFFFF"];
 c2 [label="Apprendre par oracle\\n→ SR-DIM-09", fillcolor="#FFFFFF"];
 c3 [label="Viser un vérificateur anonyme\\n(risque résiduel : voir § 6.2)", fillcolor="#E6E6E6"];
 e1 -> {{b1 b2 b3}}; e2 -> {{c1 c2 c3}};
}}""")

# 5. Processus SQUARE adapté
render("square", f"""
digraph G {{
 rankdir=LR; graph[{FONT}, fontsize=9, nodesep=0.15, ranksep=0.25]; node[{FONT}, fontsize=7.8, shape=box, style="rounded,filled", fillcolor="#F2F2F2", color="#555555", width=1.25]; edge[color="#333333"];
 s1 [label="1. Définitions\\n(glossaire)"]; s2 [label="2. Actifs &\\nobjectifs"]; s3 [label="3. Artefacts\\ncas d'abus, CS,\\narbres"];
 s4 [label="4. Risques\\nSTRIDE + matrice"]; s5 [label="5. Techniques\\nd'élicitation"]; s6 [label="6. Élicitation\\n{len(D.SEC)} exigences"];
 s7 [label="7. Catégorisation\\n{len(D.CATS)} catégories"]; s8 [label="8. Priorisation\\nAHP → P1/P2/P3"]; s9 [label="9. Inspection\\nrevue croisée"];
 s1 -> s2 -> s3 -> s4 -> s5 -> s6 -> s7 -> s8 -> s9; s9 -> s6 [style=dashed, label="itération", fontsize=7, {FONT}, constraint=false];
}}""")
for f in OUT.glob("attacktree_msg*"): f.unlink()
for f in OUT.glob("attacktree_wm*"): f.unlink()
print("diagrammes générés")

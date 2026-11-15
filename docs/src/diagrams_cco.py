"""Diagrammes du cahier conceptuel (phase 2) : DFD avec frontières de confiance, chaîne de vérification sécurisée."""
import pathlib
import subprocess

OUT = pathlib.Path(__file__).parent / "diagrams"
FONT = 'fontname="Liberation Serif"'


def render(name, dot):
    (OUT / f"{name}.dot").write_text(dot, encoding="utf-8")
    subprocess.run(["dot", "-Tpng", "-Gdpi=200", "-o", str(OUT / f"{name}.png"), str(OUT / f"{name}.dot")], check=True)


# 1. Diagramme de flux de données (DFD) et frontières de confiance
render("dfd", f"""
digraph G {{
 rankdir=TB; compound=true; graph[{FONT}, fontsize=10, nodesep=0.35, ranksep=0.45];
 node[{FONT}, fontsize=11, color="#333333"]; edge[{FONT}, fontsize=9.5, color="#333333"];
 E1 [label="E1 — Navigateur\\n(PWA / SPA)", shape=box, style="filled", fillcolor="#F2F2F2"];
 subgraph cluster_tb1 {{ label="TB1 — Frontière Internet ↔ serveur (WildFly 42 / Jakarta EE 11 / Java 25)"; style="dashed"; color="#000000"; fontsize=9;
  P1 [label="P1 — Jakarta REST\\n+ Jakarta Security / Elytron", shape=ellipse];
  P2 [label="P2 — Services CDI\\némission · partage · vérification", shape=ellipse];
  subgraph cluster_tb3 {{ label="TB3 — Fichiers non fiables (file bornée : 30 s, 512 Mo)"; style="dashed"; color="#555555"; fontsize=8.5;
   P3 [label="P3 — Rastérisation PDF\\n/ décodage image", shape=ellipse];
   P4 [label="P4 — Moteur DCT 8×8\\nfiligrane · sceau · empreinte", shape=ellipse, style=filled, fillcolor="#E6E6E6"]; }}
  subgraph cluster_tb4 {{ label="TB4 — Secrets"; style="dashed"; color="#555555"; fontsize=8.5;
   P5 [label="P5 — Signature Ed25519\\nchiffrement AES-256-GCM", shape=ellipse];
   DS4 [label="DS4 — Credential store\\nElytron (clé maître)", shape=cylinder]; }}
 }}
 subgraph cluster_tb2 {{ label="TB2 — Frontière application ↔ données"; style="dashed"; color="#000000"; fontsize=9;
  DS1 [label="DS1 — PostgreSQL\\nregistre, partages", shape=cylinder];
  DS2 [label="DS2 — Documents\\nchiffrés", shape=cylinder];
  DS3 [label="DS3 — Journal d'audit\\nchaîné, ajout seul", shape=cylinder]; }}
 X1 [label="X1 — Chaîne de production\\nGitHub, CI, dépendances\\nMaven / npm", shape=box, style="dashed"];
 X1 -> P1 [label="déploiement\\n(code + dépendances)", style=dashed];
 E1 -> P1 [label="HTTPS TLS 1.3\\nJWT, JSON, fichiers"];
 P1 -> E1 [label="verdict, RFC 9457", style=dashed];
 P1 -> P2 [label="identité + rôles"];
 P2 -> P3 [label="fichier déposé"]; P3 -> P4 [label="image rastérisée"];
 P4 -> P5 [label="données du sceau"]; P5 -> DS4 [label="clés", style=dashed];
 P2 -> DS1 [label="requêtes\\nparamétrées"]; P2 -> DS2 [label="documents"]; P2 -> DS3 [label="événements"];
}}""")

# 2. Chaîne de vérification sécurisée (ordre des contrôles)
render("verify_pipeline", f"""
digraph G {{
 rankdir=TB; graph[{FONT}, fontsize=10, nodesep=0.35, ranksep=0.6];
 node[{FONT}, fontsize=12, shape=box, style="rounded,filled", fillcolor="white", color="#333333"]; edge[color="#333333", fontsize=10, {FONT}];
 a [label="1. Limitation\\n10/h/IP\\n(SR-DIM-09)"];
 b [label="2. Signature binaire,\\ntaille, pages,\\ndimensions\\n(SR-INT-01)"];
 c [label="3. Rastérisation\\nbornée 300 dpi\\n(SR-INT-02, DIS-02)"];
 d [label="4. Resynchronisation\\ngéométrique\\n(SR-DIM-04)"];
 e [label="5. Filigrane ET\\nsceau Ed25519 ET\\nregistre non révoqué\\n(SR-DIM-05)", fillcolor="#E6E6E6"];
 f [label="6. Verdict sans score,\\ndestinataire masqué\\n(SR-DIM-08, 09)"];
 g [label="7. Rapport signé\\n+ journal chaîné\\n(SR-NRP-04, 03)"];
 x [label="Refus / « indéterminé »\\n(échec en mode sûr,\\nSR-ERR-02)", fillcolor="#222222", fontcolor="white"];
 {{rank=same; a; b; c; d;}} {{rank=same; e; f; g; x;}}
 a -> b -> c -> d -> e -> f -> g;
 {{b c d e}} -> x [style=dashed, label="échec", constraint=false];
}}""")
print("Diagrammes du cahier conceptuel générés")

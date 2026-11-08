#!/usr/bin/env bash
# Régénère diagrammes, PDF et référentiel CSV.
set -euo pipefail
cd "$(dirname "$0")"
python3 diagrams.py
python3 cdc.py ../cahier-des-charges.pdf
python3 rdb.py ../recueil-des-besoins.pdf
echo "Documents régénérés dans docs/"

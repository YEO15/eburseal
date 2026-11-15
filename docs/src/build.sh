#!/usr/bin/env bash
# Régénère diagrammes, PDF et référentiel CSV.
set -euo pipefail
cd "$(dirname "$0")"
python3 diagrams.py
python3 cdc.py ../cahier_des_charges.pdf
python3 rdb.py ../recueil_des_besoins.pdf
echo "Documents régénérés dans docs/"

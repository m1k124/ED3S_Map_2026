#!/bin/bash
set -e

cd "$(dirname "$0")"

if [ ! -f "output/carte_d3s.html" ]; then
  echo "La carte output/carte_d3s.html est introuvable."
  echo "Lancez d'abord 1_GENERER_LA_CARTE.command."
  echo
  read -r -p "Appuyez sur Entree pour fermer cette fenetre..."
  exit 1
fi

open "output/carte_d3s.html"


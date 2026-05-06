#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "==============================================="
echo " Generation de la carte interactive D3S"
echo "==============================================="
echo

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERREUR : Python 3 est introuvable sur ce Mac."
  echo "Installez Python 3 depuis https://www.python.org/downloads/"
  echo "puis relancez ce script."
  echo
  read -r -p "Appuyez sur Entree pour fermer cette fenetre..."
  exit 1
fi

if [ ! -f "data/postes_d3s.xlsx" ]; then
  echo "ERREUR : le fichier data/postes_d3s.xlsx est introuvable."
  echo "Placez le fichier Excel source dans le dossier data et nommez-le postes_d3s.xlsx."
  echo
  read -r -p "Appuyez sur Entree pour fermer cette fenetre..."
  exit 1
fi

if [ ! -f "data/referentiel_finess.csv" ]; then
  echo "ERREUR : le fichier data/referentiel_finess.csv est introuvable."
  echo "Ce fichier est necessaire pour ameliorer les coordonnees FINESS."
  echo
  read -r -p "Appuyez sur Entree pour fermer cette fenetre..."
  exit 1
fi

if [ ! -x ".venv/bin/python" ]; then
  echo "Premiere utilisation : creation de l'environnement Python local..."
  python3 -m venv .venv
fi

echo "Installation ou verification des dependances..."
".venv/bin/python" -m pip install -r requirements.txt
echo

echo "Generation de la carte..."
".venv/bin/python" main.py
echo

if [ -f "output/carte_d3s.html" ]; then
  echo "Carte generee : output/carte_d3s.html"
  open "output/carte_d3s.html"
else
  echo "ERREUR : la carte n'a pas ete generee."
  read -r -p "Appuyez sur Entree pour fermer cette fenetre..."
  exit 1
fi

echo
echo "Termine. Le fichier a envoyer est : output/carte_d3s.html"
echo
read -r -p "Appuyez sur Entree pour fermer cette fenetre..."


# Mise a jour des donnees ED3S

Ce document sert aux mises a jour courantes apres la premiere mise en ligne Render.

## Remplacer le fichier Excel

1. Remplacer `data/postes_d3s.xlsx` par le nouveau fichier.
2. Conserver exactement le nom `postes_d3s.xlsx`.
3. Verifier que l'onglet attendu existe toujours :

```yaml
sheet_name: "Postes_enrichis"
```

## Regenerer localement

Depuis la racine du projet :

```bash
source .venv/bin/activate
./build.sh
```

Le build :

- installe les dependances si necessaire ;
- regenere `output/carte_d3s.html` ;
- regenere automatiquement `output/index.html` ;
- copie les assets de `static/` vers `output/` ;
- controle que le site statique contient les elements attendus.

## Controles manuels

Ouvrir :

```bash
open output/index.html
```

Verifier :

- l'ecran d'accueil ;
- le logo de la promotion ;
- le bouton `Explorer la carte` ;
- le bouton `Consulter Plaquette Promo` ;
- les filtres ;
- la recherche ;
- l'ouverture d'une fiche poste ;
- les compteurs.

## Publier

```bash
git status
git add data output
git commit -m "Update ED3S map data"
git push
```

Render redeploie automatiquement apres le push sur `main`.

## Plaquette PDF

La plaquette officielle doit etre publiee ici :

```text
output/plaquette-promo.pdf
```

Conserver exactement ce nom pour que les boutons du site restent fonctionnels.

# Carte D3S - mode d'emploi simple

Ce dossier sert a mettre a jour et regenerer la carte interactive D3S.

Il n'est pas necessaire d'utiliser VSCode, Codex ou un logiciel de developpement.
Sur Mac, tout se fait en remplacant un fichier Excel puis en double-cliquant sur un script.

## Ce qu'il faut garder dans le dossier

- `data/postes_d3s.xlsx` : le fichier Excel source a mettre a jour.
- `data/referentiel_finess.csv` : le referentiel FINESS utilise pour ameliorer les coordonnees. Ne pas le modifier.
- `output/carte_d3s.html` : la carte HTML generee, a ouvrir ou envoyer.
- `1_GENERER_LA_CARTE.command` : le script a lancer apres chaque mise a jour Excel.

## Mise a jour habituelle

1. Ouvrir le dossier `data`.
2. Remplacer `postes_d3s.xlsx` par le nouveau fichier Excel.
3. Important : le nouveau fichier doit garder exactement le nom `postes_d3s.xlsx`.
4. Revenir dans le dossier principal.
5. Double-cliquer sur `1_GENERER_LA_CARTE.command`.
6. Attendre le message de fin.
7. La carte s'ouvre automatiquement dans le navigateur.
8. Le fichier a distribuer est `output/carte_d3s.html`.

Si macOS refuse d'ouvrir le script au premier double-clic, faire clic droit sur le fichier,
choisir `Ouvrir`, puis confirmer.

## Premiere utilisation sur un nouveau Mac

Au premier lancement, le script cree un environnement Python local dans `.venv` et installe les dependances.
Il faut donc etre connecte a Internet.

Les lancements suivants sont plus rapides.

## Points de controle apres generation

Dans la fenetre du script, verifier :

- `Postes valides avec coordonnees` : nombre de postes affichables sur la carte.
- `Postes sans coordonnees exploitables` : doit idealement rester bas.
- `Doublons supprimes` : information utile pour comprendre les ecarts.

Dans le navigateur, verifier :

- le compteur `postes affiches`;
- la recherche globale;
- les filtres categorie, type d'etablissement, annee, region, departement;
- l'ouverture d'une fiche poste en cliquant sur un marqueur.

## Si le fichier Excel change de structure

Le script sait reconnaitre plusieurs noms de colonnes grace au fichier `config/settings.yaml`.
Si une colonne n'est plus reconnue, demander de l'aide avant de modifier le code.

Le nom de l'onglet attendu est configure ici :

```yaml
sheet_name: "Postes_enrichis"
```

Si le nouvel Excel utilise un autre nom d'onglet, il faut modifier cette ligne dans `config/settings.yaml`.

## Envoi de la carte

Pour distribution, envoyer uniquement :

```text
output/carte_d3s.html
```

La personne qui ouvre la carte doit avoir Internet, car le fond de carte et les bibliotheques Leaflet sont charges en ligne.

## Depannage rapide

### Le script indique que Python est introuvable

Installer Python 3 depuis https://www.python.org/downloads/ puis relancer `1_GENERER_LA_CARTE.command`.

### La carte affiche 0 poste

Verifier que `data/postes_d3s.xlsx` contient bien les colonnes de latitude/longitude ou les colonnes FINESS attendues.
Verifier aussi que l'onglet configure dans `config/settings.yaml` existe dans le fichier Excel.

### La carte ne se charge pas chez un destinataire

Demander au destinataire de verifier sa connexion Internet et d'ouvrir le fichier avec Chrome, Edge, Firefox ou Safari.
Si le fond de carte semble bloque, renommer le fichier avant envoi, par exemple `carte_d3s_mai_2026.html`, pour eviter un cache navigateur ancien.

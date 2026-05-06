# Mise en ligne Render - ED3S Map 2026

Depot GitHub cible : https://github.com/m1k124/ED3S_Map_2026

Projet local : `/Users/maelgrand/Desktop/Campagne_DRA/scrapping/ED3S_Carte_V3_transfert_collegue`

Date de preparation : 2026-05-06

## Objectif

Mettre en ligne la carte D3S sur Render, sur le meme principe que le travail fait pour GrepolisMap, mais avec une difference importante : ce projet ED3S n'est pas une application Vite/Node. C'est un generateur Python qui produit une page HTML statique dans `output/carte_d3s.html`.

La cible la plus simple sur Render est donc un `Static Site`, avec une commande de build qui :

1. installe les dependances Python ;
2. regenere la carte HTML ;
3. copie la carte generee vers `output/index.html`, afin que l'URL Render affiche directement la carte a la racine.

Configuration Render recommandee :

```text
Service type: Static Site
Repository: https://github.com/m1k124/ED3S_Map_2026
Branch: main
Root Directory: laisser vide si le depot contient directement ce projet
Build Command: pip install -r requirements.txt && python main.py && cp output/carte_d3s.html output/index.html
Publish Directory: output
```

Render sert les sites statiques via CDN, declenche les redeploiements a chaque push sur la branche choisie, et demande un `Build Command` ainsi qu'un `Publish Directory` pour les static sites.

Sources Render consultees :

- https://render.com/docs/static-sites
- https://render.com/docs/your-first-deploy

## Phase 1 - Controle local du projet

Statut : termine le 2026-05-06.

Resultat de validation :

- environnement `.venv` cree avec Python 3.13.3 ;
- dependances installees : `pandas`, `openpyxl`, `PyYAML`, `Jinja2` ;
- generation executee avec `./.venv/bin/python main.py` ;
- lignes lues : 297 ;
- postes valides avec coordonnees : 293 ;
- postes sans coordonnees exploitables : 0 ;
- doublons supprimes : 4 ;
- carte generee : `output/carte_d3s.html`.

Objectif : verifier que la carte se genere correctement avant toute mise en ligne.

Depuis le dossier du projet :

```bash
cd /Users/maelgrand/Desktop/Campagne_DRA/scrapping/ED3S_Carte_V3_transfert_collegue
```

Verifier la structure minimale :

```bash
ls
```

Fichiers indispensables :

- `main.py`
- `requirements.txt`
- `config/settings.yaml`
- `templates/map_template.html`
- `data/postes_d3s.xlsx`
- `data/referentiel_finess.csv`
- `output/carte_d3s.html`

Verifier que la generation fonctionne :

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Controle attendu dans les logs :

- `Lignes lues` superieur a 0 ;
- `Postes valides avec coordonnees` superieur a 0 ;
- `Carte HTML: output/carte_d3s.html`.

Ouvrir ensuite :

```bash
open output/carte_d3s.html
```

Tests manuels rapides :

- la carte s'affiche ;
- les marqueurs sont visibles ;
- la recherche fonctionne ;
- les filtres categorie, type d'etablissement, annee, region et departement fonctionnent ;
- une fiche poste s'ouvre au clic sur un marqueur.

## Phase 2 - Nettoyage avant GitHub

Statut : termine le 2026-05-06.

Resultat de validation :

- ajout d'un `.gitignore` a la racine du projet ;
- exclusion de `.venv/`, `__pycache__/`, fichiers `.pyc`, `.DS_Store`, caches de test/typecheck et logs ;
- suppression du dossier local `src/__pycache__/` ;
- aucun fichier `.pyc` restant detecte ;
- aucun fichier `.DS_Store` detecte.

Point de vigilance avant push GitHub :

- `data/postes_d3s.xlsx` et `data/referentiel_finess.csv` restent presents, car Render devra les lire si la carte est regeneree pendant le build ;
- si le depot GitHub est public, valider une derniere fois que le contenu de l'Excel peut etre publie.

Objectif : eviter de publier des fichiers inutiles, locaux ou sensibles.

Verifier les fichiers presents :

```bash
find . -maxdepth 3 -type f | sort
```

Fichiers a ne pas publier :

- `.venv/`
- `__pycache__/`
- `.DS_Store`
- caches Python ;
- exports temporaires ;
- fichiers Excel de test non destines a la publication.

Si le depot n'a pas encore de `.gitignore`, prevoir d'en creer un avec au minimum :

```gitignore
.venv/
__pycache__/
*.pyc
.DS_Store
```

Decision importante avant publication :

- si `data/postes_d3s.xlsx` contient des donnees publiables, on peut le versionner ;
- si le fichier contient des donnees non publiques, ne pas le publier dans GitHub et utiliser plutot une generation locale avec publication du HTML seulement ;
- si le depot GitHub est public, relire les donnees avant le premier push.

Pour ce projet, Render doit pouvoir regenerer la carte pendant le build. Donc si on utilise `python main.py` sur Render, les fichiers `data/postes_d3s.xlsx` et `data/referentiel_finess.csv` doivent etre disponibles dans le depot, sauf si on change plus tard l'architecture.

## Phase 3 - Preparation de la racine Render

Statut : termine le 2026-05-06.

Resultat de validation :

- creation de `output/index.html` par copie de `output/carte_d3s.html` ;
- les deux fichiers ont la meme empreinte SHA-256 ;
- `output/index.html` contient bien le titre de la carte, le conteneur `#map` et les libelles attendus ;
- la commande Render recommandee reste :

```bash
pip install -r requirements.txt && python main.py && cp output/carte_d3s.html output/index.html
```

Objectif : faire en sorte que l'URL Render affiche la carte directement.

Aujourd'hui, le generateur produit :

```text
output/carte_d3s.html
```

Pour un site statique, la racine publique attend idealement :

```text
output/index.html
```

Deux options possibles.

Option recommandee au debut : laisser le code intact et demander a Render de copier le fichier pendant le build.

Build Command Render :

```bash
pip install -r requirements.txt && python main.py && cp output/carte_d3s.html output/index.html
```

Avantage : aucune modification du code Python.

Limite : la commande Render est un peu longue, mais elle est explicite.

Option plus propre ensuite : ajouter un petit script `build.sh`.

Contenu possible :

```bash
#!/usr/bin/env bash
set -e

pip install -r requirements.txt
python main.py
cp output/carte_d3s.html output/index.html
```

Puis Render utiliserait :

```bash
./build.sh
```

Cette option est interessante si on veut stabiliser le deploiement et eviter une commande Render trop chargee.

## Phase 4 - Etape prevue pour les modifications de la carte

Statut : termine le 2026-05-06.

Modifications realisees :

- transformation du template en site complet avec ecran d'accueil inspire du mash up fourni ;
- ajout d'une barre de navigation sans espace de connexion ;
- ajout de l'identite visuelle `Promotion Constance Pascal 2025-2026` ;
- ajout de boutons `Explorer la carte` et `Consulter Plaquette Promo` ;
- ajout de sections `Carte des avis`, `À propos`, `Ressources`, `FAQ` et `Nous contacter` ;
- conservation de la carte interactive existante dans une section dediee ;
- remplacement du fond de carte OpenStreetMap France par le fond clair Carto `light_all` ;
- ajout d'options Leaflet plus legeres : `detectRetina: false`, `updateWhenIdle: true`, `keepBuffer: 1` ;
- creation de `output/plaquette-promo.pdf` comme PDF temporaire a remplacer par la vraie plaquette officielle ;
- regeneration de `output/carte_d3s.html` puis copie vers `output/index.html`.

Resultat de validation :

- generation executee avec `./.venv/bin/python main.py` ;
- lignes lues : 297 ;
- postes valides avec coordonnees : 293 ;
- postes sans coordonnees exploitables : 0 ;
- doublons supprimes : 4 ;
- `output/index.html` sert bien la nouvelle page d'accueil ;
- `output/plaquette-promo.pdf` repond en local avec le type `application/pdf` ;
- aucune mention `Espace candidat`, `Connexion` ou `login` detectee dans le template et le HTML genere.

Point a faire avant publication officielle :

- remplacer `output/plaquette-promo.pdf` par la vraie plaquette PDF de la promotion, en conservant exactement le meme nom de fichier.

Objectif : faire les ajustements fonctionnels avant la premiere mise en ligne publique.

Avant de connecter Render, prevoir une pause de travail avec Codex. Message type a envoyer :

```text
Avant la mise en ligne Render de ED3S_Map_2026, je veux modifier les fonctionnalites de la carte.
Voici les modifications :
1. ...
2. ...
3. ...
Fais les changements, regenere la carte, puis mets a jour le plan de deploiement si necessaire.
```

Zones qui seront probablement concernees :

- `templates/map_template.html` pour l'interface, les filtres, le comportement JavaScript et le rendu Leaflet ;
- `src/html_renderer.py` pour les donnees injectees dans le template ;
- `src/data_cleaner.py` si une nouvelle fonctionnalite demande une nouvelle colonne normalisee ;
- `config/settings.yaml` si on ajoute des libelles, couleurs, options d'affichage ou alias de colonnes.

Exemples de modifications possibles :

- ajouter un filtre par statut ou type de poste ;
- changer les couleurs des categories ;
- modifier la fiche detaillee d'un poste ;
- ajouter un compteur par categorie ;
- ajouter une vue initiale differente ;
- afficher ou masquer certaines colonnes ;
- ameliorer la recherche globale ;
- ajouter un bouton de reinitialisation des filtres ;
- renommer le titre, le sous-titre ou les libelles visibles.

Criteres de validation apres modifications :

- `python main.py` passe sans erreur ;
- `output/carte_d3s.html` est regenere ;
- `output/index.html` est regenere ou copie si necessaire ;
- la carte s'ouvre localement ;
- les nouvelles fonctionnalites sont testees manuellement ;
- aucun fichier local inutile n'est ajoute au commit.

## Phase 5 - Initialisation Git locale

Statut : termine le 2026-05-06.

Resultat de validation :

- depot Git initialise localement ;
- branche locale renommee en `main` ;
- identite Git locale configuree pour ce depot : `m1k124 <m1k124@users.noreply.github.com>` ;
- remote `origin` ajoute : `https://github.com/m1k124/ED3S_Map_2026.git` ;
- commit initial cree : `c3eb8af Prepare ED3S map for Render deployment` ;
- contenu distant initial integre : `LICENSE` depuis le commit GitHub `6b2a145` ;
- commit de merge cree : `6f2e8ef Merge branch 'main' of https://github.com/m1k124/ED3S_Map_2026` ;
- push vers GitHub reussi apres configuration HTTP locale plus robuste ;
- verification distante : `origin/main` pointe sur `6f2e8ef`.

Note technique :

- le premier push HTTPS a echoue avec une coupure HTTP ;
- le push a fonctionne apres configuration locale :

```bash
git config http.version HTTP/1.1
git config http.postBuffer 157286400
git config http.lowSpeedLimit 0
git config http.lowSpeedTime 999999
```

Objectif : lier le dossier local au depot GitHub deja cree.

Depuis le dossier du projet :

```bash
cd /Users/maelgrand/Desktop/Campagne_DRA/scrapping/ED3S_Carte_V3_transfert_collegue
```

Si le dossier n'est pas encore un depot Git :

```bash
git init
git branch -M main
git remote add origin https://github.com/m1k124/ED3S_Map_2026.git
```

Si `origin` existe deja, verifier :

```bash
git remote -v
```

Si l'URL n'est pas la bonne :

```bash
git remote set-url origin https://github.com/m1k124/ED3S_Map_2026.git
```

Verifier l'etat :

```bash
git status
```

Ajouter les fichiers :

```bash
git add README.md DEPLOIEMENT_RENDER.md main.py requirements.txt config data src templates output
```

Faire un commit initial :

```bash
git commit -m "Prepare ED3S map for Render deployment"
```

Pousser vers GitHub :

```bash
git push -u origin main
```

Si GitHub refuse le push parce que le depot distant contient deja un commit, recuperer d'abord le distant :

```bash
git pull origin main --allow-unrelated-histories
```

Puis resoudre les conflits eventuels, refaire un commit, et pousser.

## Phase 6 - Creation du Static Site sur Render

Statut : prepare le 2026-05-06.

Preparation realisee :

- ajout d'un fichier `render.yaml` a la racine du depot ;
- declaration du site statique Render `ed3s-map-2026` ;
- runtime Render : `static` ;
- branche : `main` ;
- build command :

```bash
pip install -r requirements.txt && python main.py && cp output/carte_d3s.html output/index.html
```

- dossier publie : `./output` ;
- auto deploy active sur chaque commit ;
- variable `SKIP_INSTALL_DEPS=true` ajoutee pour eviter une installation automatique en double, puisque le build installe deja les dependances Python explicitement.

Deux chemins Render sont possibles :

- chemin recommande : creer un `Blueprint` depuis le depot GitHub ; Render lira `render.yaml` ;
- chemin manuel : creer un `Static Site` et recopier les parametres indiques plus bas.

Objectif : creer le service Render qui publie la carte.

Dans Render :

1. ouvrir https://dashboard.render.com ;
2. cliquer sur `New` ;
3. choisir `Static Site` ;
4. connecter GitHub si ce n'est pas deja fait ;
5. selectionner le depot `m1k124/ED3S_Map_2026` ;
6. configurer le service.

Parametres recommandes :

```text
Name: ed3s-map-2026
Branch: main
Root Directory: laisser vide
Build Command: pip install -r requirements.txt && python main.py && cp output/carte_d3s.html output/index.html
Publish Directory: output
Auto-Deploy: Yes
```

Option Blueprint :

1. ouvrir https://dashboard.render.com ;
2. cliquer sur `New` ;
3. choisir `Blueprint` ;
4. selectionner le depot `m1k124/ED3S_Map_2026` ;
5. verifier que Render detecte le fichier `render.yaml` a la racine ;
6. verifier que le service prevu s'appelle `ed3s-map-2026` ;
7. lancer `Deploy Blueprint`.

Notes :

- laisser `Root Directory` vide si `main.py`, `requirements.txt`, `data/`, `src/` et `templates/` sont a la racine du depot ;
- mettre `Root Directory` seulement si le projet est place dans un sous-dossier ;
- `Publish Directory` doit etre `output`, car c'est la que se trouve le HTML genere ;
- `output/index.html` doit exister a la fin du build.

## Phase 7 - Premier deploy et verification Render

Statut : termine le 2026-05-06.

Resultat Render :

- Blueprint Render cree depuis le depot `m1k124/ED3S_Map_2026` ;
- Blueprint ID : `exs-d7td6uf7f7vs739rafm0` ;
- service statique cree : `ed3s-map-2026` ;
- sync Render executee sur le commit `66efa4a Prepare Render static site blueprint` ;
- URL publique verifiee : `https://ed3s-map-2026.onrender.com` ;
- reponse HTTP de la racine : `HTTP/2 200` ;
- `content-type` de la racine : `text/html; charset=utf-8` ;
- HTML publie verifie avec les contenus `Constance Pascal`, `Carte interactive des avis de vacance D3S` et `Consulter Plaquette Promo` ;
- fond de carte Carto Light detecte dans le HTML publie ;
- PDF `https://ed3s-map-2026.onrender.com/plaquette-promo.pdf` verifie avec une reponse `HTTP/2 200` et `content-type: application/pdf`.

Point de vigilance restant :

- le PDF en ligne est encore le PDF temporaire ; il faudra le remplacer par la vraie plaquette officielle avant diffusion large.

Objectif : confirmer que la carte est bien accessible publiquement.

Pendant le premier deploy, lire les logs Render.

Signaux attendus :

- installation de `pandas`, `openpyxl`, `PyYAML`, `Jinja2` ;
- execution de `python main.py` ;
- logs de generation avec les compteurs ;
- creation ou copie de `output/index.html` ;
- statut final `Live`.

Une fois le site live :

1. ouvrir l'URL `https://ed3s-map-2026.onrender.com` ou le nom attribue par Render ;
2. verifier que la carte s'affiche sans devoir ajouter `/carte_d3s.html` ;
3. tester les marqueurs ;
4. tester les filtres ;
5. tester la recherche ;
6. tester l'ouverture d'une fiche poste ;
7. tester sur un autre navigateur ou en navigation privee.

Si la racine affiche une erreur ou une page vide :

- verifier que `output/index.html` existe bien dans les logs de build ;
- verifier que `Publish Directory` vaut exactement `output` ;
- verifier que la commande `cp output/carte_d3s.html output/index.html` est bien executee ;
- ouvrir temporairement `https://.../carte_d3s.html` pour confirmer que le fichier original est servi.

## Phase 8 - Cycle normal de mise a jour des donnees

Objectif : savoir comment publier une nouvelle version de la carte.

Quand un nouveau fichier Excel est disponible :

1. remplacer localement `data/postes_d3s.xlsx` ;
2. lancer localement :

```bash
source .venv/bin/activate
python main.py
cp output/carte_d3s.html output/index.html
```

3. ouvrir `output/index.html` ou `output/carte_d3s.html` ;
4. faire les controles metier ;
5. committer les changements :

```bash
git status
git add data/postes_d3s.xlsx output/carte_d3s.html output/index.html output/postes_valides.csv output/postes_sans_coordonnees.csv
git commit -m "Update ED3S map data"
git push
```

Render redeploiera automatiquement apres le push si `Auto-Deploy` est active.

Remarque : meme si Render regenere la carte pendant le build, conserver localement `output/carte_d3s.html` et `output/index.html` peut etre pratique pour verifier visuellement ce qui va etre publie.

## Phase 9 - Depannage courant

### Render echoue sur `pip install`

Verifier :

- le fichier `requirements.txt` est bien a la racine ;
- les dependances sont simples et compatibles Linux ;
- le log indique clairement quelle dependance echoue.

Commande locale utile :

```bash
pip install -r requirements.txt
```

### Render echoue sur `python main.py`

Verifier :

- `data/postes_d3s.xlsx` existe dans GitHub ;
- `data/referentiel_finess.csv` existe dans GitHub ;
- `config/settings.yaml` pointe vers les bons chemins relatifs ;
- l'onglet Excel configure existe bien.

Ligne importante dans `config/settings.yaml` :

```yaml
sheet_name: "Postes_enrichis"
```

### Le site Render est live mais la carte est blanche

Verifier dans la console navigateur :

- erreurs JavaScript ;
- chargement des fichiers Leaflet ;
- blocage reseau ;
- probleme de donnees injectees dans le HTML.

Verifier aussi que le fichier publie contient bien les donnees :

```bash
grep -n "postes" output/index.html | head
```

### Les fonds de carte ne s'affichent pas

La carte depend de ressources externes Leaflet / fonds de carte. Tester :

- depuis un autre reseau ;
- en navigation privee ;
- avec un autre navigateur.

Si un fournisseur de tuiles bloque, il faudra modifier `templates/map_template.html` pour utiliser un autre fond de carte.

### Les donnees ne changent pas apres un push

Verifier :

- le push est bien arrive sur `main` ;
- Render deploye bien la branche `main` ;
- le dernier deploy Render correspond au dernier commit ;
- le navigateur n'affiche pas une ancienne version en cache.

Render invalide normalement son cache CDN apres un deploy reussi, mais un cache navigateur local peut encore gener.

## Phase 10 - Evolution possible apres la premiere mise en ligne

Statut : corrections appliquees le 2026-05-06.

Corrections realisees :

- ajout d'un `build.sh` versionne ;
- mise a jour de `render.yaml` pour utiliser `./build.sh` comme commande Render ;
- conservation et correction du `.gitignore`, avec exclusion du fichier logo source au nom temporaire ;
- ajout d'une copie automatique de `carte_d3s.html` vers `index.html` directement dans `src/html_renderer.py` ;
- ajout d'une copie automatique des assets du dossier `static/` vers `output/` pendant la generation ;
- remplacement du logo CSS provisoire par le vrai logo JPEG de la promotion ;
- ajout de `static/promotion-logo.jpeg` ;
- ajout d'un message d'alerte dans le template si aucune donnee exploitable n'est disponible ;
- ajout d'un controle automatise `scripts/check_build_output.py` ;
- ajout d'une documentation separee `docs/MISE_A_JOUR_DONNEES.md`.

Commandes de validation :

```bash
./.venv/bin/python main.py
./.venv/bin/python scripts/check_build_output.py
```

Resultat de validation :

- generation locale OK avec 297 lignes lues, 293 postes valides, 0 poste sans coordonnees exploitable et 4 doublons supprimes ;
- `scripts/check_build_output.py` passe ;
- `build.sh` passe localement ;
- commit pousse : `d77977f Harden Render build and publish static assets` ;
- asset logo public verifie : `https://ed3s-map-2026.onrender.com/promotion-logo.jpeg` repond en `HTTP/2 200` avec `content-type: image/jpeg` ;
- HTML public corrige verifie avec `?v=d77977f`, le temps que le cache CDN de la racine se rafraichisse.

Point restant :

- remplacer le PDF temporaire `output/plaquette-promo.pdf` par la vraie plaquette officielle.

Une fois la premiere version publiee, on pourra rendre le projet plus robuste avec :

- un `build.sh` versionne ;
- un `.gitignore` propre ;
- un `render.yaml` pour documenter la configuration Render dans le depot ;
- une copie automatique `carte_d3s.html` vers `index.html` dans le code Python ;
- une page d'erreur ou un message si aucune donnee n'est disponible ;
- un controle automatise qui verifie que `output/index.html` contient bien une carte ;
- une documentation separee pour la personne qui met a jour le fichier Excel.

## Definition de fini

La mise en ligne sera consideree terminee quand :

- le depot GitHub `m1k124/ED3S_Map_2026` contient le projet nettoye ;
- le build Render passe sans erreur ;
- l'URL Render ouvre directement la carte ;
- les filtres et la recherche fonctionnent en ligne ;
- les donnees affichees correspondent au dernier fichier Excel valide ;
- la procedure de mise a jour est claire pour regenerer, committer et redeployer la carte.

# CAP - V14 ajustée

CAP est un outil d'aide à la décision destiné aux experts-comptables ex nihilo. Il compare Facebook, Instagram, TikTok et YouTube à partir de la cible, du besoin prioritaire, de l'objectif SMART, d'informations publiques actualisées et des moyens réellement disponibles.

## Architecture conservée

L'architecture visuelle de la V13 n'a pas été modifiée :

`Accueil -> Avant de commencer -> Cible -> Objectif -> Moyens -> Récapitulatif -> Analyse -> Résultat`

Aucun nouvel écran n'a été ajouté. La recherche externe est exécutée pendant l'analyse.

## Logique de décision

1. Le cabinet renseigne un persona, un besoin prioritaire, ses observations éventuelles, un objectif SMART et ses moyens.
2. CAP effectue une recherche documentaire sur des pages publiques indexées. Il ne recherche ni personnes à contacter, ni coordonnées, ni données personnelles.
3. Les quatre plateformes sont comparées selon la cible, le besoin, l'objectif, les observations et les signaux publics trouvés.
4. Lorsque plusieurs plateformes sont stratégiquement proches, les moyens peuvent les départager.
5. Lorsqu'une plateforme ressort nettement, elle reste prioritaire même si son lancement doit être préparé ou reporté.
6. CAP désigne toujours une seule plateforme prioritaire. Une plateforme complémentaire n'est proposée que si elle apporte une fonction distincte, permet la réutilisation des contenus et reste compatible avec la capacité du cabinet.
7. La faisabilité est évaluée séparément : `Projet prêt`, `Lancement à préparer` ou `Lancement à reporter`.

## Recherche publique

La recherche utilise des requêtes ciblées sur les pages publiques indexées de Facebook, Instagram, TikTok et YouTube. Les résultats sont utilisés comme signaux documentaires, pas comme mesure exhaustive de l'audience.

Si la recherche est indisponible, CAP termine le diagnostic avec les données du cabinet et son référentiel interne. Cette limite est explicitement indiquée dans le résultat et dans la synthèse PDF.

## Synthèse PDF

La synthèse contient notamment :

- le persona, le besoin et l'objectif SMART ;
- les réseaux observés et les sources renseignées ;
- la plateforme prioritaire et la plateforme complémentaire éventuelle ;
- les raisons du choix et de la non-priorisation des autres plateformes ;
- les informations publiques mobilisées et leur date ;
- les formats, compétences, matériel, responsables, appuis et budget ;
- le contrôle complet de la faisabilité ;
- les actions à réaliser avant le lancement.

## Installation

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Tests

```bash
python -m unittest discover -s tests -v
```

La recette automatisée comprend 331 tests. Dans l'environnement de préparation, 322 tests ont été exécutés avec succès et 9 tests d'interface Streamlit ont été ignorés parce que Streamlit n'y était pas installé.

## Limites

- la recherche publique dépend de l'accessibilité du moteur de recherche et des pages indexées ;
- les résultats publics ne constituent pas une analyse exhaustive des plateformes ;
- CAP n'effectue aucun démarchage, aucun envoi de message et aucune collecte de données personnelles ;
- la recommandation reste une aide à la décision à interpréter dans le respect des règles déontologiques de la profession.

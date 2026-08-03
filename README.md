# CAP — V14 corrigée et auditée

CAP est un outil d’aide à la décision destiné aux experts-comptables ex nihilo. Il compare Facebook, Instagram, TikTok et YouTube à partir de la cible, du besoin prioritaire, de l’objectif SMART, des observations documentées, d’une recherche publique facultative et des moyens réellement disponibles.

## Architecture conservée

L’architecture visuelle de la V13 n’a pas été modifiée :

`Accueil → Avant de commencer → Cible → Objectif → Moyens → Récapitulatif → Analyse → Résultat`

Aucun nouvel écran n’a été ajouté. La recherche documentaire est exécutée pendant l’analyse.

## Logique de décision

1. Le cabinet renseigne un persona, un besoin prioritaire, ses observations éventuelles, un objectif SMART et ses moyens.
2. CAP compare systématiquement les quatre plateformes.
3. Le besoin et l’objectif déterminent d’abord les plateformes stratégiquement les plus cohérentes.
4. Le réseau le plus souvent observé, le référentiel du persona et la recherche publique apportent des indices complémentaires ; aucun de ces éléments ne gagne automatiquement.
5. Lorsque plusieurs plateformes sont stratégiquement proches, les moyens peuvent les départager.
6. Lorsqu’une plateforme ressort nettement, elle reste prioritaire même si son lancement doit être préparé ou reporté.
7. CAP désigne une seule plateforme prioritaire. Une plateforme complémentaire n’est proposée que si les contenus sont réutilisables, si elle est documentée et si sa charge supplémentaire reste compatible avec le temps déclaré.
8. La faisabilité est évaluée séparément : `Projet prêt`, `Lancement à préparer` ou `Lancement à reporter`.

## Recherche publique

La recherche est facultative et utilise l’API documentée de Tavily lorsque la variable secrète `TAVILY_API_KEY` est configurée. Quatre recherches comparables sont exécutées en parallèle, une par plateforme, à partir de termes génériques issus du persona, du besoin et de l’objectif.

Les sources sont qualifiées selon leur autorité, leur pertinence et leur fraîcheur apparente. Le signal mesure la solidité documentaire trouvée pour la requête ; il ne mesure ni l’audience exhaustive ni la performance garantie d’une plateforme.

La recherche ne peut modifier un départage que si les quatre plateformes disposent d’une couverture qualifiée et comparable. Les états `partiel`, `insuffisant` et `indisponible` sont informatifs et restent neutres dans la décision.

Sans clé ou en cas d’erreur externe, CAP termine le diagnostic avec les données du cabinet et son référentiel interne. La limite est affichée dans le résultat et dans la synthèse PDF.

## Protection des informations

- aucun nom, numéro de dossier, identifiant, téléphone ou courriel ne doit être saisi ;
- les champs libres sont limités en longueur et contrôlés avant l’analyse ;
- une confirmation explicite est demandée avant la recherche ;
- aucun cache global des champs libres n’est utilisé ;
- la clé Tavily doit être enregistrée dans les secrets Streamlit, jamais dans GitHub ;
- CAP ne recherche aucun prospect, ne constitue aucune liste de contacts et ne génère aucun message de démarchage.

## Faisabilité

CAP vérifie séparément :

- le temps minimal indicatif ;
- un format structurant et un second format compatible ;
- les compétences propres à chaque format ;
- le caractère opérationnel d’un niveau `Notions` ;
- la solution prévue pour chaque compétence à acquérir ;
- le matériel ;
- le responsable ;
- le budget.

Un niveau `Notions` déjà opérationnel n’empêche pas le lancement. Une formation ou un appui n’est considéré comme prévu que s’il est rattaché à la compétence concernée et confirmé.

## Synthèse PDF

La synthèse contient notamment :

- le persona, le besoin et l’objectif SMART ;
- les réseaux observés et leurs sources ;
- la plateforme prioritaire et la plateforme complémentaire éventuelle ;
- les raisons du choix et de la non-priorisation des autres plateformes ;
- les sources publiques mobilisées, leur domaine, leur type, leur autorité et leur date disponible ;
- les formats, compétences, matériel, responsables, appuis et budget ;
- le contrôle complet de la faisabilité ;
- les actions à réaliser avant le lancement.

Les textes extrêmes sont tronqués et les chaînes longues sont sécurisées afin d’éviter un échec de génération du PDF.

## Installation locale

Python 3.12 recommandé.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows : .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Pour activer la recherche localement, créez `.streamlit/secrets.toml` à partir de `.streamlit/secrets.toml.example`, puis remplacez la valeur fictive. Ne publiez jamais ce fichier.

## Déploiement Streamlit Community Cloud

1. Déposer les fichiers à la racine du dépôt GitHub.
2. Connecter Streamlit Community Cloud au compte GitHub autorisé à lire le dépôt.
3. Créer l’application avec le dépôt, la branche et le fichier d’entrée `app.py`.
4. Dans les paramètres avancés ou les secrets de l’application, ajouter :

```toml
TAVILY_API_KEY = "tvly-votre-cle-reelle"
```

5. Déployer, puis exécuter la recette décrite dans `PLAN_RECETTE.md`.

## Tests

```bash
python -m compileall -q app.py config.py scoring.py research.py pdf_export.py tests
python -m unittest discover -s tests -v
```

La suite comprend des tests unitaires, des tests contradictoires, 275 combinaisons générales et des scénarios métier de référence avec plateforme, motif de départage, faisabilité et complément attendus. Le workflow GitHub Actions exécute automatiquement les tests à chaque modification de la branche principale et à chaque pull request.

## Limites

- les repères de temps et les référentiels de plateformes sont des aides méthodologiques à actualiser ;
- les résultats publics ne constituent pas une analyse exhaustive des plateformes ;
- une recherche complète renforce seulement un départage et ne remplace pas le diagnostic du cabinet ;
- la recette finale dans un navigateur doit être réalisée après le déploiement ;
- la recommandation reste une aide à la décision à interpréter dans le respect des règles déontologiques de la profession.

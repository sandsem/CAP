# CAP

CAP est un outil interactif d’aide au choix d’une plateforme sociale destiné
aux experts-comptables qui créent leur cabinet ex nihilo.

## Parcours

Le diagnostic suit quatre étapes :

1. décrire la cible, son besoin et la manière dont elle recherche l’information ;
2. formaliser l’objectif et l’effet recherché ;
3. indiquer les résultats déjà obtenus sur chaque plateforme ;
4. vérifier les formats, les compétences et les moyens mobilisables.

Seuls les réseaux réellement utilisés par la cible pour rechercher
l’information liée à son besoin sont comparés.

## Règle de recommandation

CAP compare Facebook, Instagram, TikTok et YouTube à partir d’une même grille :

- mode dominant de découverte du contenu ;
- traitement éditorial privilégié ;
- effet recherché auprès de l’audience ;
- cohérence avec l’objectif du cabinet.

Le profil générique du persona et le temps disponible ne donnent aucun point à
une plateforme. Aucun score sur 100 ni aucune pondération ne sont utilisés.

En cas d’égalité, CAP examine successivement :

1. les résultats déjà obtenus auprès de la cible ;
2. l’existence d’un compte actif, uniquement en l’absence de résultat ;
3. une plateforme retenue pour une période d’observation si aucun élément
   objectif ne permet encore de trancher.

## Contrôles

Les données stratégiques conduisent à l’un des résultats suivants :

- `Choix validé` ;
- `Projet à revoir` ;
- `Recommandation impossible`.

Les moyens du cabinet font l’objet d’un contrôle séparé. Chaque élément reçoit
un état vert, orange ou rouge. Une seule alerte rouge reporte le lancement. Une
alerte orange impose l’action indiquée. Toutes les lignes doivent être vertes
pour afficher `Projet prêt`.

Les moyens ne modifient jamais la cohérence stratégique de la plateforme.

## Guides de plateforme

Les guides Facebook, Instagram, TikTok et YouTube ne sont pas intégrés dans
cette version. L’application conserve uniquement l’emplacement destiné à leur
ajout. Ils seront intégrés à partir des guides validés dans le chapitre suivant.

La synthèse du diagnostic peut être téléchargée au format PDF.

## Lancement local

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

Les réponses restent dans la session Streamlit et ne sont pas enregistrées par
l’application.

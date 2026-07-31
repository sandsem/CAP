# CAP

CAP est un outil interactif d’aide au choix d’une plateforme sociale destiné
aux experts-comptables qui créent leur cabinet ex nihilo.

## Parcours

Le diagnostic suit quatre étapes :

1. analyser un persona, son besoin et la manière dont il recherche l’information ;
2. formaliser l’objectif du cabinet ;
3. indiquer, si nécessaire, les résultats déjà obtenus auprès de ce persona ;
4. vérifier les formats, les compétences et les moyens mobilisables.

Seuls les réseaux réellement utilisés par la cible pour rechercher
l’information liée à son besoin sont comparés.

Un diagnostic porte sur un seul persona. Si le cabinet souhaite étudier
plusieurs publics, il recommence le diagnostic pour chacun. La catégorie du
persona ne donne aucun avantage automatique à une plateforme.

## Règle de recommandation

CAP compare Facebook, Instagram, TikTok et YouTube à partir de deux conditions
obligatoires :

- la manière dont le persona recherche concrètement l’information sur chaque réseau ;
- la capacité de la plateforme à contribuer à l’objectif du cabinet.

L’usage est renseigné séparément pour chaque plateforme sélectionnée. Le moteur
ne compte pas des correspondances : si une condition manque, la plateforme
n’est pas compatible.

Le profil générique du persona et le temps disponible ne donnent aucun point à
une plateforme. Aucun score sur 100 ni aucune pondération ne sont utilisés.

Si plusieurs plateformes restent compatibles, CAP examine successivement :

1. un résultat déjà obtenu auprès du persona analysé pour le besoin étudié ;
2. une plateforme retenue pour une période d’observation si aucun élément
   objectif ne permet encore de trancher.

L’existence d’un compte actif, inactif ou absent ne modifie jamais ce choix.
Elle indique seulement, après la recommandation, s’il faut continuer à utiliser
un compte, le réactiver ou en créer un.

Si aucune plateforme ne remplit les deux conditions, CAP affiche
`Aucune plateforme compatible` au lieu de forcer une recommandation.

## Contrôles

Les données stratégiques conduisent à l’un des résultats suivants :

- `Choix validé` ;
- `Projet à revoir` ;
- `Recommandation impossible`.

Une plateforme n’est affichée que lorsque le contrôle stratégique aboutit à
`Choix validé`. Un projet à revoir doit d’abord être corrigé, puis analysé à
nouveau.

Les moyens du cabinet font l’objet d’un contrôle séparé. Chaque élément reçoit
un état vert, orange ou rouge. Une seule alerte rouge reporte le lancement. Une
alerte orange impose l’action indiquée. Toutes les lignes doivent être vertes
pour afficher `Projet prêt`.

Les moyens ne modifient jamais la cohérence stratégique de la plateforme.
Le contrôle porte sur le temps, les formats et compétences, le matériel, le
responsable et le budget. Il n’utilise aucun pourcentage de faisabilité.

L’aisance face caméra est demandée pour un Live. Pour une vidéo enregistrée,
elle est contrôlée seulement si une personne apparaît à l’écran.

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

## Tests

```bash
python -m unittest discover -s tests -v
```

La suite comprend 254 tests, dont une matrice de 216 scénarios croisant les
données stratégiques et les moyens du cabinet.

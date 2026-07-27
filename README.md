# CAP

Outil interactif d’aide au choix de la plateforme sociale destiné aux
experts-comptables ex nihilo.

## Fonctionnement

Le diagnostic confronte quatre dimensions :

- le profil de la cible ;
- les réseaux qu’elle utilise ;
- l’objectif du cabinet ;
- le temps disponible.

Le résultat distingue :

- l’indice de cohérence de chaque plateforme ;
- la fiabilité des informations renseignées ;
- le niveau de préparation du cabinet.

Les réponses restent uniquement dans la session Streamlit.

## Lancement local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Guides

Les guides PDF doivent être déposés dans le dossier `guides/` sous les noms
`facebook.pdf`, `instagram.pdf`, `tiktok.pdf` et `youtube.pdf`.

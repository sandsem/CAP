# Déploiement de CAP sur Streamlit Community Cloud

## Éléments nécessaires

- un dépôt GitHub contenant CAP ;
- un compte Streamlit Community Cloud connecté au compte GitHub qui peut lire le dépôt ;
- la branche à déployer, généralement `main` ;
- le fichier d’entrée `app.py` ;
- le fichier `requirements.txt` à la racine ;
- une clé Tavily pour activer la recherche externe.

La configuration actuelle utilise quatre recherches `advanced`, soit huit crédits Tavily par diagnostic. Ce choix privilégie la pertinence ; il pourra être ramené au mode `basic` si le quota devient prioritaire.

Aucun mot de passe GitHub, Streamlit ou Tavily ne doit être transmis dans une conversation.

## Configuration du secret

Dans les paramètres avancés ou l’espace **Secrets** de l’application Streamlit, ajouter :

```toml
TAVILY_API_KEY = "tvly-votre-cle-reelle"
```

La clé ne doit jamais être inscrite dans :

- `app.py` ;
- `research.py` ;
- `README.md` ;
- `.streamlit/config.toml` ;
- un commit GitHub.

Le fichier `.streamlit/secrets.toml` est exclu par `.gitignore`. Le fichier `.streamlit/secrets.toml.example` contient uniquement un modèle fictif.

## Création de l’application

1. Ouvrir Streamlit Community Cloud.
2. Choisir la création d’une nouvelle application.
3. Sélectionner le dépôt GitHub de CAP.
4. Sélectionner la branche.
5. Indiquer `app.py` comme fichier principal.
6. Ajouter le secret Tavily.
7. Lancer le déploiement.
8. Consulter les journaux de construction si une dépendance échoue.

## Recette après déploiement

Exécuter le parcours complet décrit dans `PLAN_RECETTE.md`, notamment :

- diagnostic sans clé ou avec recherche indisponible ;
- diagnostic avec recherche complète ;
- cas YouTube à préparer ;
- cas Instagram/TikTok départagé par les moyens ;
- cas sans temps disponible ;
- téléchargement des quatre guides ;
- téléchargement de la synthèse ;
- contrôle sur mobile et ordinateur.

## Élément à transmettre pour le contrôle final

Après le déploiement, seule l’adresse publique de l’application est nécessaire pour réaliser la recette finale. La clé Tavily et les identifiants restent privés.

# Fiche unique des modifications — CAP V14 corrigée et auditée

| N° | Décision ou anomalie | Statut | Mise en œuvre vérifiée |
|---:|---|---|---|
| 1 | Conserver l’architecture visuelle de la V13 | Corrigée | Aucun écran ajouté, supprimé ou déplacé. |
| 2 | Exploiter réellement le besoin prioritaire | Corrigée | Classification fonctionnelle et influence dans la sélection stratégique. |
| 3 | Comparer systématiquement les quatre plateformes | Corrigée | Les quatre plateformes sont évaluées à chaque diagnostic valide. |
| 4 | Utiliser l’ordre du référentiel du persona | Corrigée | La position, et non la simple présence dans la liste, est utilisée. |
| 5 | Utiliser le réseau le plus souvent observé | Corrigée | Indice renforcé parmi les plateformes proches, sans victoire automatique. |
| 6 | Remplacer la recherche fragile par une API documentée | Corrigée | Tavily, authentification Bearer, quatre requêtes parallèles. |
| 7 | Inclure le persona, le besoin et l’objectif dans la recherche | Corrigée | Requêtes comparables et limitées à des termes génériques. |
| 8 | Ne pas assimiler nombre de résultats et pertinence | Corrigée | Qualification par autorité, concordance, pertinence et fraîcheur apparente. |
| 9 | Neutraliser les recherches partielles ou insuffisantes | Corrigée | Seul le statut complet peut intervenir dans un départage. |
| 10 | Distinguer complet, partiel, insuffisant et indisponible | Corrigée | Statuts, messages et limites restitués dans l’application et le PDF. |
| 11 | Éviter le cache global des champs libres | Corrigée | Suppression de `st.cache_data` pour la recherche. |
| 12 | Informer sur le fournisseur externe | Corrigée | Tavily est nommé avant l’analyse ; confirmation de confidentialité obligatoire. |
| 13 | Détecter les données sensibles | Corrigée | Contrôle de tous les champs libres, avant la recommandation. |
| 14 | Limiter la longueur des champs | Corrigée | Limites dans l’interface et contrôle défensif dans le moteur. |
| 15 | Renforcer le contrôle SMART | Corrigée | Nombre strictement positif ; durée avec unité ou date future. |
| 16 | Faire intervenir les moyens dans les choix proches | Corrigée | Comparaison du niveau de faisabilité lorsque la stratégie ne départage pas. |
| 17 | Conserver une plateforme nettement supérieure | Corrigée | Les moyens modifient alors le statut de lancement, non la priorité. |
| 18 | Corriger le traitement du niveau `Notions` | Corrigée | Un niveau déjà opérationnel ne retarde pas le lancement. |
| 19 | Rattacher chaque appui à une compétence | Corrigée | Solution et confirmation enregistrées compétence par compétence. |
| 20 | Utiliser les minima de temps | Corrigée | Repères horaires par plateforme intégrés à la faisabilité. |
| 21 | Calculer la charge de la plateforme complémentaire | Corrigée | Minimum du canal principal + temps additionnel du relais. |
| 22 | Rendre la plateforme complémentaire exceptionnelle | Corrigée | Proximité, observation ou signal, réutilisation, faisabilité et capacité exigées. |
| 23 | Supprimer le départage arbitraire technique | Corrigée | Dernier recours fondé sur la priorité méthodologique de l’objectif. |
| 24 | Maintenir la faisabilité dans la synthèse | Corrigée | Statut textuel, tableau par critère et actions. |
| 25 | Sécuriser les textes extrêmes dans le PDF | Corrigée | Troncature, échappement et rupture des chaînes longues. |
| 26 | Qualifier les sources avant leur utilisation | Corrigée | Domaine, type, autorité, date disponible et pertinence contrôlés dans le module de recherche. |
| 27 | Permettre de préciser une autre source | Corrigée | Champ conditionnel limité et contrôlé. |
| 28 | Corriger les affirmations absolues des guides | Corrigée | Reformulation prudente du guide YouTube. |
| 29 | Dater le relevé des exemples publics des guides | Corrigée | Mention du 03/08/2026 et obligation d’actualisation. |
| 30 | Verrouiller les dépendances | Corrigée | Versions exactes dans `requirements.txt`. |
| 31 | Ajouter une intégration continue | Corrigée | Workflow GitHub Actions, Python 3.12, compilation et tests. |
| 32 | Tester les résultats métier attendus | Corrigée | Scénarios de référence avec gagnant, motif, faisabilité et complément attendus. |
| 33 | Tester les recherches contradictoires | Corrigée | Clé absente, couverture complète, vide, partielle et source officielle hors sujet. |
| 34 | Tester le PDF sous contrainte | Corrigée | Génération avec champs artificiellement très longs. |
| 35 | Conserver les quatre guides et le calendrier | Vérifiée | Fichiers présents et lisibles. |
| 36 | Effectuer une recette navigateur après déploiement | En cours | Nécessite une application Streamlit déployée et une clé Tavily configurée. |

## Ajustements après recette Streamlit du 3 août 2026

| N° | Modification | Statut | Mise en œuvre |
|---:|---|---|---|
| 37 | Personnaliser la synthèse avec le nom du cabinet | Corrigée | Champ ajouté au récapitulatif ; nom repris dans le PDF et le fichier téléchargé. |
| 38 | Ajouter une tranche d’âge facultative | Corrigée | La donnée affine uniquement la recherche documentaire et ne décide jamais seule de la plateforme. |
| 39 | Supprimer le vocabulaire interne du PDF | Corrigée | Suppression de « besoin interprété » et « élément déterminant ». |
| 40 | Donner la priorité aux observations fiables sur la recherche externe | Corrigée | En cas de choix stratégique proche, les réseaux observés et confirmés priment sur le signal web. |
| 41 | Rendre les justifications directement compréhensibles | Corrigée | Explications personnalisées à partir des réponses du cabinet. |
| 42 | Expliquer précisément la non-priorisation | Corrigée | Chaque plateforme reçoit un motif factuel propre au diagnostic. |
| 43 | Alléger la restitution de la recherche externe | Corrigée | Remplacement de la liste brute par un encadré court de vérification externe. |

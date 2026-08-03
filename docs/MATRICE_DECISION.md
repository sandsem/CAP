# Matrice de décision CAP — V14 corrigée et auditée

## Principe général

CAP n’affiche aucune note artificielle. Il applique une hiérarchie de règles explicites et compare systématiquement Facebook, Instagram, TikTok et YouTube.

## Données d’entrée

- persona ;
- besoin d’information prioritaire ;
- réseaux éventuellement observés, réseau le plus souvent utilisé et sources ;
- objectif SMART ;
- temps disponible ;
- formats envisageables ;
- compétences et capacité réelle à produire ;
- présence éventuelle à l’écran ;
- matériel ;
- responsable(s) ;
- appui ou formation, compétence par compétence ;
- budget.

## Contrôles avant analyse

CAP bloque la recommandation lorsque :

- le persona ou le besoin n’est pas défini ;
- plusieurs personas sont mélangés ;
- les réseaux déclarés ne sont pas accompagnés d’une source récente et fiable ;
- l’objectif ou son indicateur est incohérent ;
- le résultat attendu n’est pas un nombre positif ;
- l’échéance n’est ni une durée positive avec unité ni une date future ;
- un champ libre dépasse sa limite ;
- un courriel, téléphone ou identifiant de dossier est détecté.

## Recherche externe

Lorsque `TAVILY_API_KEY` est configurée, CAP exécute en parallèle une requête comparable pour chaque plateforme. Les requêtes utilisent des termes génériques issus du persona, du besoin et de l’objectif.

Chaque résultat est qualifié selon :

- l’autorité du domaine ;
- la concordance avec les termes du diagnostic ;
- le score de pertinence du fournisseur ;
- la présence d’un indice de fraîcheur.

Le signal `fort`, `modéré` ou `faible` décrit la solidité documentaire trouvée. Il ne constitue pas une mesure d’audience. Il ne peut intervenir dans le départage que lorsque les quatre plateformes bénéficient d’une couverture qualifiée et comparable.

Statuts :

- **complet** : comparaison utilisable comme indice de départage ;
- **partiel** : une ou plusieurs plateformes n’ont pas pu être interrogées ;
- **insuffisant** : les recherches ont abouti, mais la couverture qualifiée est incomplète ;
- **indisponible** : clé absente ou recherche impossible.

Les trois derniers statuts restent neutres.

## Sélection stratégique

CAP examine successivement :

1. la correspondance principale avec le besoin et l’objectif ;
2. la correspondance compatible et la profondeur stratégique ;
3. si plusieurs plateformes restent proches, leur faisabilité ;
4. le réseau déclaré comme le plus souvent utilisé, puis les autres réseaux observés ;
5. la recherche externe, uniquement si elle est complète ;
6. l’ordre du référentiel du persona ;
7. en dernier recours, l’ordre méthodologique associé à l’objectif.

Le dernier recours n’utilise pas l’ordre technique de la liste des plateformes.

## Intervention des moyens

### Plateforme nettement supérieure

Elle reste prioritaire. Un manque de format, de compétence, de matériel, de temps ou de responsable modifie la faisabilité : le lancement est préparé ou reporté.

### Plateformes stratégiquement proches

Les moyens peuvent les départager à partir :

- du temps minimal indicatif ;
- d’un format structurant ;
- d’un second format compatible ;
- des compétences ;
- du matériel ;
- du responsable ;
- du budget.

### Compétences

- **Autonome** : format réalisable ;
- **Notions et capacité à produire un contenu simple** : lancement possible avec conseil de progression ;
- **Notions non opérationnelles** : lancement à préparer ;
- **À acquérir avec solution précise et confirmée** : lancement à préparer ;
- **À acquérir sans solution** : lancement à reporter.

Chaque appui est rattaché à une compétence déterminée. Une formation générale ne couvre pas automatiquement toutes les compétences manquantes.

### Vidéo et face caméra

L’absence d’aisance face caméra ne rend pas la vidéo impossible. CAP admet la voix off, les captures d’écran, les visuels animés et les textes incrustés.

## Plateforme complémentaire

CAP désigne toujours une seule plateforme prioritaire. Une plateforme complémentaire n’est proposée que si :

- elle fait partie des candidates stratégiquement proches ;
- elle ne présente aucun blocage rouge ;
- une paire de réutilisation est prévue ;
- au moins un format est commun ;
- son intérêt est documenté par une observation du cabinet ou un signal externe modéré ou fort ;
- le temps déclaré couvre le minimum de la plateforme principale et la charge supplémentaire du relais.

Le résultat précise la charge mensuelle additionnelle à reporter dans le plan de charge.

## Faisabilité

- **Projet prêt** : aucune condition essentielle ne bloque le démarrage ;
- **Lancement à préparer** : un ajustement est nécessaire avant la première publication ;
- **Lancement à reporter** : au moins une condition indispensable n’est pas réunie.

La faisabilité ne remplace jamais la recommandation stratégique.

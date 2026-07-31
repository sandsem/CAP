# CAP

CAP est un outil interactif d’aide au choix d’une plateforme sociale destiné
aux experts-comptables qui créent leur cabinet ex nihilo.

## Parcours

Le diagnostic suit trois étapes :

1. analyser un seul persona, son besoin prioritaire et les réseaux qu’il utilise ;
2. définir l’objectif chiffré du cabinet ;
3. vérifier les formats, les compétences et les moyens mobilisables.

Un cabinet qui vise plusieurs personas réalise un diagnostic séparé pour
chacun. Le besoin prioritaire précise le sujet des futurs contenus ; il ne
classe pas automatiquement les plateformes.

## Moteur de recommandation

Lorsque le cabinet connaît les réseaux utilisés par le persona, cette
observation réelle est prioritaire. Elle doit être appuyée par au moins une
source et déclarée récente et fiable. Si plusieurs réseaux sont connus, le
réseau utilisé le plus souvent est retenu lorsqu’il a été identifié.

Lorsque le cabinet ne connaît pas ces réseaux, CAP utilise une base de
référence associant chaque catégorie de persona à plusieurs plateformes
probables. Cette base est datée du 31 juillet 2026 et doit être revue
périodiquement.

L’objectif sert ensuite à départager plusieurs plateformes possibles. Il ne
peut jamais éliminer le seul réseau réellement observé auprès du persona.
CAP n’utilise ni note sur 100, ni pondération, ni mode d’usage exclusif attribué
à une plateforme.

Si plusieurs plateformes restent au même niveau, les moyens du cabinet peuvent
les départager. Si l’égalité demeure, CAP recommande toutes les plateformes
équivalentes. Le cabinet en retient ensuite une pour le lancement. La synthèse
distingue clairement la recommandation de CAP du choix final du cabinet.

Les résultats déjà obtenus et l’état actif ou inactif d’un compte n’entrent pas
dans le moteur de recommandation.

## Faisabilité

Les moyens ne remplacent jamais une plateforme stratégiquement supérieure. Ils
interviennent seulement après la comparaison stratégique ou pour départager une
égalité.

La faisabilité porte sur cinq éléments :

- le temps disponible ;
- les formats et les compétences ;
- le matériel ;
- le responsable ;
- le budget.

Une ligne verte est prête. Une ligne orange impose une préparation. Une ligne
rouge reporte le lancement sans changer la plateforme recommandée.

Une compétence manquante ne bloque pas le diagnostic. Une autoformation, une
formation, un appui interne ou un prestataire peut être prévu. Un smartphone
peut suffire pour débuter ; une caméra ou une ring light ne sont pas rendues
artificiellement obligatoires.

## Interface et synthèse

Les questions sur les moyens restent neutres et ne révèlent pas la plateforme
avant le résultat. Le récapitulatif ne comporte pas de bouton « Précédent ».
L’écran final reste épuré ; les motifs, les constats et les actions figurent
dans la synthèse PDF.

Les guides Facebook, Instagram, TikTok et YouTube seront ajoutés dans le dossier
`guides` après leur validation.

## Lancement local

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## Tests

```bash
python -m unittest discover -s tests -v
```

La suite comprend 306 tests : 275 scénarios de décision croisant les personas,
les objectifs et les situations réseau, ainsi que des tests du moteur, de la
faisabilité, de l’interface et de l’export PDF.

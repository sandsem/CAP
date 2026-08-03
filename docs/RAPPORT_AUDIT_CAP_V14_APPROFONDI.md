> **Document historique.** Cet audit décrit l’état de la première V14 avant correction. Les anomalies qu’il recense ont été traitées dans la version actuelle. La traçabilité des corrections figure dans `RAPPORT_CORRECTIONS_AUDIT_V14.md` et dans la fiche unique.

# Rapport d’audit approfondi — CAP V14 ajustée

**Version auditée :** `CAP_V14_ajustee_GitHub.zip`  
**Date de l’audit :** 3 août 2026  
**Périmètre :** conformité au cahier des charges, logique de décision, cohérence fonctionnelle, robustesse technique, qualité de la recherche externe, protection des données, tests, synthèse PDF, guides et calendrier éditorial.

---

## 1. Conclusion générale

### Avis d’audit

**CAP V14 ne doit pas encore être figée, déposée comme version définitive sur GitHub ni décrite dans le mémoire comme outil validé.**

L’application est techniquement structurée et plusieurs éléments sont conformes : architecture visuelle conservée, parcours en trois étapes, recommandation unique, faisabilité maintenue dans la synthèse, téléchargement du guide et du calendrier, génération normale du PDF et présence de contrôles bloquants.

Cependant, des anomalies importantes affectent la valeur même de la recommandation :

1. la recherche externe ne correspond pas encore à la recherche documentaire attendue ;
2. l’ordre du référentiel des personas n’est pas exploité par le moteur ;
3. le réseau déclaré comme le plus utilisé est demandé, affiché, mais n’influence pas la décision ;
4. une recherche vide ou partiellement indisponible peut être présentée comme une recherche « réalisée » ;
5. le cache et l’information donnée à l’utilisateur sont insuffisants au regard des données envoyées à un moteur externe ;
6. le contrôle SMART accepte des valeurs négatives ou des échéances sans unité de temps ;
7. la règle appliquée au niveau « Notions » n’est pas conforme à la logique finalement validée ;
8. les 275 scénarios automatiques vérifient qu’une réponse existe, mais pas que la plateforme recommandée est la bonne.

### Évaluation synthétique

| Axe | Avis |
|---|---|
| Architecture et parcours visuel | Conforme |
| Présence de la faisabilité dans la synthèse | Conforme |
| Intégrité technique de base | Conforme avec réserve |
| Logique stratégique de recommandation | Non conforme |
| Exploitation du persona et des observations | Non conforme |
| Recherche externe | Non conforme |
| Protection des données et transparence | Non conforme |
| Contrôle SMART | Non conforme |
| Tests métier | Partiellement conformes |
| PDF et livrables | Globalement conformes, corrections nécessaires |
| Guides | Utilisables, mais certaines formulations doivent être sécurisées |
| Calendrier éditorial | Conforme sur le plan structurel |

---

## 2. Travaux réalisés

L’audit a comporté :

- l’extraction et l’inspection de tous les fichiers du ZIP ;
- la lecture de `app.py`, `config.py`, `scoring.py`, `research.py` et `pdf_export.py` ;
- la comparaison de l’architecture de l’interface avec la V13 présente sur GitHub ;
- l’exécution de la suite automatisée ;
- des tests contradictoires non prévus dans la suite initiale ;
- la génération et le rendu visuel d’une synthèse PDF ;
- des essais avec des champs anormalement longs ;
- l’inspection des quatre guides ;
- le contrôle du calendrier éditorial et de ses formules ;
- l’analyse de la cohérence entre le code, la fiche unique, la matrice et le plan de recette.

### Résultat des tests existants

- **331 tests exécutés** ;
- **322 réussis** ;
- **9 ignorés**, car Streamlit n’était pas disponible dans l’environnement d’audit ;
- compilation Python réussie.

Ce résultat démontre l’absence de régression évidente sur les cas testés. Il ne prouve pas la justesse métier de toutes les recommandations.

---

## 3. Points conformes

### 3.1 Architecture visuelle et parcours

L’architecture annoncée est conservée :

> Accueil → Avant de commencer → Cible → Objectif → Moyens → Récapitulatif → Analyse → Résultat

La recherche est déclenchée dans la phase d’analyse et n’ajoute pas de nouvel écran. Les styles, le nombre d’étapes et l’organisation générale restent proches de la V13.

### 3.2 Une plateforme prioritaire unique

Le moteur retourne une seule plateforme prioritaire lorsqu’aucun contrôle stratégique ne bloque le diagnostic. Il ne renvoie plus l’arbitrage final à l’utilisateur.

### 3.3 Plateforme complémentaire non automatique

La plateforme complémentaire est soumise à plusieurs conditions : temps disponible, proximité stratégique, possibilité de réutiliser le contenu, compatibilité des formats et présence d’un signal favorable. Elle n’apparaît donc pas systématiquement.

### 3.4 Faisabilité maintenue

La faisabilité est bien présente :

- sur l’écran final ;
- dans la synthèse PDF ;
- sous forme de tableau détaillé ;
- avec les statuts `Projet prêt`, `Lancement à préparer` et `Lancement à reporter` ;
- avec les actions à mener et les acteurs mobilisés.

Elle n’a donc pas été supprimée.

### 3.5 PDF en usage normal

Sur un jeu de données normal, le PDF est généré, lisible et contient :

- les informations saisies ;
- la plateforme prioritaire ;
- la plateforme complémentaire éventuelle ;
- le besoin interprété ;
- la faisabilité ;
- les raisons du choix ;
- les alternatives ;
- les moyens et actions ;
- les sources externes lorsqu’elles existent ;
- la notice déontologique.

### 3.6 Calendrier éditorial

Le classeur comporte neuf onglets, les formules contrôlées ne présentent pas d’erreur détectée et le tableau de bord est visuellement exploitable.

---

## 4. Anomalies bloquantes

## 4.1 Recherche externe trop limitée et insuffisamment fiable

### Constat

Le module `research.py` ne réalise pas encore la recherche documentaire validée. Il envoie quatre requêtes à l’interface HTML de DuckDuckGo, sous la forme :

```text
site:facebook.com [persona] [besoin]
site:instagram.com [persona] [besoin]
site:tiktok.com [persona] [besoin]
site:youtube.com [persona] [besoin]
```

Il compte ensuite les résultats dont le titre ou l’extrait partage quelques mots avec le contexte :

- trois résultats ou plus : signal fort ;
- un résultat ou plus : signal modéré ;
- aucun résultat : signal faible.

### Pourquoi cela ne suffit pas

Cette méthode :

- ne recherche pas les études d’audience ;
- ne consulte pas les documentations officielles des plateformes ;
- ne vérifie pas la date de publication ;
- ne mesure ni la qualité ni l’autorité de la source ;
- ne lit pas réellement le contenu des pages ;
- n’utilise pas l’objectif dans la requête ;
- assimile le nombre de résultats indexés à un signal de pertinence ;
- dépend d’une interface HTML non conçue comme une API structurée de production.

Elle ne correspond donc pas encore à la logique attendue : **référentiel interne + informations publiques actuelles + sources qualifiées + arbitrage transparent**.

### Correction requise

Construire une recherche hybride et documentée :

1. sources officielles des plateformes et études reconnues ;
2. recherche web générale sur la cible, le besoin et l’objectif ;
3. API officielle lorsqu’elle est réellement accessible, notamment YouTube ;
4. qualification de chaque source : autorité, date, type de donnée et pertinence ;
5. séparation entre données générales sur les usages et exemples publics de contenus ;
6. conservation d’un mode de repli interne lorsque les données externes sont insuffisantes.

---

## 4.2 Le persona n’influence pas réellement le classement

### Constat

`PERSONA_PLATFORM_REFERENCE` classe les quatre plateformes dans un ordre différent selon le persona. Cependant, le moteur vérifie uniquement si la plateforme figure dans la liste :

```python
target_fit = 2 if platform in known else (1 if platform in reference else 0)
```

Comme les quatre plateformes figurent dans chaque liste, elles reçoivent toutes la même valeur `1` lorsqu’aucun réseau n’est observé.

### Test contradictoire

Pour plusieurs personas très différents, le moteur a produit exactement les mêmes valeurs de compatibilité avec la cible :

```text
Facebook = 1
Instagram = 1
TikTok = 1
YouTube = 1
```

L’ordre prévu dans le référentiel n’a donc aucun effet.

### Correction requise

Exploiter le rang sans créer une note artificielle opaque. Par exemple :

- premier choix du référentiel : indice prioritaire ;
- deuxième : indice favorable ;
- troisième : indice secondaire ;
- quatrième : indice faible ;

ou utiliser une hiérarchie de règles explicite équivalente. La méthode et sa source doivent être documentées.

---

## 4.3 Le réseau le plus utilisé est demandé mais ignoré

### Constat

La réponse `q4_priority` est :

- demandée dans l’interface ;
- contrôlée ;
- affichée dans le récapitulatif ;
- reproduite dans le PDF.

Mais elle n’est jamais utilisée dans la comparaison. Dans `scoring.py`, elle sert uniquement à vérifier que la réponse appartient aux réseaux précédemment sélectionnés.

### Conséquence

Changer le réseau déclaré comme le plus utilisé ne modifie pas le résultat. CAP demande donc une information qui n’a pas de valeur décisionnelle.

### Correction requise

L’intégrer comme **niveau de preuve plus fort** que la simple présence parmi plusieurs réseaux, sans en faire un gagnant automatique. Il doit renforcer une plateforme lorsque l’observation est fiable, puis être croisé avec le besoin, l’objectif, la recherche externe et les moyens.

---

## 4.4 Gestion incorrecte d’une recherche vide ou partielle

### Constat 1 — Recherche vide

Lorsque les quatre requêtes aboutissent techniquement, mais ne retournent aucun résultat pertinent, le module indique :

```text
status = live
```

L’écran affirme alors qu’une recherche publique a été réalisée, même si aucune source n’a été trouvée.

### Constat 2 — Recherche partielle

Dès qu’une seule plateforme ne déclenche pas d’erreur technique, le statut global devient `live`. Les autres peuvent être `indisponible`.

### Risque

Un écart de disponibilité technique entre plateformes peut entrer dans le moteur comme s’il s’agissait d’un écart réel de pertinence. Les plateformes ne sont alors plus comparées sur une base homogène.

### Correction requise

Prévoir au moins quatre états :

- `complet` : couverture comparable des quatre plateformes ;
- `partiel` : certaines plateformes ou sources manquent ;
- `insuffisant` : résultats trop faibles pour influencer le choix ;
- `indisponible` : recherche impossible.

Le signal externe ne doit départager les plateformes que si la couverture est comparable et suffisamment documentée. Dans tous les autres cas, il doit rester informatif et ne pas modifier le classement.

---

## 4.5 Protection des données et information de l’utilisateur

### Constat

Le persona, le besoin et l’objectif sont envoyés à un moteur de recherche externe. La fonction est décorée ainsi :

```python
@st.cache_data(ttl=21600)
```

Le résultat mis en cache contient également le contexte textuel exact. Par ailleurs, l’interface indique :

> Les réponses sont supprimées à la fermeture de la session.

### Problème

Cette phrase est trop absolue : le cache Streamlit n’est pas, par défaut, limité à la seule session de l’utilisateur. De plus, le formulaire ne prévient pas clairement que certains champs sont transmis à un service externe de recherche.

### Correction requise

- interdire explicitement toute donnée nominative, confidentielle ou issue d’un dossier client ;
- expliquer avant la saisie que le persona, le besoin et l’objectif servent à une recherche publique externe ;
- ne pas mettre en cache le texte libre brut ou utiliser une stratégie strictement limitée à la session ;
- retirer le contexte exact du résultat conservé ;
- remplacer la phrase de suppression par une information précise et vérifiable ;
- prévoir une courte notice sur la finalité, les destinataires techniques et la durée de conservation.

---

## 4.6 Contrôle SMART défaillant

### Constat

La fonction `_positive_number` extrait toute suite de chiffres, sans tenir compte du signe ni du sens de la phrase.

### Cas acceptés à tort

```text
Résultat attendu : -5
Échéance : -3 mois

Résultat attendu : 10
Échéance : 2026

Résultat attendu : abc10
Échéance : demain 2
```

Dans les trois cas, le contrôle retourne `Choix validé`.

### Correction requise

- utiliser un champ numérique structuré pour la cible ;
- refuser les nombres négatifs ou nuls ;
- séparer la durée et son unité ;
- exiger une unité parmi jours, semaines, mois ou années ;
- ou accepter une date future au moyen d’un champ date ;
- ajouter les tests négatifs correspondants.

---

## 4.7 Niveau « Notions » non conforme à la règle validée

### Constat

Le moteur classe automatiquement toute compétence au niveau `Notions` en orange et exige :

> Réaliser la formation ou l’entraînement nécessaire avant le lancement.

### Incohérence

La logique validée était plus nuancée : le niveau `Notions` ne doit pas automatiquement empêcher de commencer. Il doit conduire à un renforcement lorsque le cabinet peut déjà produire les formats nécessaires. Il ne doit retarder le lancement que si la compétence est indispensable à un format structurant et que le niveau déclaré ne permet pas réellement de le produire.

### Correction requise

Distinguer :

- `Notions mais format réalisable` → Projet prêt avec recommandation de progression ;
- `Notions insuffisantes pour un format essentiel` → Lancement à préparer ;
- `À acquérir sans solution` → Lancement à reporter.

---

## 4.8 Les scénarios métier ne valident pas la pertinence du résultat

### Constat

Les 275 scénarios générés vérifient uniquement que :

- le statut est valide ;
- le gagnant appartient aux quatre plateformes ;
- une seule plateforme est retournée ;
- il n’existe pas d’égalité.

Ils ne définissent jamais le résultat métier attendu pour chaque cas.

### Conséquence

Une recommandation incohérente peut passer tous les tests dès lors qu’elle retourne l’un des quatre noms.

### Correction requise

Créer un jeu de scénarios de référence comprenant, pour chaque cas :

- les données d’entrée ;
- la plateforme attendue ;
- la raison déterminante ;
- le statut de faisabilité attendu ;
- l’existence ou non d’une plateforme complémentaire.

Les tests doivent couvrir notamment :

- persona réellement influent ;
- réseau prioritaire observé influent mais non automatique ;
- recherche complète, vide, partielle et indisponible ;
- plateforme clairement supérieure mais lancement retardé ;
- plateformes proches départagées par les moyens ;
- `Notions` non bloquantes ;
- valeurs SMART négatives ou ambiguës ;
- refus d’un format essentiel ;
- absence de responsable ;
- budget non validé.

---

## 5. Anomalies importantes mais non bloquantes isolément

## 5.1 Départage final dépendant de l’ordre de la liste

Lorsque tous les critères restent identiques, le moteur choisit la première plateforme dans `PLATFORM_NAMES`. Cette règle est stable techniquement, mais n’a pas de justification méthodologique suffisante.

**Correction :** définir une dernière règle métier explicite ou signaler que les données sont insuffisantes, tout en proposant une plateforme de test justifiée par les moyens les plus simples.

## 5.2 Temps minimal par plateforme déclaré mais peu exploité

`PLATFORM_MINIMUM_TIME` existe dans `config.py`, mais n’est pas utilisé dans le moteur. Seul YouTube fait l’objet d’une règle particulière pour la tranche `2 à 5 h`.

**Correction :** intégrer ces minima comme repères adaptables, sans prétendre à des seuils universels, et les relier au plan de charge.

## 5.3 Charge cumulée de la plateforme complémentaire non calculée

La plateforme complémentaire exige au moins `6 à 10 h`, mais CAP ne calcule pas le temps cumulé de la plateforme prioritaire et du relais.

**Correction :** définir une charge additionnelle limitée et une fréquence de relais, ou renvoyer au plan de charge avant de confirmer la plateforme complémentaire.

## 5.4 Appui non rattaché à chaque compétence

Une seule solution d’appui confirmée peut rendre orange l’ensemble des compétences manquantes, même si elle ne couvre pas chacune d’elles.

**Correction :** demander à quelle compétence répond chaque solution, ou présenter une confirmation simple par compétence essentielle.

## 5.5 Champs libres sans limite

Les champs texte n’ont pas de longueur maximale. Le PDF fonctionne avec environ 1 000 caractères, mais des essais à 5 000 et 20 000 caractères ont provoqué une erreur de mise en page ReportLab.

**Correction :** limiter les champs et sécuriser le PDF par découpage ou troncature contrôlée.

## 5.6 Source « Autre » insuffisamment documentée

L’utilisateur peut sélectionner `Autre source`, mais aucun champ ne lui permet de préciser laquelle. La qualité récente et fiable repose sur une simple déclaration `Oui`.

**Correction :** ajouter un champ court facultatif pour le nom, le lien ou la date de la source, uniquement lorsque `Autre source` est sélectionnée.

## 5.7 Performance de la recherche

Les quatre plateformes sont interrogées séquentiellement. Chaque recherche peut effectuer deux requêtes avec un délai maximal de sept secondes, soit un temps théorique élevé en cas de panne ou de lenteur.

**Correction :** paralléliser avec prudence, réduire les délais, limiter les tentatives et informer clairement l’utilisateur.

## 5.8 PDF

Le PDF est lisible, mais :

- une page comporte un espace blanc important à cause d’un saut de page forcé ;
- les lignes de faisabilité reposent beaucoup sur la couleur ;
- les sources ne précisent pas toujours leur date, leur type ou leur autorité ;
- les champs très longs peuvent interrompre la génération.

**Correction :** ajouter un libellé textuel de statut, améliorer la pagination et enrichir la présentation des sources.

## 5.9 Guides

Les guides s’ouvrent correctement. Le guide YouTube contient cependant des éléments à sécuriser :

- nombres d’abonnés susceptibles d’évoluer, sans date ni source visible ;
- formulation « booster sa visibilité gratuitement » ;
- formulation « les résultats sont réels si la méthode utilisée est sérieuse et constante ».

Ces phrases sont trop absolues ou rapidement périssables.

**Correction :** dater et sourcer les données, puis remplacer les promesses par des formulations prudentes : potentiel de visibilité, absence de frais d’ouverture du compte, résultats dépendant du contexte et de la régularité.

## 5.10 Reproductibilité technique

Les dépendances sont définies par plages de versions, sans fichier de verrouillage. Aucun workflow GitHub Actions n’exécute automatiquement les tests.

**Correction :** ajouter un fichier de versions validées et un contrôle continu minimal.

---

## 6. Conformité déontologique et fonctionnelle

### Points favorables

CAP :

- ne recherche pas de personnes à contacter ;
- ne constitue pas de fichier de prospects ;
- n’envoie pas de message ;
- ne propose pas de sollicitation individualisée ;
- présente une notice recommandant une communication informative, exacte et mesurée ;
- ne compare pas le cabinet à ses confrères dans ses résultats.

### Réserves

La conformité globale ne peut pas encore être déclarée complète, car :

- la transmission des champs à un moteur externe n’est pas suffisamment expliquée ;
- certaines formulations des guides sont trop affirmatives ;
- la qualité et la date des sources externes ne sont pas contrôlées.

---

## 7. Plan de correction recommandé

### Bloc 1 — Corrections indispensables avant toute rédaction

1. Reconcevoir la recherche externe et ses sources.
2. Exploiter réellement l’ordre du référentiel persona.
3. Utiliser le réseau le plus fréquent comme preuve renforcée.
4. Neutraliser la recherche vide, partielle ou non comparable.
5. Corriger le cache, la notice et la protection des champs libres.
6. Corriger le contrôle SMART.
7. Appliquer la bonne règle au niveau `Notions`.
8. Ajouter des scénarios avec résultats métier attendus.

### Bloc 2 — Sécurisation avant gel de la V14

9. Limiter les longueurs des champs et sécuriser le PDF.
10. Relier le temps minimal et le cumul des plateformes au plan de charge.
11. Rattacher les solutions aux compétences concernées.
12. Préciser la source `Autre`.
13. Corriger les formulations et données périssables des guides.
14. Ajouter un test réel sur Streamlit Cloud et, idéalement, une intégration continue.

### Bloc 3 — Recette finale

Après correction :

- exécuter les tests unitaires ;
- exécuter les nouveaux scénarios métier ;
- tester manuellement tous les écrans ;
- tester une recherche complète, partielle, vide et indisponible ;
- générer les PDF des trois statuts ;
- tester les quatre guides ;
- vérifier le fonctionnement sur mobile ;
- figer la fiche unique et la matrice ;
- seulement ensuite rédiger le paragraphe 1 de la section 3.

---

## 8. Décision d’audit

### Décision actuelle

**V14 à corriger avant validation.**

Le socle est récupérable et l’architecture n’a pas besoin d’être refaite. Les corrections concernent principalement le moteur de décision, la recherche externe, la protection des données, les contrôles et les tests métier.

### Conséquence pour le mémoire

Le paragraphe 1 de la section 3 ne doit pas encore être rédigé dans sa version définitive. Le décrire maintenant conduirait à présenter comme validées des fonctions qui ne sont pas encore fiables ou conformes à la logique arrêtée.

La prochaine étape correcte est :

> corriger les anomalies bloquantes → effectuer la recette réelle → figer CAP V14 → construire le schéma de fonctionnement → rédiger le paragraphe 1.

---

## 9. Sources officielles à mobiliser pour les corrections

- Documentation YouTube Data API — recherche de vidéos, chaînes et playlists : https://developers.google.com/youtube/v3/docs/search/list
- Documentation TikTok Research API et conditions d’éligibilité : https://developers.tiktok.com/doc/research-api-get-started
- Documentation Streamlit sur `st.cache_data` : https://docs.streamlit.io/develop/api-reference/caching-and-state/st.cache_data
- CNIL — information des personnes et transparence : https://www.cnil.fr/fr/respecter-les-droits-des-personnes
- Article 152 du Code de déontologie des experts-comptables : https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000029387074
- DuckDuckGo — interfaces HTML et Lite et règles d’utilisation : https://duckduckgo.com/duckduckgo-help-pages/settings/params et https://duckduckgo.com/terms

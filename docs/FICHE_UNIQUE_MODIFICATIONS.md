# Fiche unique des modifications de CAP

Version consolidée après les sections 1 et 2 du chapitre.

| N° | Modification décidée | État | Mise en œuvre |
|---:|---|---|---|
| 1 | Conserver uniquement les réseaux sur lesquels la cible recherche l’information liée à son besoin | Intégrée | Filtre d’éligibilité appliqué avant toute comparaison |
| 2 | Supprimer les notes sur 100 et les pondérations 60/35/5 | Intégrée | Moteur remplacé par des correspondances explicites |
| 3 | Supprimer l’affinité automatique entre un profil générique et une plateforme | Intégrée | Le profil décrit la cible mais ne classe plus les réseaux |
| 4 | Comparer les plateformes selon le mode de découverte, le traitement éditorial et l’effet recherché | Intégrée | Grille unique enregistrée dans `config.py` |
| 5 | Rapprocher ces critères de l’objectif du cabinet | Intégrée | L’objectif forme une correspondance supplémentaire, sans pondération |
| 6 | Faire intervenir les résultats déjà obtenus seulement en cas d’égalité | Intégrée | Les contacts obtenus puis l’audience cible engagée départagent les plateformes |
| 7 | Utiliser le compte actif seulement en dernier recours | Intégrée | Le compte actif intervient uniquement en l’absence de résultat qualifié |
| 8 | Ne pas forcer une recommandation lorsque l’égalité demeure | Intégrée | CAP affiche les plateformes équivalentes |
| 9 | Permettre une période d’observation en cas d’égalité | Intégrée | CAP présente l’égalité et invite à retenir une plateforme sans la déclarer supérieure |
| 10 | Remplacer la question générique sur le format principal | Intégrée | La question reste neutre ; les formats sont filtrés en arrière-plan sans révéler la plateforme |
| 11 | Vérifier uniquement les compétences utiles aux formats retenus | Intégrée | Rédaction, création de visuels, montage vidéo et face caméra sont appelés selon les formats |
| 12 | Séparer la recommandation stratégique de la faisabilité | Intégrée | Le temps, les compétences, le matériel, l’organisation et le budget ne modifient plus la plateforme |
| 13 | Afficher les trois contrôles : choix validé, projet à revoir, recommandation impossible | Intégrée | Contrôle des données stratégiques ajouté au résultat |
| 14 | Appliquer la grille verte, orange et rouge aux moyens | Intégrée | Cinq critères de faisabilité sont contrôlés |
| 15 | Une alerte rouge reporte le lancement | Intégrée | La couleur la plus défavorable détermine la décision |
| 16 | Une alerte orange doit produire une action précise | Intégrée | Chaque ligne orange ou rouge contient l’action à réaliser |
| 17 | Toutes les réponses doivent être vertes pour lancer le projet | Intégrée | Le résultat `Projet prêt` exige cinq lignes vertes |
| 18 | Prévoir l’emplacement du guide associé à la plateforme retenue | À intégrer après validation des guides | Bouton désactivé ; aucun contenu de guide n’est ajouté |
| 19 | Intégrer une promesse éditoriale dans le guide | Reportée | À intégrer dans les futurs guides validés |
| 20 | Prévoir des rubriques ou rendez-vous réguliers | Reportée | À intégrer dans les futurs guides validés |
| 21 | Prévoir l’entretien du dialogue avec l’audience | Reportée | À intégrer dans les futurs guides validés |
| 22 | Conserver les réponses uniquement pendant la session | Maintenue | Aucun enregistrement ajouté |
| 23 | Mettre à jour la documentation et les tests | Intégrée | README, grille de décision et tests réécrits |
| 24 | Clarifier le regroupement de plusieurs profils | Intégrée | La question vérifie une même information recherchée sur les mêmes réseaux et indique l’action à réaliser |
| 25 | Supprimer l’option imprécise « Plusieurs usages » | Intégrée | Plusieurs modes précis peuvent être sélectionnés directement |
| 26 | Remplacer « concordantes » par un terme simple | Intégrée | Les informations sont qualifiées de récentes et fiables |
| 27 | Ne pas révéler la plateforme avant le résultat | Intégrée | Le nom du réseau n’apparaît plus dans l’étape consacrée aux moyens |
| 28 | Supprimer la question imprécise sur l’organisation de l’aide | Intégrée | La solution retenue n’est demandée que lorsqu’une compétence doit être renforcée |
| 29 | Ne pas compter séparément l’aide et les compétences | Intégrée | La solution choisie est contrôlée dans la ligne `Formats et compétences` |
| 30 | Simplifier le contrôle du budget | Intégrée | La question vérifie uniquement si les dépenses nécessaires peuvent être financées |
| 31 | Ne recommander aucune plateforme lorsque le projet est à revoir | Intégrée | Seul le statut `Choix validé` autorise une recommandation |
| 32 | Épurer l’écran final | Intégrée | Le résultat principal et les actions utiles restent à l’écran ; le détail est déplacé dans la synthèse |
| 33 | Nommer les compétences manquantes | Intégrée | Le constat indique précisément les compétences à acquérir ou à renforcer |
| 34 | Colorer les lignes de faisabilité dans la synthèse | Intégrée | La colonne `État` est supprimée et le fond de chaque ligne porte la couleur du constat |
| 35 | Ne pas afficher de pourcentage de faisabilité | Intégrée | La règle de blocage par la situation la plus défavorable est conservée sans score artificiel |
| 36 | Renforcer les tests de la logique de décision | Intégrée | 216 scénarios croisés complètent les tests fonctionnels existants, soit 240 tests au total |

# Fiche unique des modifications de CAP

Version consolidée après les sections 1 et 2 du chapitre.

| N° | Modification décidée | État | Mise en œuvre |
|---:|---|---|---|
| 1 | Conserver uniquement les réseaux sur lesquels la cible recherche l’information liée à son besoin | Intégrée | Filtre d’éligibilité appliqué avant toute comparaison |
| 2 | Supprimer les notes sur 100 et les pondérations 60/35/5 | Intégrée | Moteur remplacé par deux conditions obligatoires, sans addition ni classement par points |
| 3 | Supprimer l’affinité automatique entre un profil générique et une plateforme | Intégrée | Le profil décrit la cible mais ne classe plus les réseaux |
| 4 | Comparer les plateformes selon la manière dont le persona y recherche l’information | Intégrée | L’usage est renseigné séparément pour chaque réseau sélectionné |
| 5 | Rapprocher cet usage de l’objectif du cabinet | Intégrée | L’usage et l’objectif sont deux conditions obligatoires ; une seule condition manquante écarte la plateforme |
| 6 | Faire intervenir les résultats déjà obtenus seulement en cas d’égalité | Intégrée | Une audience cible engagée ou des contacts obtenus auprès du persona peuvent départager les plateformes, sans hiérarchie artificielle entre ces résultats |
| 7 | Supprimer l’état du compte des critères de départage | Intégrée | Un compte actif, inactif ou absent ne modifie plus la recommandation ; sa réutilisation, sa réactivation ou sa création relève seulement du lancement opérationnel |
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
| 24 | Limiter chaque diagnostic à un seul persona | Intégrée | Le choix multiple et la question de regroupement sont supprimés ; un autre persona impose un autre diagnostic |
| 25 | Supprimer l’option imprécise « Plusieurs usages » | Intégrée | Plusieurs modes précis peuvent être sélectionnés directement |
| 26 | Remplacer « concordantes » par un terme simple | Intégrée | Les informations sont qualifiées de récentes et fiables |
| 27 | Ne pas révéler la plateforme avant le résultat | Intégrée | Le nom du réseau n’apparaît plus dans l’étape consacrée aux moyens |
| 28 | Supprimer la question imprécise sur l’organisation de l’aide | Intégrée | La solution retenue n’est demandée que lorsqu’une compétence doit être renforcée |
| 29 | Ne pas compter séparément l’aide et les compétences | Intégrée | La solution choisie est contrôlée dans la ligne `Formats et compétences` |
| 30 | Simplifier le contrôle du budget | Intégrée | La question vérifie uniquement si les dépenses nécessaires peuvent être financées |
| 31 | Ne recommander aucune plateforme lorsque le projet est à revoir | Intégrée | Seul le statut `Choix validé` autorise une recommandation |
| 32 | Épurer l’écran final | Intégrée | Seuls le résultat et le téléchargement restent à l’écran ; toutes les actions sont déplacées dans la synthèse |
| 33 | Nommer les compétences manquantes | Intégrée | Le constat indique précisément les compétences à acquérir ou à renforcer |
| 34 | Colorer les lignes de faisabilité dans la synthèse | Intégrée | La colonne `État` est supprimée et le fond de chaque ligne porte la couleur du constat |
| 35 | Ne pas afficher de pourcentage de faisabilité | Intégrée | La règle de blocage par la situation la plus défavorable est conservée sans score artificiel |
| 36 | Renforcer les tests de la logique de décision | Intégrée | 216 scénarios croisés complètent les tests fonctionnels et métier, soit 254 tests au total |
| 37 | Remplacer les états partiels du persona et du besoin par une règle binaire | Intégrée | Le persona est défini ou non ; le besoin est validé par la présence d’un besoin d’information précis |
| 38 | Conserver le besoin prioritaire comme lien entre le persona et ses usages | Intégrée | Les réseaux sont renseignés pour le besoin observé, sans rattachement automatique du profil à une plateforme |
| 39 | Rendre l’aisance face caméra conditionnelle | Intégrée | Elle est contrôlée si une personne apparaît dans une vidéo et systématiquement pour un Live |
| 40 | Regrouper les contrôles de faisabilité par couleur dans le PDF | Intégrée | Les lignes vertes précèdent les lignes orange puis rouges ; le fond de la ligne porte la couleur |
| 41 | Reformuler l’action liée aux informations partiellement vérifiées | Intégrée | CAP demande de confirmer les réseaux utilisés par le persona à l’aide d’une source récente |
| 42 | Supprimer le traitement éditorial et l’effet recherché du diagnostic | Intégrée | Les deux questions, leurs règles et leur affichage dans la synthèse ont été retirés |
| 43 | Supprimer le comptage caché des correspondances | Intégrée | Le moteur ne recherche plus le plus grand nombre de critères remplis |
| 44 | Relier chaque usage au réseau concerné | Intégrée | Une question distincte est posée pour Facebook, Instagram, TikTok ou YouTube lorsqu’ils sont sélectionnés |
| 45 | Reconnaître l’absence de plateforme compatible | Intégrée | CAP n’impose ni recommandation ni égalité lorsqu’aucun réseau ne remplit les deux conditions |
| 46 | Limiter le départage aux résultats du persona analysé | Intégrée | Les résultats d’un autre public ne peuvent pas influencer la recommandation |
| 47 | Ne pas classer artificiellement deux résultats différents | Intégrée | Si plusieurs plateformes ont déjà produit un résultat auprès du persona, l’égalité est conservée |

# Plan de recette — CAP V14 corrigée et auditée

## 1. Contrôles automatiques

```bash
python -m compileall -q app.py config.py scoring.py research.py pdf_export.py tests
python -m unittest discover -s tests -v
```

Vérifier également le workflow GitHub Actions après le premier dépôt.

## 2. Parcours complet dans Streamlit

1. Accueil et écran de préparation.
2. Blocage si le persona n’est pas finalisé.
3. Limites de longueur des champs.
4. Rejet d’un courriel, téléphone ou identifiant dans chaque champ libre.
5. Saisie du persona, du besoin et des observations.
6. Contrôle des sources et précision de `Autre source`.
7. Contrôle SMART : nombres négatifs, zéro, date passée, durée sans unité.
8. Questions conditionnelles sur les formats, compétences et appuis.
9. Appui rattaché à chaque compétence.
10. Affichage de tous les réseaux observés dans le récapitulatif.
11. Confirmation de confidentialité obligatoire.
12. Recherche publique pendant l’analyse, sans nouvel écran.
13. Une seule plateforme prioritaire.
14. Plateforme complémentaire uniquement dans les cas éligibles.
15. Présence du bloc de faisabilité.
16. Téléchargement de la synthèse PDF.
17. Téléchargement du guide correspondant.
18. Nouveau diagnostic sans reprise indésirable des anciennes réponses.
19. Affichage mobile et écran large.

## 3. Scénarios métier de référence

### Besoin complexe et réseau observé différent

- Persona : micro-entrepreneur.
- Besoin : passage de la micro-entreprise à une société.
- Réseau observé : Instagram.
- Objectif : expertise et conseil.
- Formats : carrousel uniquement.

Attendu : YouTube prioritaire ; lancement à préparer ; aucune plateforme complémentaire.

### Instagram et TikTok proches

- Persona : start-up.
- Objectif : visibilité.
- Réseaux observés : Instagram et TikTok.
- Formats : photo et carrousel.

Attendu : Instagram prioritaire par les moyens. Le relais TikTok ne doit apparaître que si la capacité et les conditions de réutilisation sont réunies.

### Recrutement d’un jeune talent

Attendu : TikTok peut devenir prioritaire lorsque les observations le confirment et que la vidéo est maîtrisée.

### Aucun temps disponible

Attendu : la plateforme stratégique reste identifiée ; faisabilité `Lancement à reporter` ; aucune plateforme complémentaire.

## 4. Recherche externe

### Clé absente

Attendu : statut `indisponible`, diagnostic terminé avec le référentiel interne, aucun effet sur le classement.

### Couverture complète

Attendu : quatre plateformes couvertes par des sources qualifiées ; statut `complet` ; sources visibles dans le PDF.

### Une plateforme en erreur

Attendu : statut `partiel`, aucun effet sur le classement.

### Résultats sans source qualifiée

Attendu : statut `insuffisant`, aucun effet sur le classement.

### Source officielle hors sujet

Attendu : source rejetée si elle ne présente ni concordance suffisante ni score de pertinence élevé.

## 5. PDF

Contrôler visuellement :

- la plateforme prioritaire ;
- le complément éventuel ;
- les motifs de choix ;
- les alternatives ;
- les sources et leur qualification ;
- la faisabilité avec statut textuel ;
- les actions ;
- les acteurs ;
- les sauts de page et les textes longs.

## 6. Critère de gel

La V14 peut être figée uniquement lorsque :

- tous les tests automatiques réussissent ;
- le workflow GitHub est vert ;
- la recette navigateur est terminée ;
- une recherche réelle complète et un repli sans clé ont été testés ;
- les quatre guides et le calendrier se téléchargent ;
- aucune incohérence n’est constatée entre écran, PDF, matrice et fiche unique.

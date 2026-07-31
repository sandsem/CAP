import unittest

from scoring import (
    compare_platforms,
    evaluate,
    required_skills_for_formats,
    strategic_control,
)


def base_answers():
    return {
        "q1": "Oui",
        "q2": ["Profession libérale / Freelance"],
        "q2_coherence": "Oui",
        "q3": "Oui",
        "priority_need": "Structurer et développer son activité",
        "q4": ["Instagram", "TikTok"],
        "q4_modes_by_network": {
            "Instagram": "Découverte visuelle en suivant des comptes",
            "TikTok": "Recommandation de contenus selon les centres d’intérêt",
        },
        "q5": ["Expérience terrain", "Étude sectorielle"],
        "q5_quality": "Récentes et fiables",
        "q6": "Acquisition",
        "indicator": "Prises de contact qualifiées",
        "target": "2",
        "deadline": "3 mois",
        "q7": {
            "Facebook": "Aucun résultat identifié",
            "Instagram": "Contacts obtenus",
            "TikTok": "Aucun résultat identifié",
            "YouTube": "Aucun résultat identifié",
        },
        "q8": "6 à 10 h",
        "q14": ["Carrousel", "Reel"],
        "q9": {
            "Rédaction / script": "Autonome",
            "Création de visuels": "Autonome",
            "Montage vidéo": "Autonome",
        },
        "q10": [
            "Smartphone récent",
            "Ordinateur",
            "Connexion stable",
            "Micro",
        ],
        "q11": "Expert-comptable",
        "q12": [],
        "q13": "Aucune dépense nécessaire",
        "q15": None,
        "q16": "Non",
    }


class StrategicTests(unittest.TestCase):
    def test_instagram_recommended_from_observed_usage(self):
        result = evaluate(base_answers())
        self.assertEqual(result["winner"], "Instagram")
        self.assertEqual(result["strategic_status"], "Choix validé")
        self.assertNotIn("scores", result)
        self.assertNotIn("guide", result)

    def test_generic_profile_does_not_score_platforms(self):
        answers = base_answers()
        answers["q2"] = ["Artisan / commerçant / restaurateur"]
        result = evaluate(answers)
        self.assertEqual(result["winner"], "Instagram")

    def test_treatment_and_effect_do_not_influence_the_engine(self):
        answers = base_answers()
        answers["q6_treatment"] = "Expliquer et approfondir un sujet"
        answers["q6_effect"] = "Démontrer l’expertise"
        result = evaluate(answers)
        self.assertEqual(result["winner"], "Instagram")
        self.assertNotIn("traitement", result["selection_reasons"][0].lower())
        self.assertNotIn("effet", result["selection_reasons"][0].lower())

    def test_target_network_is_an_eligibility_filter(self):
        answers = base_answers()
        answers["q4"] = ["TikTok"]
        answers["q4_modes_by_network"] = {
            "TikTok": "Recommandation de contenus selon les centres d’intérêt"
        }
        result = evaluate(answers)
        self.assertEqual(result["winner"], "TikTok")

    def test_youtube_matches_search_and_expertise(self):
        answers = base_answers()
        answers["q4"] = ["YouTube"]
        answers["q4_modes_by_network"] = {
            "YouTube": "Recherche volontaire d’une réponse"
        }
        answers["q6"] = "Expertise / conseil"
        answers["q14"] = ["Vidéo longue"]
        result = evaluate(answers)
        self.assertEqual(result["winner"], "YouTube")

    def test_facebook_matches_community_and_proximity(self):
        answers = base_answers()
        answers["q4"] = ["Facebook"]
        answers["q4_modes_by_network"] = {
            "Facebook": "Échanges dans une communauté ou un groupe local"
        }
        answers["q6"] = "Fidélisation"
        answers["q14"] = ["Publication texte"]
        result = evaluate(answers)
        self.assertEqual(result["winner"], "Facebook")

    def test_usage_is_checked_for_each_network(self):
        answers = base_answers()
        answers["q7"]["Instagram"] = "Aucun résultat identifié"
        answers["q7"]["TikTok"] = "Aucun résultat identifié"
        answers["q4_modes_by_network"]["TikTok"] = (
            "Découverte visuelle en suivant des comptes"
        )
        selection = compare_platforms(answers)
        self.assertEqual(selection["winner"], "Instagram")
        self.assertEqual(selection["compatible_platforms"], ["Instagram"])

    def test_platform_with_no_valid_match_is_never_recommended(self):
        answers = base_answers()
        answers["q4"] = ["Facebook"]
        answers["q4_modes_by_network"] = {
            "Facebook": "Recherche volontaire d’une réponse"
        }
        answers["q6"] = "Recrutement"
        selection = compare_platforms(answers)
        self.assertIsNone(selection["winner"])
        self.assertEqual(selection["outcome"], "no_compatible_platform")
        self.assertEqual(selection["compatible_platforms"], [])

    def test_objective_and_usage_are_both_mandatory(self):
        answers = base_answers()
        answers["q4"] = ["YouTube"]
        answers["q4_modes_by_network"] = {
            "YouTube": "Recherche volontaire d’une réponse"
        }
        answers["q6"] = "Fidélisation"
        selection = compare_platforms(answers)
        self.assertIsNone(selection["winner"])
        self.assertFalse(selection["comparison"]["YouTube"]["objective_match"])
        self.assertTrue(selection["comparison"]["YouTube"]["usage_match"])

    def test_results_are_not_ranked_against_each_other(self):
        answers = self._tie_answers()
        answers["q7"]["Instagram"] = "Audience cible engagée"
        answers["q7"]["TikTok"] = "Contacts obtenus"
        selection = compare_platforms(answers)
        self.assertIsNone(selection["winner"])
        self.assertEqual(
            set(selection["tied_platforms"]),
            {"Instagram", "TikTok"},
        )

    def _tie_answers(self):
        answers = base_answers()
        answers["q7"]["Instagram"] = "Aucun résultat identifié"
        answers["q7"]["TikTok"] = "Aucun résultat identifié"
        return answers

    def test_results_already_obtained_break_tie_first(self):
        answers = self._tie_answers()
        answers["q7"]["Instagram"] = "Contacts obtenus"
        answers["q7"]["TikTok"] = "Aucun résultat identifié"
        selection = compare_platforms(answers)
        self.assertEqual(selection["winner"], "Instagram")
        self.assertEqual(
            selection["tie_break"],
            "résultat déjà obtenu auprès de ce persona",
        )

    def test_active_account_never_breaks_tie(self):
        answers = self._tie_answers()
        answers["q7"]["Instagram"] = "Compte actif"
        selection = compare_platforms(answers)
        self.assertIsNone(selection["winner"])
        self.assertEqual(selection["tie_break"], "égalité reconnue")
        self.assertEqual(
            set(selection["tied_platforms"]),
            {"Instagram", "TikTok"},
        )

    def test_equality_is_not_forced(self):
        answers = self._tie_answers()
        selection = compare_platforms(answers)
        self.assertIsNone(selection["winner"])
        self.assertEqual(set(selection["tied_platforms"]), {"Instagram", "TikTok"})

    def test_observation_choice_does_not_become_false_recommendation(self):
        answers = self._tie_answers()
        answers["q15"] = "TikTok"
        answers["q14"] = ["Vidéo"]
        result = evaluate(answers)
        self.assertIsNone(result["winner"])
        self.assertEqual(result["observation_platform"], "TikTok")
        self.assertEqual(result["platform_for_launch"], "TikTok")

    def test_missing_source_blocks_recommendation(self):
        answers = base_answers()
        answers["q5"] = ["Aucune source"]
        result = evaluate(answers)
        self.assertEqual(result["strategic_status"], "Recommandation impossible")
        self.assertIsNone(result["winner"])

    def test_one_reliable_source_is_sufficient(self):
        answers = base_answers()
        answers["q5"] = ["Expérience terrain"]
        result = evaluate(answers)
        self.assertEqual(result["strategic_status"], "Choix validé")
        self.assertEqual(result["winner"], "Instagram")

    def test_partially_verified_information_requires_review(self):
        answers = base_answers()
        answers["q5_quality"] = "Partiellement vérifiées"
        result = evaluate(answers)
        self.assertEqual(result["strategic_status"], "Projet à revoir")
        self.assertIsNone(result["winner"])
        self.assertIsNone(result["platform_for_launch"])

    def test_old_information_blocks_recommendation(self):
        answers = base_answers()
        answers["q5_quality"] = "Anciennes ou non vérifiées"
        control = strategic_control(answers)
        self.assertEqual(control["status"], "Recommandation impossible")

    def test_multiple_personas_require_separate_diagnostics(self):
        answers = base_answers()
        answers["q2"] = ["Start-up", "Profession libérale / Freelance"]
        control = strategic_control(answers)
        self.assertEqual(control["status"], "Recommandation impossible")
        self.assertTrue(
            any("un seul persona" in note for note in control["blocking"])
        )

    def test_each_selected_network_requires_an_observed_usage(self):
        answers = base_answers()
        del answers["q4_modes_by_network"]["TikTok"]
        control = strategic_control(answers)
        self.assertEqual(control["status"], "Recommandation impossible")
        self.assertTrue(any("TikTok" in note for note in control["blocking"]))

    def test_target_must_be_numeric(self):
        answers = base_answers()
        answers["target"] = "beaucoup"
        control = strategic_control(answers)
        self.assertEqual(control["status"], "Recommandation impossible")
        self.assertIn(
            "Indiquer un résultat attendu chiffré.",
            control["blocking"],
        )

    def test_deadline_must_be_precise(self):
        answers = base_answers()
        answers["deadline"] = "dès que possible"
        control = strategic_control(answers)
        self.assertEqual(control["status"], "Recommandation impossible")
        self.assertIn("Indiquer une échéance précise.", control["blocking"])


class FeasibilityTests(unittest.TestCase):
    def test_formats_trigger_only_needed_skills(self):
        self.assertEqual(
            required_skills_for_formats(["Carrousel"]),
            {"Rédaction / script", "Création de visuels"},
        )
        self.assertEqual(
            required_skills_for_formats(["Reel"]),
            {"Rédaction / script", "Montage vidéo"},
        )
        self.assertEqual(
            required_skills_for_formats(["Reel"], appears_on_camera=True),
            {
                "Rédaction / script",
                "Montage vidéo",
                "Aisance face caméra",
            },
        )
        self.assertIn(
            "Aisance face caméra",
            required_skills_for_formats(["Live"]),
        )

    def test_recorded_video_without_on_camera_presence_does_not_require_it(self):
        answers = base_answers()
        answers["q14"] = ["Reel"]
        answers["q16"] = "Non"
        answers["q9"] = {
            "Rédaction / script": "Autonome",
            "Montage vidéo": "Autonome",
        }
        result = evaluate(answers)
        skill_row = next(
            row
            for row in result["feasibility_rows"]
            if row["criterion"] == "Formats et compétences"
        )
        self.assertEqual(skill_row["status"], "vert")

    def test_recorded_video_on_camera_requires_on_camera_skill(self):
        answers = base_answers()
        answers["q14"] = ["Reel"]
        answers["q16"] = "Oui"
        answers["q9"]["Aisance face caméra"] = "À acquérir"
        answers["q12"] = ["Solution à trouver"]
        result = evaluate(answers)
        skill_row = next(
            row
            for row in result["feasibility_rows"]
            if row["criterion"] == "Formats et compétences"
        )
        self.assertEqual(skill_row["status"], "rouge")
        self.assertIn("Aisance face caméra", skill_row["observation"])

    def test_all_green_means_project_ready(self):
        result = evaluate(base_answers())
        self.assertEqual(result["feasibility_label"], "Projet prêt")
        self.assertTrue(
            all(row["status"] == "vert" for row in result["feasibility_rows"])
        )

    def test_orange_requires_preparation(self):
        answers = base_answers()
        answers["q8"] = "Moins de 2 h"
        result = evaluate(answers)
        self.assertEqual(result["winner"], "Instagram")
        self.assertEqual(result["feasibility_label"], "Lancement à préparer")

    def test_one_red_postpones_launch_without_changing_platform(self):
        answers = base_answers()
        answers["q9"]["Montage vidéo"] = "À acquérir"
        answers["q12"] = ["Solution à trouver"]
        result = evaluate(answers)
        self.assertEqual(result["winner"], "Instagram")
        self.assertEqual(result["feasibility_label"], "Lancement à reporter")
        self.assertTrue(
            any(row["status"] == "rouge" for row in result["feasibility_rows"])
        )
        skill_row = next(
            row
            for row in result["feasibility_rows"]
            if row["criterion"] == "Formats et compétences"
        )
        self.assertIn("Montage vidéo", skill_row["observation"])

    def test_concrete_training_solution_turns_missing_skill_orange(self):
        answers = base_answers()
        answers["q9"]["Montage vidéo"] = "À acquérir"
        answers["q12"] = ["Formation"]
        result = evaluate(answers)
        skill_row = next(
            row
            for row in result["feasibility_rows"]
            if row["criterion"] == "Formats et compétences"
        )
        self.assertEqual(skill_row["status"], "orange")
        self.assertEqual(result["feasibility_label"], "Lancement à préparer")

    def test_unfunded_essential_expense_postpones_launch(self):
        answers = base_answers()
        answers["q13"] = "Non"
        result = evaluate(answers)
        budget_row = next(
            row
            for row in result["feasibility_rows"]
            if row["criterion"] == "Budget"
        )
        self.assertEqual(budget_row["status"], "rouge")
        self.assertEqual(result["feasibility_label"], "Lancement à reporter")


if __name__ == "__main__":
    unittest.main()

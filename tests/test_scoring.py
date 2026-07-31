import unittest

from config import OUT_OF_SCOPE_NETWORK
from scoring import compare_platforms, evaluate, required_skills_for_formats, strategic_control


def base_answers():
    return {
        "q1": "Oui",
        "q2": ["Profession libérale / Freelance"],
        "custom_profile": "",
        "priority_need": "Choisir le statut juridique adapté à son activité",
        "q4": ["Instagram", "TikTok"],
        "q4_priority": "Instagram",
        "q5": ["Entretiens", "Données clients"],
        "q5_quality": "Oui",
        "q6": "Acquisition",
        "custom_objective": "",
        "indicator": "Demandes de contact",
        "target": "10",
        "deadline": "8 mois",
        "q8": "6 à 10 h",
        "q14": ["Carrousel"],
        "q16": "Non",
        "q9": {
            "Rédaction / script": "Autonome",
            "Création de visuels": "Autonome",
        },
        "q10": ["Smartphone récent", "Ordinateur", "Connexion internet stable"],
        "q11": ["L’expert-comptable"],
        "q12": [],
        "q12_confirmed": {},
        "q13_has_cost": "Non",
        "q13_budget_validated": "Sans objet",
        "q15": None,
    }


class StrategicTests(unittest.TestCase):
    def test_known_preferred_network_wins(self):
        result = evaluate(base_answers())
        self.assertEqual(result["winner"], "Instagram")
        self.assertEqual(result["tie_break"], "réseau le plus souvent utilisé par le persona")

    def test_single_observed_network_is_never_removed_by_objective(self):
        answers = base_answers()
        answers.update({"q4": ["TikTok"], "q4_priority": "TikTok", "q6": "Expertise et conseil"})
        self.assertEqual(compare_platforms(answers)["winner"], "TikTok")

    def test_unknown_network_uses_persona_reference(self):
        answers = base_answers()
        answers.update({
            "q4": ["Je ne sais pas"], "q4_priority": "Je ne sais pas",
            "q5": [], "q5_quality": None, "q6": "Expertise et conseil",
        })
        selection = compare_platforms(answers)
        self.assertEqual(selection["winner"], "YouTube")
        self.assertEqual(selection["candidate_basis"], "base de référence du persona")

    def test_acquisition_does_not_artificially_exclude_a_platform(self):
        answers = base_answers()
        answers.update({"q4": ["Facebook", "YouTube"], "q4_priority": "Je ne sais pas"})
        selection = compare_platforms(answers)
        self.assertEqual(set(selection["tied_platforms"]), {"Facebook", "YouTube"})

    def test_results_and_account_status_are_ignored(self):
        answers = base_answers()
        answers["q7"] = {"TikTok": "Contacts obtenus", "Instagram": "Aucun résultat"}
        self.assertEqual(compare_platforms(answers)["winner"], "Instagram")

    def test_per_platform_usage_is_ignored(self):
        answers = base_answers()
        answers["q4_modes_by_network"] = {"Instagram": "Recherche", "TikTok": "Recherche"}
        self.assertEqual(compare_platforms(answers)["winner"], "Instagram")

    def test_missing_source_blocks_known_network(self):
        answers = base_answers()
        answers["q5"] = ["Aucune source"]
        self.assertEqual(strategic_control(answers)["status"], "Recommandation impossible")

    def test_unknown_network_does_not_require_user_source(self):
        answers = base_answers()
        answers.update({"q4": ["Je ne sais pas"], "q4_priority": "Je ne sais pas", "q5": [], "q5_quality": None})
        self.assertEqual(strategic_control(answers)["status"], "Choix validé")

    def test_unreliable_network_information_blocks(self):
        answers = base_answers()
        answers["q5_quality"] = "Non"
        self.assertEqual(strategic_control(answers)["status"], "Recommandation impossible")

    def test_non_defined_objective_blocks(self):
        answers = base_answers()
        answers["q6"] = "Non défini"
        self.assertEqual(strategic_control(answers)["status"], "Recommandation impossible")

    def test_indicator_must_match_the_objective(self):
        answers = base_answers()
        answers["indicator"] = "Candidatures reçues"
        control = strategic_control(answers)
        self.assertEqual(control["status"], "Recommandation impossible")
        self.assertIn("indicateur directement lié", " ".join(control["blocking"]))

    def test_custom_objective_is_allowed_when_described(self):
        answers = base_answers()
        answers.update({"q6": "Autre", "custom_objective": "Développer les partenariats locaux"})
        self.assertEqual(strategic_control(answers)["status"], "Choix validé")

    def test_one_diagnostic_cannot_mix_personas(self):
        answers = base_answers()
        answers["q2"] = ["Start-up", "Micro-entrepreneur"]
        self.assertEqual(strategic_control(answers)["status"], "Recommandation impossible")

    def test_out_of_scope_network_blocks(self):
        answers = base_answers()
        answers.update({"q4": [OUT_OF_SCOPE_NETWORK], "q5": [], "q5_quality": None})
        self.assertEqual(strategic_control(answers)["status"], "Recommandation impossible")

    def test_special_network_answers_are_exclusive(self):
        answers = base_answers()
        answers["q4"] = ["TikTok", "Je ne sais pas"]
        self.assertEqual(strategic_control(answers)["status"], "Recommandation impossible")

    def test_perfect_tie_is_reported_not_forced(self):
        answers = base_answers()
        answers.update({
            "q2": ["Créateur d’entreprise"],
            "q4": ["Je ne sais pas"], "q4_priority": "Je ne sais pas",
            "q5": [], "q5_quality": None, "q6": "Acquisition",
        })
        result = evaluate(answers)
        self.assertIsNone(result["winner"])
        self.assertEqual(set(result["recommended_platforms"]), {"Instagram", "TikTok"})

    def test_cabinet_choice_is_separate_from_cap_recommendation(self):
        answers = base_answers()
        answers.update({
            "q2": ["Créateur d’entreprise"],
            "q4": ["Je ne sais pas"], "q4_priority": "Je ne sais pas",
            "q5": [], "q5_quality": None, "q6": "Acquisition", "q15": "TikTok",
        })
        result = evaluate(answers)
        self.assertEqual(set(result["recommended_platforms"]), {"Instagram", "TikTok"})
        self.assertEqual(result["retained_platform"], "TikTok")

    def test_single_recommendation_is_not_presented_as_cabinet_choice(self):
        result = evaluate(base_answers())
        self.assertEqual(result["winner"], "Instagram")
        self.assertIsNone(result["retained_platform"])


class FeasibilityTests(unittest.TestCase):
    def _row(self, result, criterion):
        return next(row for row in result["feasibility_rows"] if row["criterion"] == criterion)

    def test_required_skills_are_format_specific(self):
        self.assertEqual(required_skills_for_formats(["Carrousel"]), {"Rédaction / script", "Création de visuels"})
        self.assertEqual(required_skills_for_formats(["Vidéo courte"]), {"Rédaction / script", "Montage vidéo"})

    def test_on_camera_video_adds_camera_skill(self):
        self.assertIn("Aisance face caméra", required_skills_for_formats(["Vidéo courte"], True))

    def test_missing_skill_with_confirmed_training_is_orange(self):
        answers = base_answers()
        answers["q9"]["Création de visuels"] = "À acquérir"
        answers.update({"q12": ["Formation"], "q12_confirmed": {"Formation": "Oui"}})
        result = evaluate(answers)
        self.assertEqual(self._row(result, "Formats et compétences")["status"], "orange")

    def test_missing_skill_without_solution_is_red_but_keeps_platform(self):
        answers = base_answers()
        answers["q9"]["Création de visuels"] = "À acquérir"
        result = evaluate(answers)
        self.assertEqual(result["winner"], "Instagram")
        self.assertEqual(self._row(result, "Formats et compétences")["status"], "rouge")

    def test_no_time_postpones_without_changing_platform(self):
        answers = base_answers()
        answers["q8"] = "Aucun temps disponible"
        result = evaluate(answers)
        self.assertEqual(result["winner"], "Instagram")
        self.assertEqual(result["feasibility_label"], "Lancement à reporter")

    def test_smartphone_is_enough_for_visual_content(self):
        answers = base_answers()
        answers["q10"] = ["Smartphone récent", "Connexion internet stable"]
        self.assertEqual(self._row(evaluate(answers), "Matériel")["status"], "vert")

    def test_ring_light_and_camera_are_not_mandatory(self):
        answers = base_answers()
        answers["q10"] = ["Smartphone récent", "Connexion internet stable"]
        material = self._row(evaluate(answers), "Matériel")
        self.assertNotIn("Ring light", material["observation"])
        self.assertNotIn("Caméra", material["observation"])

    def test_unvalidated_budget_is_red(self):
        answers = base_answers()
        answers.update({"q13_has_cost": "Oui", "q13_budget_validated": "Non"})
        self.assertEqual(self._row(evaluate(answers), "Budget")["status"], "rouge")

    def test_no_responsible_person_is_red(self):
        answers = base_answers()
        answers["q11"] = ["Personne n’est encore désignée"]
        self.assertEqual(self._row(evaluate(answers), "Responsable")["status"], "rouge")

    def test_several_responsible_people_are_allowed(self):
        answers = base_answers()
        answers["q11"] = ["L’expert-comptable", "Un collaborateur désigné"]
        responsible = self._row(evaluate(answers), "Responsable")
        self.assertEqual(responsible["status"], "vert")
        self.assertIn("Un collaborateur désigné", responsible["observation"])

    def test_another_responsible_person_is_used_when_specified(self):
        answers = base_answers()
        answers.update({"q11": ["Autre"], "custom_pilot": "La secrétaire du cabinet"})
        responsible = self._row(evaluate(answers), "Responsable")
        self.assertEqual(responsible["status"], "vert")
        self.assertIn("La secrétaire du cabinet", responsible["observation"])


if __name__ == "__main__":
    unittest.main()

import unittest

from config import OUT_OF_SCOPE_NETWORK, PLATFORM_NAMES
from scoring import (
    classify_need,
    compare_platforms,
    evaluate,
    required_skills_for_formats,
    strategic_control,
)


def base_answers():
    return {
        "q1": "Oui",
        "q2": ["Profession libérale / Freelance"],
        "custom_profile": "",
        "priority_need": "Choisir le statut juridique adapté à son activité",
        "target_age_range": "35 à 44 ans",
        "cabinet_name": "Cabinet Test",
        "q4": ["Instagram", "TikTok"],
        "q4_priority": "Instagram",
        "q5": ["Entretiens", "Données clients"],
        "q5_quality": "Oui",
        "custom_source_details": "",
        "q6": "Acquisition",
        "custom_objective": "",
        "indicator": "Demandes de contact",
        "target": "10",
        "deadline": "8 mois",
        "q8": "6 à 10 h",
        "q14": ["Photo", "Carrousel"],
        "q16": "Non",
        "q9": {
            "Rédaction / script": "Autonome",
            "Création de visuels": "Autonome",
        },
        "q9_operational": {},
        "q10": ["Smartphone récent", "Ordinateur", "Connexion internet stable"],
        "q11": ["L’expert-comptable"],
        "q12": [],
        "q12_confirmed": {},
        "q12_by_skill": {},
        "q13_has_cost": "Non",
        "q13_budget_validated": "Sans objet",
        "q15": None,
    }


def fake_research(signals=None):
    signals = signals or {}
    return {
        "status": "complet",
        "can_influence": True,
        "searched_at": "03/08/2026 00:30",
        "note": "Signal documentaire public.",
        "sources": [],
        "platforms": {
            platform: {
                "signal": signals.get(platform, "faible"),
                "result_count": 1 if signals.get(platform) else 0,
                "sources": [],
            }
            for platform in PLATFORM_NAMES
        },
    }


class StrategicTests(unittest.TestCase):
    def test_need_is_interpreted(self):
        analysis = classify_need("Passer du statut de micro-entrepreneur à une société")
        self.assertEqual(analysis["category"], "explication approfondie")
        self.assertEqual(analysis["platforms"][0], "YouTube")

    def test_observed_network_is_evidence_not_automatic_winner(self):
        answers = base_answers()
        answers.update({
            "q2": ["Micro-entrepreneur"],
            "priority_need": "Passer du statut de micro-entrepreneur à une société",
            "q4": ["Instagram"],
            "q4_priority": "Instagram",
            "q5": ["Entretiens"],
            "q6": "Expertise et conseil",
            "indicator": "Enregistrements ou partages des contenus",
        })
        result = evaluate(answers)
        self.assertEqual(result["winner"], "YouTube")

    def test_clear_strategic_winner_remains_despite_missing_video(self):
        answers = base_answers()
        answers.update({
            "q2": ["Micro-entrepreneur"],
            "priority_need": "Passer du statut de micro-entrepreneur à une société",
            "q4": ["Instagram"],
            "q4_priority": "Instagram",
            "q5": ["Entretiens"],
            "q6": "Expertise et conseil",
            "indicator": "Enregistrements ou partages des contenus",
            "q14": ["Carrousel"],
        })
        result = evaluate(answers)
        self.assertEqual(result["winner"], "YouTube")
        self.assertEqual(result["feasibility_label"], "Lancement à préparer")
        self.assertIn("Se former", " ".join(result["launch_actions"]))

    def test_means_break_close_instagram_tiktok_choice(self):
        answers = base_answers()
        answers.update({
            "q2": ["Start-up"],
            "priority_need": "Faire connaître le cabinet auprès de nouveaux entrepreneurs",
            "q4": ["Instagram", "TikTok"],
            "q4_priority": "Je ne sais pas",
            "q6": "Visibilité et notoriété",
            "indicator": "Portée des publications",
            "q14": ["Photo", "Carrousel"],
        })
        result = evaluate(answers)
        self.assertEqual(result["winner"], "Instagram")
        self.assertEqual(result["tie_break"], "moyens du cabinet")

    def test_external_research_breaks_equal_readiness(self):
        answers = base_answers()
        answers.update({
            "q2": ["Start-up"],
            "priority_need": "Faire connaître le cabinet auprès de nouveaux entrepreneurs",
            "q4": ["Je ne sais pas"],
            "q4_priority": "Je ne sais pas",
            "q5": [],
            "q5_quality": None,
            "q6": "Visibilité et notoriété",
            "indicator": "Portée des publications",
            "q14": ["Carrousel", "Vidéo courte"],
            "q9": {
                "Rédaction / script": "Autonome",
                "Création de visuels": "Autonome",
                "Montage vidéo": "Autonome",
            },
        })
        result = evaluate(answers, fake_research({"TikTok": "fort", "Instagram": "faible"}))
        self.assertEqual(result["winner"], "TikTok")
        self.assertEqual(result["tie_break"], "recherche externe")


    def test_preferred_observed_network_is_used_when_platforms_are_otherwise_close(self):
        answers = base_answers()
        answers.update({
            "q2": ["Start-up"],
            "priority_need": "Faire connaître le cabinet auprès de nouveaux entrepreneurs",
            "q4": ["Instagram", "TikTok"],
            "q4_priority": "TikTok",
            "q6": "Visibilité et notoriété",
            "indicator": "Portée des publications",
            "q14": ["Carrousel", "Vidéo courte"],
            "q9": {
                "Rédaction / script": "Autonome",
                "Création de visuels": "Autonome",
                "Montage vidéo": "Autonome",
            },
        })
        result = evaluate(answers)
        self.assertEqual(result["winner"], "TikTok")
        self.assertEqual(result["tie_break"], "données de cible")

    def test_mixed_need_does_not_use_keyword_order_as_hidden_tie_break(self):
        analysis = classify_need("Recruter et gagner en visibilité")
        self.assertEqual(analysis["category"], "général")
        self.assertGreaterEqual(len(analysis["matched_categories"]), 2)

    def test_single_observed_network_is_treated_as_preferred_even_without_stale_field(self):
        answers = base_answers()
        answers.update({
            "q2": ["Start-up"],
            "priority_need": "Faire connaître le cabinet auprès de nouveaux entrepreneurs",
            "q4": ["TikTok"],
            "q4_priority": None,
            "q5": ["Entretiens"],
            "q6": "Visibilité et notoriété",
            "indicator": "Portée des publications",
            "q14": ["Carrousel", "Vidéo courte"],
            "q9": {
                "Rédaction / script": "Autonome",
                "Création de visuels": "Autonome",
                "Montage vidéo": "Autonome",
            },
        })
        result = evaluate(answers)
        self.assertEqual(result["winner"], "TikTok")

    def test_cap_always_returns_one_primary_platform(self):
        answers = base_answers()
        answers.update({
            "q2": ["Créateur d’entreprise"],
            "q4": ["Je ne sais pas"],
            "q4_priority": "Je ne sais pas",
            "q5": [],
            "q5_quality": None,
            "q6": "Acquisition",
        })
        result = evaluate(answers)
        self.assertIn(result["winner"], PLATFORM_NAMES)
        self.assertEqual(result["recommended_platforms"], [result["winner"]])
        self.assertIsNone(result["retained_platform"])

    def test_complement_is_not_automatic(self):
        answers = base_answers()
        answers["q8"] = "2 à 5 h"
        result = evaluate(answers)
        self.assertIsNone(result["complementary_platform"])

    def test_complement_requires_content_reuse_and_capacity(self):
        answers = base_answers()
        answers.update({
            "q2": ["Start-up"],
            "priority_need": "Faire connaître le cabinet auprès de nouveaux entrepreneurs",
            "q4": ["Instagram", "TikTok"],
            "q4_priority": "Je ne sais pas",
            "q6": "Visibilité et notoriété",
            "indicator": "Portée des publications",
            "q14": ["Carrousel", "Vidéo courte"],
            "q9": {
                "Rédaction / script": "Autonome",
                "Création de visuels": "Autonome",
                "Montage vidéo": "Autonome",
            },
            "q8": "6 à 10 h",
        })
        result = evaluate(answers, fake_research({"Instagram": "fort", "TikTok": "modéré"}))
        self.assertEqual(result["winner"], "Instagram")
        self.assertEqual(result["complementary_platform"], "TikTok")

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

    def test_zero_target_is_rejected(self):
        answers = base_answers()
        answers["target"] = "0"
        self.assertEqual(strategic_control(answers)["status"], "Recommandation impossible")

    def test_zero_deadline_is_rejected(self):
        answers = base_answers()
        answers["deadline"] = "0 mois"
        self.assertEqual(strategic_control(answers)["status"], "Recommandation impossible")


    def test_negative_target_is_rejected(self):
        answers = base_answers()
        answers["target"] = "-5"
        self.assertEqual(strategic_control(answers)["status"], "Recommandation impossible")

    def test_deadline_without_unit_is_rejected(self):
        answers = base_answers()
        answers["deadline"] = "2026"
        self.assertEqual(strategic_control(answers)["status"], "Recommandation impossible")

    def test_ambiguous_deadline_is_rejected(self):
        answers = base_answers()
        answers["deadline"] = "demain 2"
        self.assertEqual(strategic_control(answers)["status"], "Recommandation impossible")

    def test_sensitive_identifier_is_rejected(self):
        answers = base_answers()
        answers["priority_need"] = "Dossier client 123456 à analyser"
        self.assertEqual(strategic_control(answers)["status"], "Recommandation impossible")

    def test_other_source_requires_details(self):
        answers = base_answers()
        answers["q5"] = ["Autre source"]
        self.assertEqual(strategic_control(answers)["status"], "Recommandation impossible")
        answers["custom_source_details"] = "Étude sectorielle 2026"
        self.assertEqual(strategic_control(answers)["status"], "Choix validé")

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

    def test_sensitive_data_in_any_free_text_field_blocks(self):
        fields = [
            ("custom_objective", "Écrire à contact@example.com"),
            ("custom_source_details", "Dossier client 123456"),
            ("custom_pilot", "+33 6 12 34 56 78"),
            ("custom_indicator", "SIRET 12345678901234"),
        ]
        for field, value in fields:
            with self.subTest(field=field):
                answers = base_answers()
                answers[field] = value
                self.assertEqual(strategic_control(answers)["status"], "Recommandation impossible")

    def test_oversized_free_text_blocks(self):
        answers = base_answers()
        answers["priority_need"] = "x" * 241
        self.assertEqual(strategic_control(answers)["status"], "Recommandation impossible")


class FeasibilityTests(unittest.TestCase):
    def _row(self, result, criterion):
        return next(row for row in result["feasibility_rows"] if row["criterion"] == criterion)

    def test_required_skills_are_format_specific(self):
        self.assertEqual(required_skills_for_formats(["Carrousel"]), {"Rédaction / script", "Création de visuels"})
        self.assertEqual(required_skills_for_formats(["Vidéo courte"]), {"Rédaction / script", "Montage vidéo"})

    def test_on_camera_video_adds_camera_skill(self):
        self.assertIn("Aisance face caméra", required_skills_for_formats(["Vidéo courte"], True))

    def test_no_face_camera_does_not_prevent_video(self):
        answers = base_answers()
        answers.update({
            "q14": ["Vidéo courte", "Carrousel"],
            "q16": "Non",
            "q9": {
                "Rédaction / script": "Autonome",
                "Montage vidéo": "Autonome",
                "Création de visuels": "Autonome",
            },
        })
        result = evaluate(answers)
        self.assertNotIn("Aisance face caméra", self._row(result, "Formats et compétences")["observation"])

    def test_one_format_requires_preparation(self):
        answers = base_answers()
        answers["q14"] = ["Carrousel"]
        result = evaluate(answers)
        self.assertEqual(self._row(result, "Formats et compétences")["status"], "orange")
        self.assertIn("second format", self._row(result, "Formats et compétences")["action"])

    def test_missing_skill_with_confirmed_training_is_orange(self):
        answers = base_answers()
        answers["q9"]["Création de visuels"] = "À acquérir"
        answers["q12_by_skill"] = {
            "Création de visuels": {"solution": "Formation", "confirmed": "Oui"}
        }
        result = evaluate(answers)
        self.assertEqual(self._row(result, "Formats et compétences")["status"], "orange")

    def test_missing_skill_without_solution_is_red_but_keeps_clear_platform(self):
        answers = base_answers()
        answers.update({
            "q2": ["Start-up"],
            "priority_need": "Faire connaître le cabinet auprès de nouveaux entrepreneurs",
            "q4": ["Instagram"],
            "q4_priority": "Instagram",
            "q5": ["Entretiens"],
            "q6": "Visibilité et notoriété",
            "indicator": "Portée des publications",
        })
        answers["q9"]["Création de visuels"] = "À acquérir"
        result = evaluate(answers)
        self.assertEqual(result["winner"], "Instagram")
        self.assertEqual(self._row(result, "Formats et compétences")["status"], "rouge")

    def test_notions_operational_do_not_delay_launch(self):
        answers = base_answers()
        answers.update({
            "q2": ["Start-up"],
            "priority_need": "Faire connaître le cabinet auprès de nouveaux entrepreneurs",
            "q4": ["Instagram"],
            "q4_priority": "Instagram",
            "q5": ["Entretiens"],
            "q6": "Visibilité et notoriété",
            "indicator": "Portée des publications",
        })
        answers["q9"]["Création de visuels"] = "Notions"
        answers["q9_operational"] = {"Création de visuels": "Oui"}
        result = evaluate(answers)
        self.assertEqual(result["winner"], "Instagram")
        self.assertEqual(self._row(result, "Formats et compétences")["status"], "vert")

    def test_notions_not_operational_require_preparation(self):
        answers = base_answers()
        answers["q9"]["Création de visuels"] = "Notions"
        answers["q9_operational"] = {"Création de visuels": "Non"}
        result = evaluate(answers)
        self.assertEqual(self._row(result, "Formats et compétences")["status"], "orange")

    def test_no_time_postpones_without_changing_clear_platform(self):
        answers = base_answers()
        answers.update({
            "q2": ["Start-up"],
            "priority_need": "Faire connaître le cabinet auprès de nouveaux entrepreneurs",
            "q4": ["Instagram"],
            "q4_priority": "Instagram",
            "q5": ["Entretiens"],
            "q6": "Visibilité et notoriété",
            "indicator": "Portée des publications",
            "q8": "Aucun temps disponible",
        })
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

    def test_carrousel_can_be_created_with_computer_without_camera(self):
        answers = base_answers()
        answers.update({
            "q14": ["Carrousel", "Publication texte"],
            "q10": ["Ordinateur", "Connexion internet stable"],
            "q9": {
                "Rédaction / script": "Autonome",
                "Création de visuels": "Autonome",
            },
        })
        result = evaluate(answers)
        self.assertNotEqual(self._row(result, "Matériel")["status"], "rouge")

    def test_complement_is_not_proposed_until_primary_is_ready(self):
        answers = base_answers()
        answers.update({
            "q2": ["Start-up"],
            "priority_need": "Faire connaître le cabinet auprès de nouveaux entrepreneurs",
            "q4": ["Instagram", "TikTok"],
            "q4_priority": "Instagram",
            "q5": ["Entretiens"],
            "q6": "Visibilité et notoriété",
            "indicator": "Portée des publications",
            "q14": ["Photo"],
            "q8": "6 à 10 h",
        })
        result = evaluate(answers)
        self.assertEqual(result["feasibility_label"], "Lancement à préparer")
        self.assertIsNone(result["complementary_platform"])

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
        result = evaluate(answers)
        responsible = self._row(result, "Responsable")
        self.assertEqual(responsible["status"], "vert")
        self.assertIn("La secrétaire du cabinet", responsible["observation"])
        self.assertIn("La secrétaire du cabinet", result["actors"])


class PlainLanguageAndPriorityTests(unittest.TestCase):
    def test_reliable_observations_come_before_external_search_when_strategy_is_close(self):
        answers = base_answers()
        answers.update({
            "q2": ["Dirigeant TPE-PME"],
            "priority_need": "Atteindre un meilleur niveau de rémunération",
            "q4": ["TikTok", "YouTube"],
            "q4_priority": "Je ne sais pas",
            "q5": ["Statistiques", "Questionnaire", "Étude sectorielle"],
            "q5_quality": "Oui",
            "q6": "Acquisition",
            "indicator": "Rendez-vous obtenus",
            "q14": ["Publication texte", "Photo", "Vidéo courte", "Story"],
            "q9": {
                "Rédaction / script": "À acquérir",
                "Création de visuels": "Notions",
                "Montage vidéo": "Notions",
            },
        })
        result = evaluate(answers, fake_research({"Facebook": "fort", "TikTok": "modéré", "YouTube": "modéré"}))
        self.assertIn(result["winner"], {"TikTok", "YouTube"})
        self.assertNotEqual(result["winner"], "Facebook")

    def test_selection_reasons_do_not_expose_internal_vocabulary(self):
        result = evaluate(base_answers())
        text = " ".join(result["selection_reasons"] + list(result["non_priority_reasons"].values())).lower()
        for forbidden in ("règle stable", "référentiel du persona", "famille unique", "profondeur stratégique"):
            self.assertNotIn(forbidden, text)

    def test_remuneration_need_is_classified_as_detailed_explanation(self):
        analysis = classify_need("Atteindre un meilleur niveau de rémunération")
        self.assertEqual(analysis["category"], "explication approfondie")


if __name__ == "__main__":
    unittest.main()

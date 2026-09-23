from __future__ import annotations

import unittest

from src.v4.structure_editorial import SIMILARITY_THRESHOLD as V4_THRESHOLD
from tomelinea.rules import (
    SIMILARITY_THRESHOLD,
    DecisionScope,
    Situation,
    decide,
    group_cases,
    persistence_event,
    rule_from_decision,
)


class V5RuleEngineTests(unittest.TestCase):
    def test_similarity_threshold_reuses_validated_v4_value(self) -> None:
        self.assertEqual(SIMILARITY_THRESHOLD, V4_THRESHOLD)
        self.assertEqual(SIMILARITY_THRESHOLD, 0.88)

    def test_multiple_situations_on_same_object_form_one_case(self) -> None:
        situations = (
            Situation("text", "widow", "element-42", "page-8"),
            Situation("text", "hyphenation", "element-42", "page-8"),
            Situation("pagination", "page_right", "page-9", "page-9"),
        )
        cases = group_cases(situations)
        self.assertEqual(len(cases), 2)
        self.assertEqual(cases[0].subject_id, "element-42")
        self.assertEqual(
            [item.kind for item in cases[0].situations],
            ["widow", "hyphenation"],
        )

    def test_case_order_is_deterministic(self) -> None:
        cases = group_cases(
            (
                Situation("text", "a", "B"),
                Situation("text", "b", "A"),
                Situation("text", "c", "B"),
            )
        )
        self.assertEqual([item.subject_id for item in cases], ["B", "A"])
        self.assertEqual([item.kind for item in cases[0].situations], ["a", "c"])

    def test_decision_is_local_by_default(self) -> None:
        situation = Situation("text", "title_orphan", "title-7")
        case = group_cases([situation])[0]
        decision = decide(case, situation.id, "correct")
        self.assertEqual(decision.scope, DecisionScope.LOCAL)
        self.assertEqual(decision.similar_subject_ids, ())
        rule = rule_from_decision(case, decision)
        self.assertEqual(rule.member_subject_ids, ("title-7",))
        self.assertTrue(rule.applies_to(situation))

    def test_similarity_extension_must_be_explicit(self) -> None:
        situation = Situation("pagination", "page_right", "page-10")
        case = group_cases([situation])[0]

        with self.assertRaises(ValueError):
            decide(
                case,
                situation.id,
                "apply",
                similar_subject_ids=["page-20"],
            )

        decision = decide(
            case,
            situation.id,
            "apply",
            scope=DecisionScope.SIMILAR,
            similar_subject_ids=["page-20", "page-30", "page-20"],
        )
        self.assertEqual(decision.similar_subject_ids, ("page-20", "page-30"))
        rule = rule_from_decision(case, decision)
        self.assertEqual(rule.threshold, 0.88)
        self.assertEqual(
            rule.member_subject_ids,
            ("page-10", "page-20", "page-30"),
        )

    def test_rule_matches_only_explicit_domain_kind_and_members(self) -> None:
        anchor = Situation("text", "widow", "paragraph-1")
        case = group_cases([anchor])[0]
        decision = decide(
            case,
            anchor.id,
            "correct",
            scope=DecisionScope.SIMILAR,
            similar_subject_ids=["paragraph-2"],
        )
        rule = rule_from_decision(case, decision)

        self.assertTrue(rule.applies_to(Situation("text", "widow", "paragraph-2")))
        self.assertFalse(rule.applies_to(Situation("text", "widow", "paragraph-3")))
        self.assertFalse(rule.applies_to(Situation("text", "hyphenation", "paragraph-2")))
        self.assertFalse(rule.applies_to(Situation("pagination", "widow", "paragraph-2")))

    def test_decisions_are_sequential_inside_one_case(self) -> None:
        first = Situation("text", "widow", "paragraph-1")
        second = Situation("text", "hyphenation", "paragraph-1")
        case = group_cases([first, second])[0]

        first_rule = rule_from_decision(
            case,
            decide(case, first.id, "correct"),
        )
        second_rule = rule_from_decision(
            case,
            decide(case, second.id, "leave"),
        )

        self.assertEqual(first_rule.kind, "widow")
        self.assertEqual(second_rule.kind, "hyphenation")

    def test_persistence_event_keeps_existing_stable_id_contract(self) -> None:
        situation = Situation("text", "style_outlier", "element-stable-99")
        case = group_cases([situation])[0]
        decision = decide(case, situation.id, "correct")
        self.assertEqual(
            persistence_event(situation, decision),
            {
                "domain": "text",
                "stable_id": "element-stable-99",
                "choice": "correct",
            },
        )

    def test_engine_has_no_ai_or_probability_state(self) -> None:
        situation = Situation("text", "widow", "paragraph-1", facts={"line_count": 1})
        case = group_cases([situation])[0]
        decision = decide(case, situation.id, "correct")
        rule = rule_from_decision(case, decision)

        for obj in (situation, case, decision, rule):
            self.assertFalse(hasattr(obj, "model"))
            self.assertFalse(hasattr(obj, "confidence"))
            self.assertFalse(hasattr(obj, "probability"))
            self.assertFalse(hasattr(obj, "ai"))


if __name__ == "__main__":
    unittest.main()
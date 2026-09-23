from __future__ import annotations

import unittest

from src.v4 import text_anomalies as v4_text
from tomelinea.rules import Situation, group_cases
from tomelinea.text import (
    RECOMMENDED_TEXT_KINDS,
    TECHNICAL_TEXT_KINDS,
    TEXT_SITUATION_KINDS,
    TextSituationClass,
    analyze_book_text_anomalies,
    text_issue_to_situation,
    text_situation_class,
    text_situations_from_issues,
)


class V5TextSituationTests(unittest.TestCase):
    def test_detector_is_the_validated_v4_detector(self) -> None:
        self.assertIs(
            analyze_book_text_anomalies,
            v4_text.analyze_book_text_anomalies,
        )

    def test_catalog_contains_the_ten_validated_user_facing_kinds(self) -> None:
        expected = {
            "double_space",
            "space_before_punctuation",
            "missing_space_after_punctuation",
            "french_nonbreaking_space",
            "text_not_justified",
            "style_outlier",
            "hyphenation",
            "title_orphan",
            "orphan_line",
            "widow",
        }

        self.assertEqual(TEXT_SITUATION_KINDS, expected)
        self.assertEqual(len(TECHNICAL_TEXT_KINDS), 4)
        self.assertEqual(len(RECOMMENDED_TEXT_KINDS), 6)

    def test_technical_and_recommended_classes_are_explicit(self) -> None:
        self.assertEqual(
            text_situation_class("double_space"),
            TextSituationClass.TECHNICAL,
        )
        self.assertEqual(
            text_situation_class("widow"),
            TextSituationClass.RECOMMENDED,
        )
        self.assertEqual(
            text_situation_class("future_local_case"),
            TextSituationClass.LOCAL,
        )

    def test_issue_is_translated_without_confidence_score(self) -> None:
        issue = {
            "id": "page-1:element-1:double_space:line2",
            "type": "double_space",
            "kind": "double_space",
            "page_id": "page-1",
            "source_page": 3,
            "element_id": "element-1",
            "element_ids": ("element-1",),
            "title": "Il y a un espace en trop ici",
            "technical_term": "espace double",
            "why": "Deux espaces se suivent.",
            "proposal": "Ramener cet espacement à un seul espace.",
            "geometry": {
                "x_mm": 20,
                "y_mm": 30,
                "width_mm": 80,
                "height_mm": 5,
            },
            "confidence": 0.995,
            "engine": "tomelinea.text_anomalies",
            "engine_version": "2",
        }

        situation = text_issue_to_situation(issue)

        self.assertIsInstance(situation, Situation)
        self.assertEqual(situation.domain, "text")
        self.assertEqual(situation.kind, "double_space")
        self.assertEqual(situation.subject_id, "element-1")
        self.assertEqual(situation.page_id, "page-1")
        self.assertEqual(
            situation.qualifier,
            "page-1:element-1:double_space:line2",
        )
        self.assertEqual(
            situation.facts["classification"],
            "technical",
        )
        self.assertNotIn("confidence", situation.facts)
        self.assertFalse(hasattr(situation, "confidence"))

    def test_multiple_issues_same_element_become_one_case(self) -> None:
        issues = (
            {
                "id": "page-1:element-1:double_space:line1",
                "type": "double_space",
                "page_id": "page-1",
                "element_id": "element-1",
            },
            {
                "id": "page-1:element-1:hyphenation:line3",
                "type": "hyphenation",
                "page_id": "page-1",
                "element_id": "element-1",
            },
        )

        situations = text_situations_from_issues(issues)
        cases = group_cases(situations)

        self.assertEqual(len(situations), 2)
        self.assertEqual(len(cases), 1)
        self.assertEqual(cases[0].subject_id, "element-1")
        self.assertEqual(
            [item.kind for item in cases[0].situations],
            ["double_space", "hyphenation"],
        )

    def test_distinct_line_issues_keep_distinct_situation_ids(self) -> None:
        issues = (
            {
                "id": "page-1:element-1:double_space:line1",
                "type": "double_space",
                "page_id": "page-1",
                "element_id": "element-1",
            },
            {
                "id": "page-1:element-1:double_space:line4",
                "type": "double_space",
                "page_id": "page-1",
                "element_id": "element-1",
            },
        )

        situations = text_situations_from_issues(issues)

        self.assertNotEqual(
            situations[0].id,
            situations[1].id,
        )


if __name__ == "__main__":
    unittest.main()
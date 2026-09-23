from __future__ import annotations

from types import SimpleNamespace
import unittest

from src.v4 import text_engine as v4_text_engine
from tomelinea.rules import (
    DecisionScope,
    Situation,
    decide,
    group_cases,
)
from tomelinea.text import (
    TEXT_CHOICE_CORRECTED,
    TEXT_CHOICE_IGNORED,
    execute_text_decision,
    prepare_text_review,
    text_issue_from_situation,
)
import tomelinea.text.execution as execution


def make_situation(
    kind: str = "text_not_justified",
) -> Situation:
    return Situation(
        domain="text",
        kind=kind,
        subject_id="element-1",
        page_id="page-1",
        qualifier=f"page-1:element-1:{kind}",
        facts={
            "issue_id": f"page-1:element-1:{kind}",
            "title": "Probleme de texte",
            "technical_term": "terme",
            "why": "Raison",
            "proposal": "Proposition",
            "geometry": {
                "x_mm": 10.0,
                "y_mm": 20.0,
                "width_mm": 80.0,
                "height_mm": 10.0,
            },
            "element_ids": (
                "element-1",
            ),
            "source_engine": "tomelinea.text_anomalies",
            "source_engine_version": "2",
        },
    )


def fake_book():
    element = {
        "id": "element-1",
        "metadata": {},
    }
    page = SimpleNamespace(
        content=[element],
    )
    book = SimpleNamespace(
        metadata={},
        pages={
            "page-1": page,
        },
    )
    return book, element


class V5TextExecutionTests(unittest.TestCase):
    def test_execution_uses_validated_v4_functions(self) -> None:
        self.assertIs(
            execution.prepare_text,
            v4_text_engine.prepare_text,
        )
        self.assertIs(
            execution.correct_after_approval,
            v4_text_engine.correct_after_approval,
        )
        self.assertIs(
            execution.accept_specific_exception,
            v4_text_engine.accept_specific_exception,
        )

    def test_prepare_text_review_keeps_automatic_and_human_steps_separate(self) -> None:
        original = execution.prepare_text

        try:
            execution.prepare_text = lambda book: v4_text_engine.TextEngineReport(
                rules={
                    "alignment": "justify",
                },
                rules_created=True,
                automatic_corrections=(
                    {
                        "kind": "double_space",
                        "changed": True,
                    },
                ),
                issues=(
                    {
                        "id": "page-1:element-1:widow",
                        "type": "widow",
                        "page_id": "page-1",
                        "element_id": "element-1",
                    },
                ),
            )

            review = prepare_text_review(
                object(),
            )

            self.assertTrue(
                review.rules_created,
            )
            self.assertEqual(
                review.automatic_corrections[0]["kind"],
                "double_space",
            )
            self.assertEqual(
                len(review.situations),
                1,
            )
            self.assertEqual(
                review.situations[0].kind,
                "widow",
            )
        finally:
            execution.prepare_text = original

    def test_situation_rebuilds_minimal_v4_issue_contract(self) -> None:
        situation = make_situation(
            "hyphenation",
        )

        issue = text_issue_from_situation(
            situation,
        )

        self.assertEqual(
            issue["id"],
            "page-1:element-1:hyphenation",
        )
        self.assertEqual(
            issue["type"],
            "hyphenation",
        )
        self.assertEqual(
            issue["page_id"],
            "page-1",
        )
        self.assertEqual(
            issue["element_id"],
            "element-1",
        )
        self.assertEqual(
            issue["geometry"]["x_mm"],
            10.0,
        )

    def test_corrected_decision_delegates_and_records_v4_state(self) -> None:
        situation = make_situation()
        case = group_cases(
            [situation]
        )[0]
        decision = decide(
            case,
            situation.id,
            TEXT_CHOICE_CORRECTED,
        )

        book, _element = fake_book()

        original_supported = execution.correction_supported
        original_correct = execution.correct_after_approval
        calls = []

        try:
            execution.correction_supported = (
                lambda current_book, issue: True
            )

            def fake_correct(current_book, issue):
                calls.append(
                    dict(issue)
                )
                return {
                    "changed": True,
                    "kind": issue["type"],
                }

            execution.correct_after_approval = fake_correct

            result = execute_text_decision(
                book,
                situation,
                decision,
            )
        finally:
            execution.correction_supported = original_supported
            execution.correct_after_approval = original_correct

        self.assertEqual(
            len(calls),
            1,
        )
        self.assertTrue(
            result.changed,
        )
        self.assertEqual(
            result.choice,
            "corrected",
        )
        self.assertEqual(
            book.metadata["text_problem_decisions"][
                situation.qualifier
            ],
            "corrected",
        )
        self.assertTrue(
            book.metadata["text_reflow_requested"],
        )

    def test_ignored_decision_uses_real_v4_exception_engine(self) -> None:
        situation = make_situation(
            "text_not_justified",
        )
        case = group_cases(
            [situation]
        )[0]
        decision = decide(
            case,
            situation.id,
            TEXT_CHOICE_IGNORED,
        )

        book, element = fake_book()

        result = execute_text_decision(
            book,
            situation,
            decision,
        )

        self.assertFalse(
            result.changed,
        )
        self.assertEqual(
            result.exception_rule,
            "alignment",
        )
        self.assertEqual(
            book.metadata["text_problem_decisions"][
                situation.qualifier
            ],
            "ignored",
        )
        self.assertTrue(
            element["metadata"]["text_rule_exceptions"][
                "alignment"
            ],
        )

    def test_similar_scope_is_rejected_until_text_similarity_is_validated(self) -> None:
        situation = make_situation()
        case = group_cases(
            [situation]
        )[0]
        decision = decide(
            case,
            situation.id,
            TEXT_CHOICE_CORRECTED,
            scope=DecisionScope.SIMILAR,
            similar_subject_ids=(
                "element-2",
            ),
        )

        book, _element = fake_book()

        with self.assertRaises(
            ValueError,
        ):
            execute_text_decision(
                book,
                situation,
                decision,
            )

    def test_unknown_choice_is_rejected(self) -> None:
        situation = make_situation()
        case = group_cases(
            [situation]
        )[0]
        decision = decide(
            case,
            situation.id,
            "invented",
        )

        book, _element = fake_book()

        with self.assertRaises(
            ValueError,
        ):
            execute_text_decision(
                book,
                situation,
                decision,
            )

    def test_unsupported_correction_is_not_declared_corrected(self) -> None:
        situation = make_situation()
        case = group_cases(
            [situation]
        )[0]
        decision = decide(
            case,
            situation.id,
            TEXT_CHOICE_CORRECTED,
        )
        book, _element = fake_book()

        original_supported = execution.correction_supported

        try:
            execution.correction_supported = (
                lambda current_book, issue: False
            )

            with self.assertRaises(
                ValueError,
            ):
                execute_text_decision(
                    book,
                    situation,
                    decision,
                )
        finally:
            execution.correction_supported = original_supported

        self.assertNotIn(
            "text_problem_decisions",
            book.metadata,
        )


if __name__ == "__main__":
    unittest.main()
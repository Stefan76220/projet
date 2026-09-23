"""Catalogue et execution Texte publics de TomeLinea V5."""

from .api import (
    RECOMMENDED_TEXT_KINDS,
    TECHNICAL_TEXT_KINDS,
    TEXT_SITUATION_KINDS,
    TextSituationClass,
    analyze_book_text_anomalies,
    detect_text_situations,
    text_issue_to_situation,
    text_situation_class,
    text_situations_from_issues,
)
from .execution import (
    TEXT_CHOICE_CORRECTED,
    TEXT_CHOICE_IGNORED,
    TEXT_DECISION_CHOICES,
    TextDecisionExecution,
    TextReviewPreparation,
    execute_text_decision,
    prepare_text_review,
    text_issue_from_situation,
)

__all__ = [
    "TextSituationClass",
    "TECHNICAL_TEXT_KINDS",
    "RECOMMENDED_TEXT_KINDS",
    "TEXT_SITUATION_KINDS",
    "text_situation_class",
    "text_issue_to_situation",
    "text_situations_from_issues",
    "detect_text_situations",
    "analyze_book_text_anomalies",
    "TEXT_CHOICE_CORRECTED",
    "TEXT_CHOICE_IGNORED",
    "TEXT_DECISION_CHOICES",
    "TextReviewPreparation",
    "TextDecisionExecution",
    "prepare_text_review",
    "text_issue_from_situation",
    "execute_text_decision",
]
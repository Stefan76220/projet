"""Catalogue Texte public de TomeLinea V5."""

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
]
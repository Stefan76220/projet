"""Catalogue et execution Couvertures publics de TomeLinea V5."""

from .api import (
    COVER_SITUATION_KINDS,
    INSIDE_BACK_COVER,
    INSIDE_COVER_CONFIRMATION,
    INSIDE_FRONT_COVER,
    cover_issue_to_situation,
    cover_situations,
    inside_cover_confirmation_issues,
)
from .execution import (
    COVER_CHOICE_BLANK,
    COVER_CHOICE_CONTENT,
    COVER_DECISION_CHOICES,
    CoverDecisionExecution,
    execute_cover_decision,
)

__all__ = [
    "INSIDE_FRONT_COVER",
    "INSIDE_BACK_COVER",
    "INSIDE_COVER_CONFIRMATION",
    "COVER_SITUATION_KINDS",
    "inside_cover_confirmation_issues",
    "cover_issue_to_situation",
    "cover_situations",
    "COVER_CHOICE_CONTENT",
    "COVER_CHOICE_BLANK",
    "COVER_DECISION_CHOICES",
    "CoverDecisionExecution",
    "execute_cover_decision",
]
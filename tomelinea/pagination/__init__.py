"""Catalogue et execution Pagination publics de TomeLinea V5."""

from .api import (
    BLANK_AFTER,
    BLANK_BEFORE,
    CONSTRAINT_HELP,
    CONSTRAINT_LABELS,
    DOUBLE_PAGE,
    PAGINATION_CLASSES,
    PAGINATION_SITUATION_KINDS,
    PAGE_LEFT,
    PAGE_RIGHT,
    SIMILARITY_THRESHOLD,
    PaginationSituationClass,
    double_page_situation,
    pagination_situation,
    pagination_situation_class,
    similar_pagination_page_ids,
)
from .execution import (
    PAGINATION_CHOICE_DISABLED,
    PAGINATION_CHOICE_ENABLED,
    PAGINATION_DECISION_CHOICES,
    PaginationDecisionExecution,
    execute_pagination_decision,
)

__all__ = [
    "PAGE_RIGHT",
    "PAGE_LEFT",
    "BLANK_BEFORE",
    "BLANK_AFTER",
    "DOUBLE_PAGE",
    "CONSTRAINT_LABELS",
    "CONSTRAINT_HELP",
    "SIMILARITY_THRESHOLD",
    "PaginationSituationClass",
    "PAGINATION_SITUATION_KINDS",
    "PAGINATION_CLASSES",
    "pagination_situation_class",
    "pagination_situation",
    "double_page_situation",
    "similar_pagination_page_ids",
    "PAGINATION_CHOICE_ENABLED",
    "PAGINATION_CHOICE_DISABLED",
    "PAGINATION_DECISION_CHOICES",
    "PaginationDecisionExecution",
    "execute_pagination_decision",
]
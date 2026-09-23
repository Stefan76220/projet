"""Document logique commun de TomeLinea V5."""

from .api import (
    IntegrityReport,
    TLDocument,
    TLImage,
    TLParagraph,
    TLRun,
    TLSection,
    TLTable,
    TLDOCUMENT_SCHEMA,
    TLDOCUMENT_VERSION,
    build_tldocument_from_docx,
)

__all__ = [
    "TLDOCUMENT_SCHEMA",
    "TLDOCUMENT_VERSION",
    "TLRun",
    "TLParagraph",
    "TLTable",
    "TLImage",
    "TLSection",
    "TLDocument",
    "IntegrityReport",
    "build_tldocument_from_docx",
]

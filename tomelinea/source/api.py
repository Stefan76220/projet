"""API Source commune de TomeLinea V5.

V5-02 n'implemente pas un nouveau moteur Source.
Elle expose le moteur V4 gele derriere des noms V5 stables afin que
les nouveaux consommateurs ne dependent plus des noms historiques *V4.
"""

from src.v4.source import (
    SourceElement,
    SourceV4 as Source,
    SourceVersion,
    file_sha256,
)

__all__ = [
    "Source",
    "SourceElement",
    "SourceVersion",
    "file_sha256",
]
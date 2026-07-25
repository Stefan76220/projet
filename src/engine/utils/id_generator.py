from __future__ import annotations

from itertools import count


class IdGenerator:
    """
    Générateur d'identifiants uniques.
    """

    _counter = count(1)

    @classmethod
    def next(cls) -> int:
        return next(cls._counter)
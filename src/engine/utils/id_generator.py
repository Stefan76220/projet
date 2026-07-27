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

    @classmethod
    def reset(
        cls,
        start: int = 1,
    ) -> None:

        cls._counter = count(start)
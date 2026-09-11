from __future__ import annotations

"""
TomeLinea V4 — comparaison déterministe des pages Source.

Ce moteur travaille uniquement à partir des faits déjà extraits.
Il n'utilise aucune IA et ne décide pas du rôle éditorial d'une page.

Il cherche notamment :
- des pages très proches pouvant partager un modèle ;
- des variantes appartenant à une même famille ;
- des groupes de pages structurellement apparentés.
"""

from dataclasses import dataclass
from difflib import SequenceMatcher
import re
from typing import Any

from src.v4.analysis import AnalysisV4
from src.v4.source import SourceVersion


FAMILY_MIN_SCORE = 0.68


@dataclass(frozen=True, slots=True)
class PageProfile:
    page_number: int
    target_id: str

    text: str
    char_count: int
    word_count: int

    image_count: int

    table_count: int | None = None
    text_block_count: int | None = None
    element_count: int | None = None

    styles: tuple[str, ...] = ()
    image_placements: tuple[
        tuple[float, float, float, float],
        ...
    ] = ()


@dataclass(frozen=True, slots=True)
class PageSimilarityRelation:
    page_a: int
    page_b: int

    score: float

    relation: str


@dataclass(frozen=True, slots=True)
class PageFamilyCandidate:
    pages: tuple[int, ...]

    core_pages: tuple[int, ...]
    variant_pages: tuple[int, ...]


def _fact(
    analysis: AnalysisV4,
    version: SourceVersion,
    page_number: int,
    key: str,
) -> Any:
    return analysis.effective_value(
        target_type="source_page",
        target_id=(
            f"{version.id}:page:{page_number}"
        ),
        key="fact." + key,
    )


def _version_fact(
    analysis: AnalysisV4,
    version: SourceVersion,
    key: str,
) -> Any:
    return analysis.effective_value(
        target_type="source_version",
        target_id=version.id,
        key="fact." + key,
    )


def _ratio(
    left: float,
    right: float,
) -> float | None:
    maximum = max(
        float(left),
        float(right),
    )

    if maximum == 0:
        return None

    return min(
        float(left),
        float(right),
    ) / maximum


def _jaccard(
    left: set[str],
    right: set[str],
) -> float | None:
    union = left | right

    if not union:
        return None

    return len(
        left & right
    ) / len(union)


def _words(
    text: str,
) -> list[str]:
    return re.findall(
        r"[\wÀ-ÖØ-öø-ÿ’'-]+",
        text.lower(),
        flags=re.UNICODE,
    )


def _lines(
    text: str,
) -> list[str]:
    return [
        " ".join(
            line.lower().split()
        )
        for line in text.splitlines()
        if line.strip()
    ]


def _weighted_score(
    components: list[
        tuple[float, float | None]
    ],
) -> float:
    active = [
        (weight, value)
        for weight, value
        in components
        if value is not None
    ]

    if not active:
        return 0.0

    total_weight = sum(
        weight
        for weight, _
        in active
    )

    return sum(
        weight * float(value)
        for weight, value
        in active
    ) / total_weight


def _image_geometry_similarity(
    left: PageProfile,
    right: PageProfile,
) -> float | None:

    if (
        not left.image_placements
        and not right.image_placements
    ):
        return None

    if (
        len(left.image_placements)
        != len(right.image_placements)
    ):
        return 0.0

    if not left.image_placements:
        return None

    left_boxes = sorted(
        left.image_placements
    )

    right_boxes = sorted(
        right.image_placements
    )

    distances: list[float] = []

    for box_a, box_b in zip(
        left_boxes,
        right_boxes,
    ):
        distance = sum(
            abs(a - b)
            for a, b
            in zip(box_a, box_b)
        ) / 4.0

        distances.append(
            distance
        )

    average = sum(
        distances
    ) / len(distances)

    return max(
        0.0,
        1.0 - (
            average * 10.0
        ),
    )


def build_page_profile(
    analysis: AnalysisV4,
    version: SourceVersion,
    page_number: int,
) -> PageProfile:

    text = str(
        _fact(
            analysis,
            version,
            page_number,
            "text.content",
        )
        or ""
    )

    placements_raw = (
        _fact(
            analysis,
            version,
            page_number,
            "image.placements",
        )
        or []
    )

    placements: list[
        tuple[
            float,
            float,
            float,
            float,
        ]
    ] = []

    for raw in placements_raw:
        bbox = raw.get(
            "bbox_norm"
        )

        if (
            isinstance(bbox, list)
            and len(bbox) == 4
        ):
            placements.append(
                tuple(
                    float(value)
                    for value in bbox
                )
            )

    table_count = _fact(
        analysis,
        version,
        page_number,
        "table.count",
    )

    text_block_count = _fact(
        analysis,
        version,
        page_number,
        "layout.text_block_count",
    )

    element_count = _fact(
        analysis,
        version,
        page_number,
        "layout.element_count",
    )

    styles = (
        _fact(
            analysis,
            version,
            page_number,
            "paragraph.styles",
        )
        or []
    )

    return PageProfile(
        page_number=page_number,
        target_id=(
            f"{version.id}:page:{page_number}"
        ),
        text=text,
        char_count=int(
            _fact(
                analysis,
                version,
                page_number,
                "text.char_count",
            )
            or 0
        ),
        word_count=int(
            _fact(
                analysis,
                version,
                page_number,
                "text.word_count",
            )
            or 0
        ),
        image_count=int(
            _fact(
                analysis,
                version,
                page_number,
                "image.count",
            )
            or 0
        ),
        table_count=(
            int(table_count)
            if table_count is not None
            else None
        ),
        text_block_count=(
            int(text_block_count)
            if text_block_count is not None
            else None
        ),
        element_count=(
            int(element_count)
            if element_count is not None
            else None
        ),
        styles=tuple(
            sorted(
                str(value)
                for value in styles
            )
        ),
        image_placements=tuple(
            placements
        ),
    )


def similarity_score(
    left: PageProfile,
    right: PageProfile,
) -> float:

    left_words = _words(
        left.text
    )

    right_words = _words(
        right.text
    )

    left_lines = _lines(
        left.text
    )

    right_lines = _lines(
        right.text
    )

    image_count_score = (
        1.0
        if left.image_count
        == right.image_count
        else (
            _ratio(
                left.image_count,
                right.image_count,
            )
            or 0.0
        )
    )

    table_score: float | None = None

    if (
        left.table_count is not None
        and right.table_count is not None
    ):
        table_score = (
            1.0
            if left.table_count
            == right.table_count
            else (
                _ratio(
                    left.table_count,
                    right.table_count,
                )
                or 0.0
            )
        )

    text_block_score = None

    if (
        left.text_block_count is not None
        and right.text_block_count is not None
    ):
        text_block_score = _ratio(
            left.text_block_count,
            right.text_block_count,
        )

    element_score = None

    if (
        left.element_count is not None
        and right.element_count is not None
    ):
        element_score = _ratio(
            left.element_count,
            right.element_count,
        )

    style_score = _jaccard(
        set(left.styles),
        set(right.styles),
    )

    char_score = _ratio(
        left.char_count,
        right.char_count,
    )

    word_score = _ratio(
        left.word_count,
        right.word_count,
    )

    lexical_score = _jaccard(
        set(left_words),
        set(right_words),
    )

    line_score: float | None = None

    if left_lines or right_lines:
        line_score = (
            SequenceMatcher(
                None,
                left_lines,
                right_lines,
            ).ratio()
        )

    geometry_score = (
        _image_geometry_similarity(
            left,
            right,
        )
    )

    return round(
        _weighted_score(
            [
                (
                    0.10,
                    image_count_score,
                ),
                (
                    0.08,
                    table_score,
                ),
                (
                    0.18,
                    text_block_score,
                ),
                (
                    0.18,
                    element_score,
                ),
                (
                    0.12,
                    style_score,
                ),
                (
                    0.18,
                    geometry_score,
                ),
                (
                    0.08,
                    char_score,
                ),
                (
                    0.06,
                    word_score,
                ),
                (
                    0.20,
                    lexical_score,
                ),
                (
                    0.18,
                    line_score,
                ),
            ]
        ),
        6,
    )


def _same_model_candidate(
    left: PageProfile,
    right: PageProfile,
    score: float,
) -> bool:

    if score < 0.70:
        return False

    if (
        left.image_count
        != right.image_count
    ):
        return False

    if (
        left.table_count is not None
        and right.table_count is not None
        and left.table_count
        != right.table_count
    ):
        return False

    text_ratio = _ratio(
        left.char_count,
        right.char_count,
    )

    if (
        text_ratio is not None
        and text_ratio < 0.90
    ):
        return False

    if (
        left.text_block_count is not None
        and right.text_block_count is not None
    ):
        return (
            left.text_block_count
            == right.text_block_count
        )

    if (
        left.element_count is not None
        and right.element_count is not None
    ):
        if (
            left.element_count
            != right.element_count
        ):
            return False

        style_score = _jaccard(
            set(left.styles),
            set(right.styles),
        )

        if (
            style_score is not None
            and style_score < 0.95
        ):
            return False

        return True

    return score >= 0.74


def compare_source_pages(
    analysis: AnalysisV4,
    version: SourceVersion,
    *,
    minimum_score: float = FAMILY_MIN_SCORE,
) -> tuple[
    PageSimilarityRelation,
    ...
]:

    page_count = _version_fact(
        analysis,
        version,
        "document.page_count",
    )

    if page_count is None:
        raise ValueError(
            "Nombre de pages Source absent."
        )

    profiles = {
        number: build_page_profile(
            analysis,
            version,
            number,
        )
        for number
        in range(
            1,
            int(page_count) + 1,
        )
    }

    relations: list[
        PageSimilarityRelation
    ] = []

    for left_number in range(
        1,
        int(page_count) + 1,
    ):
        for right_number in range(
            left_number + 1,
            int(page_count) + 1,
        ):
            left = profiles[
                left_number
            ]

            right = profiles[
                right_number
            ]

            score = similarity_score(
                left,
                right,
            )

            if score < minimum_score:
                continue

            relation = (
                "modele_commun"
                if _same_model_candidate(
                    left,
                    right,
                    score,
                )
                else "variante_probable"
            )

            relations.append(
                PageSimilarityRelation(
                    page_a=left_number,
                    page_b=right_number,
                    score=score,
                    relation=relation,
                )
            )

    return tuple(
        relations
    )


def detect_page_families(
    relations: tuple[
        PageSimilarityRelation,
        ...
    ],
) -> tuple[
    PageFamilyCandidate,
    ...
]:

    if not relations:
        return ()

    parent: dict[int, int] = {}

    def find(value: int) -> int:
        parent.setdefault(
            value,
            value,
        )

        if parent[value] != value:
            parent[value] = find(
                parent[value]
            )

        return parent[value]

    def union(
        left: int,
        right: int,
    ) -> None:
        root_left = find(left)
        root_right = find(right)

        if root_left != root_right:
            parent[root_right] = (
                root_left
            )

    for relation in relations:
        union(
            relation.page_a,
            relation.page_b,
        )

    components: dict[
        int,
        set[int],
    ] = {}

    for page in list(parent):
        root = find(page)

        components.setdefault(
            root,
            set(),
        ).add(page)

    result: list[
        PageFamilyCandidate
    ] = []

    for pages in components.values():
        if len(pages) < 2:
            continue

        same_model_parent = {
            page: page
            for page in pages
        }

        def model_find(
            value: int,
        ) -> int:
            if (
                same_model_parent[value]
                != value
            ):
                same_model_parent[
                    value
                ] = model_find(
                    same_model_parent[
                        value
                    ]
                )

            return same_model_parent[
                value
            ]

        def model_union(
            left: int,
            right: int,
        ) -> None:
            root_left = model_find(
                left
            )

            root_right = model_find(
                right
            )

            if root_left != root_right:
                same_model_parent[
                    root_right
                ] = root_left

        for relation in relations:
            if (
                relation.page_a in pages
                and relation.page_b in pages
                and relation.relation
                == "modele_commun"
            ):
                model_union(
                    relation.page_a,
                    relation.page_b,
                )

        model_groups: dict[
            int,
            set[int],
        ] = {}

        for page in pages:
            root = model_find(page)

            model_groups.setdefault(
                root,
                set(),
            ).add(page)

        valid_cores = [
            group
            for group
            in model_groups.values()
            if len(group) >= 2
        ]

        if valid_cores:
            core = max(
                valid_cores,
                key=lambda group: (
                    len(group),
                    tuple(
                        -value
                        for value
                        in sorted(group)
                    ),
                ),
            )
        else:
            core = set()

        variants = (
            pages - core
        )

        result.append(
            PageFamilyCandidate(
                pages=tuple(
                    sorted(pages)
                ),
                core_pages=tuple(
                    sorted(core)
                ),
                variant_pages=tuple(
                    sorted(variants)
                ),
            )
        )

    result.sort(
        key=lambda family: (
            family.pages[0]
            if family.pages
            else 999999
        )
    )

    return tuple(result)

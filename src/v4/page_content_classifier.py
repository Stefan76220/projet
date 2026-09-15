from __future__ import annotations

from dataclasses import dataclass
from collections import Counter
from math import sqrt
from typing import Any


LABEL_TITLE = "Titre"
LABEL_TEXT = "Texte"
LABEL_TEXT_IMAGE = "Texte + image"
LABEL_IMAGE = "Image"
LABEL_IMAGES = "Images"
LABEL_TABLE = "Tableau"
LABEL_LIST = "Liste"
LABEL_SHEET = "Fiche"
LABEL_EMPTY = "Vide"


@dataclass(frozen=True)
class PageContentDescription:
    label: str
    confidence: float
    reason: str


def _kind_value(element: Any) -> str:

    if isinstance(
        element,
        dict,
    ):

        return str(
            element.get(
                "kind",
                "",
            )
            or ""
        ).lower()

    kind = getattr(
        element,
        "kind",
        "",
    )

    return str(
        getattr(
            kind,
            "value",
            kind,
        )
        or ""
    ).lower()

def _geometry(element: Any):

    if isinstance(
        element,
        dict,
    ):

        geometry = element.get(
            "geometry",
            {},
        )

        if not isinstance(
            geometry,
            dict,
        ):

            geometry = {}

        values = []

        for name in (
            "x_mm",
            "y_mm",
            "width_mm",
            "height_mm",
        ):

            try:

                values.append(
                    float(
                        geometry.get(
                            name,
                            0.0,
                        )
                        or 0.0
                    )
                )

            except Exception:

                values.append(
                    0.0
                )

        return tuple(
            values
        )

    values = []

    for name in (
        "x_mm",
        "y_mm",
        "width_mm",
        "height_mm",
    ):

        try:

            values.append(
                float(
                    getattr(
                        element,
                        name,
                        0.0,
                    )
                    or 0.0
                )
            )

        except Exception:

            values.append(
                0.0
            )

    return tuple(
        values
    )

def _payload(element: Any) -> dict:

    if isinstance(
        element,
        dict,
    ):

        value = element.get(
            "payload",
            {},
        )

    else:

        value = getattr(
            element,
            "payload",
            None,
        )

    return (
        value
        if isinstance(
            value,
            dict,
        )
        else {}
    )

def _metadata(element: Any) -> dict:

    if isinstance(
        element,
        dict,
    ):

        value = element.get(
            "metadata",
            {},
        )

    else:

        value = getattr(
            element,
            "metadata",
            None,
        )

    return (
        value
        if isinstance(
            value,
            dict,
        )
        else {}
    )


def _normalized_bbox(value):

    if (
        not isinstance(
            value,
            (list, tuple),
        )
        or len(value) != 4
    ):
        return None

    try:

        x0, y0, x1, y1 = (
            float(item)
            for item in value
        )

    except Exception:
        return None

    if (
        x1 <= x0
        or y1 <= y0
    ):
        return None

    return (
        x0,
        y0,
        x1,
        y1,
    )


def _intersection_area(
    left,
    right,
) -> float:

    x0 = max(
        left[0],
        right[0],
    )

    y0 = max(
        left[1],
        right[1],
    )

    x1 = min(
        left[2],
        right[2],
    )

    y1 = min(
        left[3],
        right[3],
    )

    return max(
        0.0,
        x1 - x0,
    ) * max(
        0.0,
        y1 - y0,
    )


def _page_dimensions(
    book,
):

    fmt = getattr(
        book,
        "format",
        None,
    )

    width = float(
        getattr(
            fmt,
            "width_mm",
            1.0,
        )
        or 1.0
    )

    height = float(
        getattr(
            fmt,
            "height_mm",
            1.0,
        )
        or 1.0
    )

    return (
        max(
            width,
            1.0,
        ),
        max(
            height,
            1.0,
        ),
    )


def _facts(
    book,
    page,
):

    page_w, page_h = (
        _page_dimensions(
            book
        )
    )

    page_area = (
        page_w
        * page_h
    )

    texts = []
    images = []

    for element in list(
        getattr(
            page,
            "content",
            [],
        )
        or []
    ):

        kind = (
            _kind_value(
                element
            )
        )

        if "text" in kind:

            texts.append(
                element
            )

        elif "image" in kind:

            images.append(
                element
            )

    words = 0
    characters = 0
    font_sizes = []

    text_area = 0.0

    block_line_counts = []
    block_word_counts = []
    text_values = []

    for element in texts:

        payload = (
            _payload(
                element
            )
        )

        block_text = str(
            payload.get(
                "text",
                "",
            )
            or ""
        ).strip()

        text_values.append(
            block_text
        )

        block_words = len(
            block_text.split()
        )

        block_word_counts.append(
            block_words
        )

        characters += len(
            block_text
        )

        words += block_words

        (
            _x,
            _y,
            width,
            height,
        ) = _geometry(
            element
        )

        text_area += max(
            0.0,
            width * height,
        )

        spans = payload.get(
            "spans",
            [],
        )

        line_indices = set()

        if isinstance(
            spans,
            list,
        ):

            for span in spans:

                if not isinstance(
                    span,
                    dict,
                ):
                    continue

                line_index = span.get(
                    "line_index"
                )

                if line_index is not None:

                    try:

                        line_indices.add(
                            int(
                                line_index
                            )
                        )

                    except Exception:
                        pass

                try:

                    size = float(
                        span.get(
                            "size",
                            0.0,
                        )
                        or 0.0
                    )

                except Exception:

                    size = 0.0

                if size > 0:

                    font_sizes.append(
                        size
                    )

        block_line_counts.append(
            max(
                1,
                len(
                    line_indices
                ),
            )
        )

    image_area = 0.0

    for element in images:

        (
            _x,
            _y,
            width,
            height,
        ) = _geometry(
            element
        )

        image_area += max(
            0.0,
            width * height,
        )

    max_font = max(
        font_sizes,
        default=0.0,
    )

    median_font = 0.0

    if font_sizes:

        ordered = sorted(
            font_sizes
        )

        median_font = ordered[
            len(
                ordered
            )
            // 2
        ]

    page_metadata = getattr(
        page,
        "metadata",
        {},
    )

    if not isinstance(
        page_metadata,
        dict,
    ):
        page_metadata = {}

    source_tables = page_metadata.get(
        "source_layout_tables",
        [],
    )

    if not isinstance(
        source_tables,
        list,
    ):
        source_tables = []

    source_lists = page_metadata.get(
        "source_layout_lists",
        [],
    )

    if not isinstance(
        source_lists,
        list,
    ):
        source_lists = []

    dominant_list_items = 0
    dominant_list_kind = ""

    for structure in source_lists:

        if not isinstance(
            structure,
            dict,
        ):
            continue

        try:
            item_count = int(
                structure.get(
                    "item_count",
                    0,
                )
                or 0
            )
        except Exception:
            item_count = 0

        if item_count > dominant_list_items:
            dominant_list_items = item_count
            dominant_list_kind = str(
                structure.get(
                    "kind",
                    "",
                )
                or ""
            )

    return {
        "table_count":
            len(
                source_tables
            ),

        "tables":
            source_tables,

        "list_count":
            len(
                source_lists
            ),

        "lists":
            source_lists,

        "dominant_list_items":
            dominant_list_items,

        "dominant_list_kind":
            dominant_list_kind,

        "texts":
            texts,

        "images":
            images,

        "text_count":
            len(
                texts
            ),

        "image_count":
            len(
                images
            ),

        "words":
            words,

        "characters":
            characters,

        "text_ratio":
            min(
                1.0,
                text_area
                / page_area,
            ),

        "image_ratio":
            min(
                1.0,
                image_area
                / page_area,
            ),

        "max_font":
            max_font,

        "median_font":
            median_font,

        "page_w":
            page_w,

        "page_h":
            page_h,

        "block_line_counts":
            block_line_counts,

        "block_word_counts":
            block_word_counts,

        "text_values":
            text_values,
    }

def _looks_like_image_grid(
    facts,
) -> bool:

    """
    Une structure tabulaire peut n'etre qu'une grille
    de mise en page.

    Si plusieurs images occupent reellement une part
    importante des cellules, la description visible
    devient "Images" et non "Tableau".
    """

    tables = facts.get(
        "tables",
        [],
    )

    images = facts.get(
        "images",
        [],
    )

    if (
        not tables
        or len(images) < 2
    ):
        return False

    image_boxes = []

    for element in images:

        metadata = _metadata(
            element
        )

        bbox = _normalized_bbox(
            metadata.get(
                "source_bbox_norm"
            )
        )

        if bbox is not None:

            image_boxes.append(
                bbox
            )

    if len(
        image_boxes
    ) < 2:

        return False

    for table in tables:

        if not isinstance(
            table,
            dict,
        ):
            continue

        table_bbox = _normalized_bbox(
            table.get(
                "bbox_norm"
            )
        )

        if table_bbox is None:
            continue

        table_area = (
            (
                table_bbox[2]
                - table_bbox[0]
            )
            * (
                table_bbox[3]
                - table_bbox[1]
            )
        )

        if table_area <= 0:
            continue

        inside_count = 0
        image_area_inside = 0.0

        for image_bbox in image_boxes:

            center_x = (
                image_bbox[0]
                + image_bbox[2]
            ) / 2.0

            center_y = (
                image_bbox[1]
                + image_bbox[3]
            ) / 2.0

            center_inside = (
                table_bbox[0]
                <= center_x
                <= table_bbox[2]
                and table_bbox[1]
                <= center_y
                <= table_bbox[3]
            )

            if not center_inside:
                continue

            inside_count += 1

            image_area_inside += (
                _intersection_area(
                    image_bbox,
                    table_bbox,
                )
            )

        coverage = (
            image_area_inside
            / table_area
        )

        try:

            rows = int(
                table.get(
                    "row_count",
                    0,
                )
                or 0
            )

            cols = int(
                table.get(
                    "col_count",
                    0,
                )
                or 0
            )

        except Exception:

            rows = 0
            cols = 0

        cell_count = (
            rows * cols
        )

        enough_images = (
            inside_count >= 2
        )

        if cell_count > 0:

            enough_images = (
                enough_images
                and inside_count
                >= max(
                    2,
                    int(
                        cell_count
                        * 0.50
                    ),
                )
            )

        # Les images doivent vraiment constituer
        # la matiere dominante de la grille.
        if (
            enough_images
            and coverage >= 0.35
        ):

            return True

    return False


def _looks_like_table(
    facts,
) -> bool:

    """
    Un tableau n'est jamais deduit de la geometrie
    des blocs texte.

    Il doit avoir ete reellement detecte lors de
    l'analyse Source.
    """

    return (
        int(
            facts.get(
                "table_count",
                0,
            )
            or 0
        )
        > 0
    )

def _base_description(
    facts,
) -> PageContentDescription:

    text_count = int(
        facts.get(
            "text_count",
            0,
        )
        or 0
    )

    image_count = int(
        facts.get(
            "image_count",
            0,
        )
        or 0
    )

    words = int(
        facts.get(
            "words",
            0,
        )
        or 0
    )

    image_ratio = float(
        facts.get(
            "image_ratio",
            0.0,
        )
        or 0.0
    )

    max_font = float(
        facts.get(
            "max_font",
            0.0,
        )
        or 0.0
    )

    # --------------------------------------------------------
    # 1. STRUCTURES FORTES
    # --------------------------------------------------------

    if _looks_like_image_grid(
        facts
    ):

        return PageContentDescription(
            LABEL_IMAGES,
            0.98,
            "Plusieurs images dominent une grille de mise en page.",
        )

    if _looks_like_table(
        facts
    ):

        return PageContentDescription(
            LABEL_TABLE,
            0.98,
            "Tableau reel detecte dans la Source.",
        )

    list_items = int(
        facts.get(
            "dominant_list_items",
            0,
        )
        or 0
    )

    blocks = max(
        1,
        text_count,
    )

    list_dominance = (
        list_items
        / blocks
    )

    list_kind = str(
        facts.get(
            "dominant_list_kind",
            "",
        )
        or ""
    )

    # Une liste à cases est souvent une sous-zone de contrôle au sein
    # d'une page textuelle. Elle ne devient le type dominant que si elle
    # occupe réellement l'essentiel de la matière textuelle.
    list_threshold = (
        0.75
        if list_kind == "checklist"
        else 0.55
    )

    if (
        list_items >= 4
        and list_dominance >= list_threshold
    ):

        return PageContentDescription(
            LABEL_LIST,
            0.95,
            "Une structure de liste domine la page.",
        )

    # --------------------------------------------------------
    # 2. VIDE
    # --------------------------------------------------------

    # Ignore les traces techniques minuscules d'un PDF.
    if (
        image_count == 0
        and words == 0
    ):

        return PageContentDescription(
            LABEL_EMPTY,
            0.99,
            "Aucune matiere significative.",
        )

    # --------------------------------------------------------
    # 3. IMAGE / IMAGES
    # --------------------------------------------------------

    if (
        image_count == 1
        and words == 0
        and image_ratio >= 0.50
    ):

        return PageContentDescription(
            LABEL_IMAGE,
            0.98,
            "Une image constitue l'essentiel de la page.",
        )

    if (
        image_count >= 2
        and (
            image_ratio >= 0.20
            or words <= 15
        )
    ):

        return PageContentDescription(
            LABEL_IMAGES,
            0.94,
            "Plusieurs images constituent l'essentiel de la page.",
        )

    # --------------------------------------------------------
    # 4. TITRE
    # --------------------------------------------------------

    # Ici "Titre" decrit une page tres peu chargee,
    # dominee typographiquement par un grand titre.
    #
    # Ce n'est pas un role editorial.
    if (
        words <= 25
        and text_count <= 5
        and max_font >= 22.0
        and image_ratio < 0.25
    ):

        return PageContentDescription(
            LABEL_TITLE,
            0.92,
            "Page peu chargee dominee par un grand titre.",
        )

    # --------------------------------------------------------
    # 5. CONTENU COURANT
    # --------------------------------------------------------

    if image_count == 0:

        return PageContentDescription(
            LABEL_TEXT,
            0.96,
            "Contenu essentiellement textuel.",
        )

    return PageContentDescription(
        LABEL_TEXT_IMAGE,
        0.96,
        "Texte et image sont tous deux significatifs.",
    )

def _layout_vector(
    book,
    page,
):

    """
    Signature structurelle d'une page.

    Elle ne regarde pas le sens du texte.
    Elle conserve :
    - nature texte / image ;
    - position ;
    - dimensions ;
    - taille typographique dominante.
    """

    page_w, page_h = (
        _page_dimensions(
            book
        )
    )

    signature = []

    for element in list(
        getattr(
            page,
            "content",
            [],
        )
        or []
    ):

        kind = _kind_value(
            element
        )

        if (
            "text" not in kind
            and "image" not in kind
        ):
            continue

        (
            x,
            y,
            width,
            height,
        ) = _geometry(
            element
        )

        if "image" in kind:

            signature.append(
                (
                    "I",
                    x / page_w,
                    y / page_h,
                    width / page_w,
                    height / page_h,
                    0.0,
                )
            )

            continue

        payload = _payload(
            element
        )

        sizes = []

        spans = payload.get(
            "spans",
            [],
        )

        if isinstance(
            spans,
            list,
        ):

            for span in spans:

                if not isinstance(
                    span,
                    dict,
                ):
                    continue

                try:

                    size = float(
                        span.get(
                            "size",
                            0.0,
                        )
                        or 0.0
                    )

                except Exception:

                    size = 0.0

                if size > 0:

                    sizes.append(
                        size
                    )

        dominant_size = (
            max(
                sizes
            )
            if sizes
            else 0.0
        )

        signature.append(
            (
                "T",
                x / page_w,
                y / page_h,
                width / page_w,
                height / page_h,
                dominant_size,
            )
        )

    return signature

def _layout_similarity(
    left,
    right,
) -> float:

    if (
        not left
        or not right
    ):

        return 0.0

    def item_distance(
        first,
        second,
    ):

        if first[0] != second[0]:

            return 999.0

        geometry = sqrt(
            sum(
                (
                    first[index]
                    - second[index]
                )
                ** 2
                for index
                in range(
                    1,
                    5,
                )
            )
        )

        font_penalty = 0.0

        if first[0] == "T":

            first_font = first[5]
            second_font = second[5]

            if (
                first_font > 0
                and second_font > 0
            ):

                font_penalty = min(
                    0.20,
                    abs(
                        first_font
                        - second_font
                    )
                    / max(
                        first_font,
                        second_font,
                    )
                    * 0.25,
                )

        return (
            geometry
            + font_penalty
        )

    if len(
        left
    ) <= len(
        right
    ):

        small = left
        large = right

    else:

        small = right
        large = left

    available = set(
        range(
            len(
                large
            )
        )
    )

    matched = []

    for item in small:

        best_index = None
        best_distance = None

        for index in available:

            distance = item_distance(
                item,
                large[index],
            )

            if (
                best_distance is None
                or distance
                < best_distance
            ):

                best_index = index
                best_distance = distance

        if (
            best_index is None
            or best_distance is None
            or best_distance > 0.12
        ):

            continue

        available.remove(
            best_index
        )

        matched.append(
            max(
                0.0,
                1.0
                - best_distance
                / 0.12,
            )
        )

    if not matched:

        return 0.0

    match_count = len(
        matched
    )

    core_coverage = (
        match_count
        / len(
            small
        )
    )

    total_coverage = (
        match_count
        / len(
            large
        )
    )

    precision = (
        sum(
            matched
        )
        / match_count
    )

    return (
        core_coverage
        * 0.50
        + total_coverage
        * 0.20
        + precision
        * 0.30
    )

def page_layout_similarity(
    book,
    left_page_id: str,
    right_page_id: str,
) -> float:
    """Score public de similarité de mise en page utilisé par TomeLinea.

    C'est exactement le moteur qui sert déjà à reconnaître les familles
    de fiches. Aucun second calcul de similarité n'est introduit.
    """

    pages = getattr(book, "pages", {})
    left = pages.get(str(left_page_id))
    right = pages.get(str(right_page_id))

    if left is None:
        raise KeyError(left_page_id)
    if right is None:
        raise KeyError(right_page_id)

    return float(
        _layout_similarity(
            _layout_vector(book, left),
            _layout_vector(book, right),
        )
    )


def similar_layout_page_ids(
    book,
    anchor_page_id: str,
    *,
    threshold: float = 0.88,
) -> list[str]:
    """Pages dont la mise en page est similaire à l'ancre au seuil choisi."""

    anchor_page_id = str(anchor_page_id)
    if anchor_page_id not in getattr(book, "pages", {}):
        raise KeyError(anchor_page_id)

    threshold = float(threshold)
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("Le seuil de similarité doit être compris entre 0 et 1.")

    result: list[str] = []
    for page_id in list(getattr(book, "page_order", []) or []):
        if page_id == anchor_page_id:
            result.append(page_id)
            continue

        try:
            score = page_layout_similarity(
                book,
                anchor_page_id,
                page_id,
            )
        except Exception:
            continue

        if score >= threshold:
            result.append(page_id)

    return result


def classify_book_pages(
    book,
):

    results = {}
    facts_by_id = {}
    vectors = {}

    page_order = list(
        getattr(
            book,
            "page_order",
            [],
        )
        or []
    )

    pages = getattr(
        book,
        "pages",
        {},
    )

    # --------------------------------------------------------
    # PREMIERE PASSE :
    # description du contenu de chaque page.
    # --------------------------------------------------------

    for page_id in page_order:

        page = pages.get(
            page_id
        )

        if page is None:
            continue

        facts = _facts(
            book,
            page,
        )

        facts_by_id[
            page_id
        ] = facts

        results[
            page_id
        ] = _base_description(
            facts
        )

        vectors[
            page_id
        ] = _layout_vector(
            book,
            page,
        )

    # --------------------------------------------------------
    # DEUXIEME PASSE :
    # recherche des familles repetitives.
    #
    # Fiche n'est jamais determinee par une page seule.
    # --------------------------------------------------------

    candidates = []

    for page_id in page_order:

        facts = facts_by_id.get(
            page_id
        )

        description = results.get(
            page_id
        )

        if (
            facts is None
            or description is None
        ):
            continue

        # Ces structures ont deja une signification
        # suffisamment forte pour ne pas devenir Fiche.
        if description.label in (
            LABEL_TABLE,
            LABEL_LIST,
            LABEL_EMPTY,
            LABEL_TITLE,
        ):

            continue

        element_count = (
            facts.get(
                "text_count",
                0,
            )
            + facts.get(
                "image_count",
                0,
            )
        )

        # Evite de transformer deux pages tres simples
        # en "Fiche" uniquement parce qu'elles se ressemblent.
        if element_count < 5:
            continue

        candidates.append(
            page_id
        )

    neighbours = {
        page_id: set()
        for page_id
        in candidates
    }

    for index, left_id in enumerate(
        candidates
    ):

        for right_id in candidates[
            index + 1:
        ]:

            score = _layout_similarity(
                vectors.get(
                    left_id,
                    [],
                ),
                vectors.get(
                    right_id,
                    [],
                ),
            )

            # "Fiche" exige une organisation
            # quasiment identique.
            if score >= 0.88:

                neighbours[
                    left_id
                ].add(
                    right_id
                )

                neighbours[
                    right_id
                ].add(
                    left_id
                )

    # --------------------------------------------------------
    # Une composante de plusieurs pages constitue
    # une famille de fiches.
    # --------------------------------------------------------

    visited = set()
    sheet_ids = set()

    for page_id in candidates:

        if page_id in visited:
            continue

        family = set()
        stack = [
            page_id
        ]

        while stack:

            current = stack.pop()

            if current in visited:
                continue

            visited.add(
                current
            )

            family.add(
                current
            )

            stack.extend(
                neighbours.get(
                    current,
                    set(),
                )
                - visited
            )

        # Une page seule n'est jamais une Fiche.
        if len(
            family
        ) >= 2:

            sheet_ids.update(
                family
            )

    for page_id in sheet_ids:

        results[
            page_id
        ] = PageContentDescription(
            LABEL_SHEET,
            0.95,
            (
                "Page appartenant a une famille "
                "de mises en page quasi identiques."
            ),
        )

    return results


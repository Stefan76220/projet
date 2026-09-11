from __future__ import annotations

"""
TomeLinea V4 ? pont Source / Analyse -> Composition.

Ce module mat?rialise le contenu objectivement extrait de la
Source dans PageV4.content lors de la cr?ation initiale du Livre.

Il ne remplace jamais une modification humaine.

La couche visuelle Source peut rester affich?e fid?lement :
les ?l?ments Composition existent d?j? sans devoir ?tre rendus
par-dessus tant que l'utilisateur ne les ?dite pas.
"""

from typing import Any

from src.v4.analysis import AnalysisV4
from src.v4.composition import (
    IMAGE,
    PAGE,
    TEXT,
    new_element,
    source_reference,
)
from src.v4.domain import BookV4


def _target_id(
    source_version_id: str,
    source_page: int,
) -> str:

    return (
        f"{source_version_id}:"
        f"page:{int(source_page)}"
    )


def _effective(
    analysis: AnalysisV4,
    target_id: str,
    key: str,
    default=None,
):

    value = analysis.effective_value(
        target_type="source_page",
        target_id=target_id,
        key=f"fact.{key}",
    )

    if value is None:
        return default

    return value


def _bbox(
    value: Any,
) -> tuple[
    float,
    float,
    float,
    float,
] | None:

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

    # La zone repr?sente le contenu visible
    # sur la page Source.
    x0 = max(
        0.0,
        min(
            1.0,
            x0,
        ),
    )

    y0 = max(
        0.0,
        min(
            1.0,
            y0,
        ),
    )

    x1 = max(
        0.0,
        min(
            1.0,
            x1,
        ),
    )

    y1 = max(
        0.0,
        min(
            1.0,
            y1,
        ),
    )

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


def _map_bbox_to_book(
    *,
    bbox_norm,
    source_width_mm: float,
    source_height_mm: float,
    book_width_mm: float,
    book_height_mm: float,
) -> tuple[
    float,
    float,
    float,
    float,
] | None:
    """
    Reproduit le m?me principe que l'affichage Source :
    la page originale est contenue proportionnellement dans
    le format du Livre et centr?e si les rapports diff?rent.
    """

    box = _bbox(
        bbox_norm
    )

    if box is None:
        return None

    (
        x0,
        y0,
        x1,
        y1,
    ) = box

    source_width_mm = max(
        0.001,
        float(
            source_width_mm
        ),
    )

    source_height_mm = max(
        0.001,
        float(
            source_height_mm
        ),
    )

    book_width_mm = max(
        0.001,
        float(
            book_width_mm
        ),
    )

    book_height_mm = max(
        0.001,
        float(
            book_height_mm
        ),
    )

    scale = min(
        book_width_mm
        / source_width_mm,

        book_height_mm
        / source_height_mm,
    )

    rendered_width = (
        source_width_mm
        * scale
    )

    rendered_height = (
        source_height_mm
        * scale
    )

    offset_x = (
        book_width_mm
        - rendered_width
    ) / 2.0

    offset_y = (
        book_height_mm
        - rendered_height
    ) / 2.0

    x_mm = (
        offset_x
        + x0 * rendered_width
    )

    y_mm = (
        offset_y
        + y0 * rendered_height
    )

    width_mm = (
        (x1 - x0)
        * rendered_width
    )

    height_mm = (
        (y1 - y0)
        * rendered_height
    )

    if (
        width_mm <= 0
        or height_mm <= 0
    ):
        return None

    return (
        x_mm,
        y_mm,
        width_mm,
        height_mm,
    )


def materialize_initial_composition(
    analysis: AnalysisV4,
    book: BookV4,
) -> dict[str, int]:
    """
    Construit les premiers objets de Composition ? partir
    des faits effectifs de l'Analyse.

    Cette fonction est destin?e uniquement au Livre initial.

    Elle ne touche pas aux pages poss?dant d?j? du contenu :
    une r?analyse future doit passer par le moteur de r?analyse.
    """

    text_count = 0
    image_count = 0
    page_count = 0

    fmt = book.format

    for page in book.ordered_pages():

        source = page.source

        if source is None:
            continue

        if source.source_page is None:
            continue

        # Ne jamais ?craser un contenu d?j? mat?rialis?.
        if page.content:
            continue

        target_id = _target_id(
            source.source_version_id,
            source.source_page,
        )

        source_width = _effective(
            analysis,
            target_id,
            "page.width_mm",
            float(
                fmt.width_mm
            ),
        )

        source_height = _effective(
            analysis,
            target_id,
            "page.height_mm",
            float(
                fmt.height_mm
            ),
        )

        text_blocks = _effective(
            analysis,
            target_id,
            "layout.text_blocks",
            [],
        )

        image_placements = _effective(
            analysis,
            target_id,
            "image.placements",
            [],
        )

        table_placements = _effective(
            analysis,
            target_id,
            "layout.tables",
            [],
        )

        list_structures = _effective(
            analysis,
            target_id,
            "layout.lists",
            [],
        )

        source_ref = source_reference(
            source_element_id=(
                source.source_id
            ),
            source_version_id=(
                source.source_version_id
            ),
            source_page=(
                source.source_page
            ),
        )

        # Resultat factuel de l'analyse Source.
        # Il ne s'agit pas d'un type de page :
        # seulement de structures reellement detectees.
        page.metadata[
            "source_layout_tables"
        ] = (
            table_placements
            if isinstance(
                table_placements,
                list,
            )
            else []
        )

        page.metadata[
            "source_layout_lists"
        ] = (
            list_structures
            if isinstance(
                list_structures,
                list,
            )
            else []
        )

        page_created = False

        # Un flux repr?sente ici le flux textuel
        # de la Source enti?re.
        #
        # Les paragraph_id peuvent ensuite ?tre fusionn?s
        # par le moteur de continuit? entre pages.
        flow_id = (
            "source-flow:"
            f"{source.source_id}:"
            f"{source.source_version_id}"
        )

        if isinstance(
            text_blocks,
            list,
        ):

            for local_index, block in enumerate(
                text_blocks
            ):

                if not isinstance(
                    block,
                    dict,
                ):
                    continue

                geometry = _map_bbox_to_book(
                    bbox_norm=block.get(
                        "bbox_norm"
                    ),
                    source_width_mm=(
                        source_width
                    ),
                    source_height_mm=(
                        source_height
                    ),
                    book_width_mm=(
                        fmt.width_mm
                    ),
                    book_height_mm=(
                        fmt.height_mm
                    ),
                )

                if geometry is None:
                    continue

                block_text = str(
                    block.get(
                        "text",
                        "",
                    )
                ).strip()

                if not block_text:
                    continue

                block_index = int(
                    block.get(
                        "block_index",
                        local_index,
                    )
                )

                block_sub_index = block.get(
                    "block_sub_index"
                )
                paragraph_suffix = str(block_index)
                if block_sub_index is not None:
                    try:
                        paragraph_suffix += f":{int(block_sub_index)}"
                    except (TypeError, ValueError):
                        paragraph_suffix += f":{block_sub_index}"

                paragraph_id = (
                    "source-paragraph:"
                    f"{source.source_id}:"
                    f"{source.source_version_id}:"
                    f"{source.source_page}:"
                    f"{paragraph_suffix}"
                )

                (
                    x_mm,
                    y_mm,
                    width_mm,
                    height_mm,
                ) = geometry

                element = new_element(
                    kind=TEXT,
                    x_mm=x_mm,
                    y_mm=y_mm,
                    width_mm=width_mm,
                    height_mm=height_mm,
                    reference_frame=PAGE,
                    source_ref=source_ref,
                    payload={
                        "text":
                            block_text,

                        "flow_id":
                            flow_id,

                        "paragraph_id":
                            paragraph_id,

                        "segment_index":
                            0,

                        "spans":
                            block.get(
                                "spans",
                                [],
                            ),
                    },
                    metadata={
                        "origin":
                            "analysis_source",

                        "analysis_target_id":
                            target_id,

                        "analysis_key":
                            "fact.layout.text_blocks",

                        "source_bbox_norm":
                            block.get(
                                "bbox_norm"
                            ),

                        "source_block_index":
                            block_index,

                        "source_block_sub_index":
                            block_sub_index,

                        # La Source reste la r?f?rence visuelle
                        # tant que l'objet n'a pas ?t? ?dit?.
                        "source_visual_preserved":
                            True,

                        "continuation_state":
                            "not_analyzed",
                    },
                )

                page.content.append(
                    element
                )

                text_count += 1
                page_created = True

        if isinstance(
            image_placements,
            list,
        ):

            for image_index, image in enumerate(
                image_placements
            ):

                if not isinstance(
                    image,
                    dict,
                ):
                    continue

                geometry = _map_bbox_to_book(
                    bbox_norm=image.get(
                        "bbox_norm"
                    ),
                    source_width_mm=(
                        source_width
                    ),
                    source_height_mm=(
                        source_height
                    ),
                    book_width_mm=(
                        fmt.width_mm
                    ),
                    book_height_mm=(
                        fmt.height_mm
                    ),
                )

                if geometry is None:
                    continue

                (
                    x_mm,
                    y_mm,
                    width_mm,
                    height_mm,
                ) = geometry

                element = new_element(
                    kind=IMAGE,
                    x_mm=x_mm,
                    y_mm=y_mm,
                    width_mm=width_mm,
                    height_mm=height_mm,
                    reference_frame=PAGE,
                    source_ref=source_ref,
                    payload={
                        "xref":
                            int(
                                image.get(
                                    "xref",
                                    0,
                                )
                                or 0
                            ),

                        "width_px":
                            int(
                                image.get(
                                    "width_px",
                                    0,
                                )
                                or 0
                            ),

                        "height_px":
                            int(
                                image.get(
                                    "height_px",
                                    0,
                                )
                                or 0
                            ),
                    },
                    metadata={
                        "origin":
                            "analysis_source",

                        "analysis_target_id":
                            target_id,

                        "analysis_key":
                            "fact.image.placements",

                        "source_bbox_norm":
                            image.get(
                                "bbox_norm"
                            ),

                        "source_image_index":
                            image_index,

                        "source_visual_preserved":
                            True,
                    },
                )

                page.content.append(
                    element
                )

                image_count += 1
                page_created = True

        if page_created:
            page_count += 1

    # Les coordonnées extraites du PDF ne suffisent pas pour les futurs
    # changements de format. On mémorise dès l'analyse les relations logiques
    # texte / image proposées (paragraphe, titre, etc.).
    from src.v4.content_anchors import infer_book_content_anchors

    anchor_result = infer_book_content_anchors(book, overwrite=False)

    book.history.append(
        {
            "action":
                "initial_composition_from_analysis",

            "pages":
                page_count,

            "text_elements":
                text_count,

            "image_elements":
                image_count,

            "anchored_images":
                anchor_result.images_anchored,
        }
    )

    book.validate()

    return {
        "pages":
            page_count,

        "text_elements":
            text_count,

        "image_elements":
            image_count,
    }

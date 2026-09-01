from __future__ import annotations

"""
TomeLinea V4 — extraction factuelle déterministe des Sources.

Cette couche ne classe pas éditorialement le livre.
Elle observe uniquement ce qui est objectivement présent.

Formats initiaux :
- PDF : géométrie, texte, blocs et images réellement placées ;
- ODT : structure XML native, styles, tableaux, images et sauts de page.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
import re
import zipfile
import xml.etree.ElementTree as ET

from src.v4.analysis import AnalysisFinding, AnalysisV4
from src.v4.intelligence import record_fact
from src.v4.source import SourceVersion


EXTRACTOR_ENGINE = "tomelinea.source_extraction"
EXTRACTOR_VERSION = "1"


@dataclass(frozen=True, slots=True)
class ExtractionSummary:
    source_version_id: str
    file_type: str
    page_count: int | None
    observations_recorded: int


class _FactRecorder:
    def __init__(
        self,
        analysis: AnalysisV4,
        version: SourceVersion,
    ) -> None:
        self.analysis = analysis
        self.version = version
        self.findings: list[AnalysisFinding] = []

    def add(
        self,
        *,
        target_type: str,
        target_id: str,
        key: str,
        value: Any,
        evidence: tuple[str, ...] = (),
    ) -> AnalysisFinding:
        finding = record_fact(
            self.analysis,
            target_type=target_type,
            target_id=target_id,
            key=key,
            value=value,
            engine=EXTRACTOR_ENGINE,
            engine_version=EXTRACTOR_VERSION,
            source_version_ids=(self.version.id,),
            evidence=evidence,
        )
        self.findings.append(finding)
        return finding


def _page_target(
    version: SourceVersion,
    page_number: int,
) -> str:
    return f"{version.id}:page:{page_number}"


def _clean_text(value: str) -> str:
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    return "\n".join(
        line.rstrip()
        for line in value.split("\n")
    ).strip()


def _word_count(value: str) -> int:
    return len(
        re.findall(
            r"\b[\wÀ-ÖØ-öø-ÿ’'-]+\b",
            value,
            flags=re.UNICODE,
        )
    )


def _orientation(
    width: float,
    height: float,
) -> str:
    if abs(width - height) < 0.01:
        return "carre"
    return "paysage" if width > height else "portrait"


def _round_mm(value: float) -> float:
    return round(float(value), 3)


# ==============================================================
# PDF
# ==============================================================

def _extract_pdf(
    recorder: _FactRecorder,
    path: Path,
) -> int:
    try:
        import pymupdf
    except ImportError as exc:
        raise RuntimeError(
            "L'extraction PDF nécessite PyMuPDF."
        ) from exc

    document = pymupdf.open(path)

    try:
        page_count = int(document.page_count)
        total_text_chars = 0
        total_images = 0
        page_sizes: list[tuple[float, float]] = []

        for index in range(page_count):
            page = document[index]
            number = index + 1
            target_id = _page_target(
                recorder.version,
                number,
            )

            width_mm = _round_mm(
                page.rect.width * 25.4 / 72.0
            )
            height_mm = _round_mm(
                page.rect.height * 25.4 / 72.0
            )

            page_sizes.append(
                (width_mm, height_mm)
            )

            text = _clean_text(
                page.get_text("text")
            )

            text_chars = len(text)
            total_text_chars += text_chars

            raw_blocks = page.get_text(
                "dict"
            ).get("blocks", [])

            text_blocks = [
                block
                for block in raw_blocks
                if int(
                    block.get("type", -1)
                ) == 0
            ]

            image_info = page.get_image_info(
                xrefs=True
            )

            total_images += len(image_info)

            page_area = float(
                page.rect.width
                * page.rect.height
            ) or 1.0

            image_area = 0.0
            placements: list[
                dict[str, Any]
            ] = []

            for image in image_info:
                bbox = tuple(
                    float(value)
                    for value in image.get(
                        "bbox",
                        (0, 0, 0, 0),
                    )
                )

                x0, y0, x1, y1 = bbox

                area = (
                    max(0.0, x1 - x0)
                    * max(0.0, y1 - y0)
                )

                image_area += area

                placements.append(
                    {
                        "xref": int(
                            image.get(
                                "xref",
                                0,
                            ) or 0
                        ),
                        "bbox_norm": [
                            round(
                                x0
                                / page.rect.width,
                                6,
                            ),
                            round(
                                y0
                                / page.rect.height,
                                6,
                            ),
                            round(
                                x1
                                / page.rect.width,
                                6,
                            ),
                            round(
                                y1
                                / page.rect.height,
                                6,
                            ),
                        ],
                        "width_px": int(
                            image.get(
                                "width",
                                0,
                            ) or 0
                        ),
                        "height_px": int(
                            image.get(
                                "height",
                                0,
                            ) or 0
                        ),
                    }
                )

            common = {
                "target_type": "source_page",
                "target_id": target_id,
            }

            recorder.add(
                **common,
                key="page.number",
                value=number,
            )

            recorder.add(
                **common,
                key="page.width_mm",
                value=width_mm,
            )

            recorder.add(
                **common,
                key="page.height_mm",
                value=height_mm,
            )

            recorder.add(
                **common,
                key="page.orientation",
                value=_orientation(
                    width_mm,
                    height_mm,
                ),
            )

            recorder.add(
                **common,
                key="text.content",
                value=text,
            )

            recorder.add(
                **common,
                key="text.char_count",
                value=text_chars,
            )

            recorder.add(
                **common,
                key="text.word_count",
                value=_word_count(text),
            )

            recorder.add(
                **common,
                key="layout.text_block_count",
                value=len(text_blocks),
            )

            recorder.add(
                **common,
                key="image.count",
                value=len(image_info),
            )

            recorder.add(
                **common,
                key="image.placements",
                value=placements,
            )

            recorder.add(
                **common,
                key="image.coverage_ratio",
                value=round(
                    image_area / page_area,
                    6,
                ),
            )

        version_id = recorder.version.id

        recorder.add(
            target_type="source_version",
            target_id=version_id,
            key="document.native_kind",
            value="pdf_layout",
        )

        recorder.add(
            target_type="source_version",
            target_id=version_id,
            key="document.page_count",
            value=page_count,
        )

        recorder.add(
            target_type="source_version",
            target_id=version_id,
            key="document.text_extractable",
            value=total_text_chars > 0,
        )

        recorder.add(
            target_type="source_version",
            target_id=version_id,
            key="document.text_char_count",
            value=total_text_chars,
        )

        recorder.add(
            target_type="source_version",
            target_id=version_id,
            key="document.placed_image_count",
            value=total_images,
        )

        recorder.add(
            target_type="source_version",
            target_id=version_id,
            key="document.page_sizes_mm",
            value=[
                list(item)
                for item
                in sorted(
                    set(page_sizes)
                )
            ],
        )

        return page_count

    finally:
        document.close()


# ==============================================================
# ODT
# ==============================================================

_ODT_NS = {
    "office":
        "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "text":
        "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
    "table":
        "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
    "draw":
        "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0",
    "style":
        "urn:oasis:names:tc:opendocument:xmlns:style:1.0",
    "fo":
        "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0",
}


def _q(
    namespace: str,
    name: str,
) -> str:
    return (
        f"{{{_ODT_NS[namespace]}}}"
        f"{name}"
    )


def _odt_break_styles(
    *roots: ET.Element,
) -> set[str]:
    result: set[str] = set()

    for root in roots:
        for style in root.findall(
            ".//style:style",
            _ODT_NS,
        ):
            name = style.get(
                _q("style", "name")
            )

            props = style.find(
                "style:paragraph-properties",
                _ODT_NS,
            )

            if not name or props is None:
                continue

            before = props.get(
                _q(
                    "fo",
                    "break-before",
                )
            )

            after = props.get(
                _q(
                    "fo",
                    "break-after",
                )
            )

            if (
                before == "page"
                or after == "page"
            ):
                result.add(name)

    return result


def _length_to_mm(
    raw: str | None,
) -> float | None:
    if raw is None:
        return None

    match = re.fullmatch(
        r"\s*"
        r"([+-]?(?:\d+(?:\.\d*)?|\.\d+))"
        r"\s*(mm|cm|in|pt|pc)\s*",
        raw,
        flags=re.IGNORECASE,
    )

    if not match:
        return None

    value = float(match.group(1))
    unit = match.group(2).lower()

    factors = {
        "mm": 1.0,
        "cm": 10.0,
        "in": 25.4,
        "pt": 25.4 / 72.0,
        "pc": 25.4 / 6.0,
    }

    return _round_mm(
        value * factors[unit]
    )


def _odt_page_layout(
    styles_root: ET.Element,
) -> dict[str, Any]:
    layout = styles_root.find(
        ".//style:page-layout",
        _ODT_NS,
    )

    if layout is None:
        return {}

    props = layout.find(
        "style:page-layout-properties",
        _ODT_NS,
    )

    if props is None:
        return {}

    result: dict[str, Any] = {}

    mapping = {
        "width_mm": "page-width",
        "height_mm": "page-height",
        "margin_top_mm": "margin-top",
        "margin_bottom_mm": "margin-bottom",
        "margin_left_mm": "margin-left",
        "margin_right_mm": "margin-right",
    }

    for key, attr in mapping.items():
        value = _length_to_mm(
            props.get(
                _q("fo", attr)
            )
        )

        if value is not None:
            result[key] = value

    orientation = props.get(
        _q(
            "style",
            "print-orientation",
        )
    )

    if orientation:
        result[
            "orientation"
        ] = orientation

    return result


def _element_text(
    element: ET.Element,
) -> str:
    return _clean_text(
        "".join(
            element.itertext()
        )
    )


def _extract_odt(
    recorder: _FactRecorder,
    path: Path,
) -> int:
    with zipfile.ZipFile(path) as archive:
        content_root = ET.fromstring(
            archive.read(
                "content.xml"
            )
        )

        styles_root = ET.fromstring(
            archive.read(
                "styles.xml"
            )
        )

        body = content_root.find(
            ".//office:body/office:text",
            _ODT_NS,
        )

        if body is None:
            raise ValueError(
                "ODT sans corps exploitable."
            )

        break_styles = (
            _odt_break_styles(
                content_root,
                styles_root,
            )
        )

        style_attr = _q(
            "text",
            "style-name",
        )

        pages: list[
            list[ET.Element]
        ] = [[]]

        break_count = 0

        for element in list(body):
            style_name = element.get(
                style_attr
            )

            is_break = (
                element.tag
                == _q("text", "p")
                and style_name
                in break_styles
            )

            if is_break:
                break_count += 1
                pages.append([])
                continue

            pages[-1].append(element)

        if (
            pages
            and not pages[-1]
            and len(pages) > 1
        ):
            pages.pop()

        used_styles: set[str] = set()
        total_images = 0
        total_tables = 0
        total_text_chars = 0

        for number, elements in enumerate(
            pages,
            start=1,
        ):
            target_id = _page_target(
                recorder.version,
                number,
            )

            text_parts: list[str] = []
            page_styles: set[str] = set()
            image_count = 0
            table_count = 0

            for element in elements:
                text = _element_text(
                    element
                )

                if text:
                    text_parts.append(text)

                for node in element.iter():
                    style_name = node.get(
                        style_attr
                    )

                    if style_name:
                        page_styles.add(
                            style_name
                        )

                        used_styles.add(
                            style_name
                        )

                image_count += len(
                    element.findall(
                        ".//draw:image",
                        _ODT_NS,
                    )
                )

                if (
                    element.tag
                    == _q(
                        "table",
                        "table",
                    )
                ):
                    table_count += 1
                else:
                    table_count += len(
                        element.findall(
                            ".//table:table",
                            _ODT_NS,
                        )
                    )

            text = _clean_text(
                "\n".join(
                    text_parts
                )
            )

            total_text_chars += len(text)
            total_images += image_count
            total_tables += table_count

            common = {
                "target_type":
                    "source_page",
                "target_id":
                    target_id,
            }

            recorder.add(
                **common,
                key="page.number",
                value=number,
            )

            recorder.add(
                **common,
                key="text.content",
                value=text,
            )

            recorder.add(
                **common,
                key="text.char_count",
                value=len(text),
            )

            recorder.add(
                **common,
                key="text.word_count",
                value=_word_count(text),
            )

            recorder.add(
                **common,
                key="image.count",
                value=image_count,
            )

            recorder.add(
                **common,
                key="table.count",
                value=table_count,
            )

            recorder.add(
                **common,
                key="paragraph.styles",
                value=sorted(
                    page_styles
                ),
            )

            recorder.add(
                **common,
                key="layout.element_count",
                value=len(elements),
            )

        version_id = (
            recorder.version.id
        )

        pictures = [
            name
            for name
            in archive.namelist()
            if (
                name.startswith(
                    "Pictures/"
                )
                and not name.endswith("/")
            )
        ]

        recorder.add(
            target_type="source_version",
            target_id=version_id,
            key="document.native_kind",
            value="odt_structured",
        )

        recorder.add(
            target_type="source_version",
            target_id=version_id,
            key="document.page_count",
            value=len(pages),
        )

        recorder.add(
            target_type="source_version",
            target_id=version_id,
            key="document.explicit_page_break_count",
            value=break_count,
        )

        recorder.add(
            target_type="source_version",
            target_id=version_id,
            key="document.paragraph_style_names",
            value=sorted(
                used_styles
            ),
        )

        recorder.add(
            target_type="source_version",
            target_id=version_id,
            key="document.embedded_image_count",
            value=len(pictures),
        )

        recorder.add(
            target_type="source_version",
            target_id=version_id,
            key="document.placed_image_count",
            value=total_images,
        )

        recorder.add(
            target_type="source_version",
            target_id=version_id,
            key="document.table_count",
            value=total_tables,
        )

        recorder.add(
            target_type="source_version",
            target_id=version_id,
            key="document.text_char_count",
            value=total_text_chars,
        )

        recorder.add(
            target_type="source_version",
            target_id=version_id,
            key="document.page_layout",
            value=_odt_page_layout(
                styles_root
            ),
        )

        return len(pages)


_EXTRACTORS: dict[
    str,
    Callable[
        [_FactRecorder, Path],
        int,
    ],
] = {
    "pdf": _extract_pdf,
    "odt": _extract_odt,
}


def extract_source_version(
    analysis: AnalysisV4,
    version: SourceVersion,
) -> ExtractionSummary:
    """
    Extrait les faits objectifs d'une version Source enregistrée.
    """

    path = Path(
        version.original_path
    ).expanduser().resolve()

    if not path.is_file():
        raise FileNotFoundError(path)

    file_type = (
        version.file_type
        .lower()
        .lstrip(".")
    )

    extractor = _EXTRACTORS.get(
        file_type
    )

    if extractor is None:
        raise ValueError(
            "Format Source non encore "
            f"pris en charge : {file_type or '?'}"
        )

    recorder = _FactRecorder(
        analysis,
        version,
    )

    recorder.add(
        target_type="source_version",
        target_id=version.id,
        key="file.type",
        value=file_type,
    )

    recorder.add(
        target_type="source_version",
        target_id=version.id,
        key="file.size_bytes",
        value=version.size_bytes,
    )

    recorder.add(
        target_type="source_version",
        target_id=version.id,
        key="file.fingerprint",
        value=version.fingerprint,
    )

    page_count = extractor(
        recorder,
        path,
    )

    analysis.mark_source_version_analyzed(
        version.id,
        version.fingerprint,
    )

    return ExtractionSummary(
        source_version_id=version.id,
        file_type=file_type,
        page_count=page_count,
        observations_recorded=len(
            recorder.findings
        ),
    )

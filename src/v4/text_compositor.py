from __future__ import annotations

"""Moteur de composition de texte TomeLinea V4.

Cette couche ne crée pas de choix éditoriaux. Elle applique des règles déjà
validées par le livre et s'appuie, lorsque disponible, sur :
- uniseg (MIT) pour les possibilités de coupure Unicode UAX #14 ;
- les motifs français TeX `hyph-fr.tex` (MIT) pour les césures françaises.

Le moteur reste utilisable sans ces ressources : il retombe alors sur un
comportement conservateur et n'invente jamais une césure.
"""

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import math
import re
from typing import Callable, Iterable, Iterator, Sequence


try:  # dépendance pure Python, MIT
    from uniseg.linebreak import line_break_units as _uax14_line_break_units
except Exception:  # pragma: no cover - repli volontaire si dépendance absente
    _uax14_line_break_units = None


ENGINE_VERSION = "1.0"

DEFAULT_CONTROLLED_HYPHENATION = {
    "min_word_length": 7,
    "min_left": 3,
    "min_right": 3,
    "max_consecutive": 2,
    "last_word": False,
    "across_page": False,
}

FRENCH_PATTERN_RELATIVE_PATH = Path("assets") / "typography" / "hyph-fr.tex"


def project_hyphenation_pattern_path(project_root: str | Path | None = None) -> Path:
    if project_root is None:
        project_root = Path(__file__).resolve().parents[2]
    return Path(project_root) / FRENCH_PATTERN_RELATIVE_PATH


def _letters_only(value: str) -> str:
    return "".join(ch for ch in str(value or "") if ch.isalpha() or ch in "’'")


def unicode_line_units(text: str) -> tuple[str, ...]:
    """Unités de coupure de ligne selon UAX #14 si uniseg est disponible.

    Le repli n'autorise les coupures qu'aux espaces ordinaires et ne coupe
    jamais sur espace insécable / espace fine insécable.
    """
    value = str(text or "")
    if not value:
        return ()
    if _uax14_line_break_units is not None:
        try:
            return tuple(_uax14_line_break_units(value))
        except Exception:
            pass

    # Repli conservateur : conserver les espaces avec l'unité précédente,
    # et ne jamais proposer de coupure autour des espaces insécables.
    units: list[str] = []
    current = ""
    for ch in value:
        current += ch
        if ch == " ":
            units.append(current)
            current = ""
        elif ch in "\n\r":
            units.append(current)
            current = ""
    if current:
        units.append(current)
    return tuple(units)


@dataclass(frozen=True, slots=True)
class HyphenationPattern:
    letters: str
    weights: tuple[int, ...]


class FrenchPatternHyphenator:
    """Implémentation locale de l'algorithme de motifs TeX (Liang).

    Les *données* de langue restent dans `hyph-fr.tex`, distribué sous licence
    MIT. Aucun code de TeX, LibreOffice ou autre moteur n'est repris.
    """

    def __init__(
        self,
        patterns: Sequence[HyphenationPattern] = (),
        exceptions: dict[str, tuple[int, ...]] | None = None,
        *,
        left_min: int = 2,
        right_min: int = 2,
    ) -> None:
        self.patterns = tuple(patterns)
        self.exceptions = dict(exceptions or {})
        self.left_min = max(1, int(left_min))
        self.right_min = max(1, int(right_min))
        by_first: dict[str, list[HyphenationPattern]] = {}
        for pattern in self.patterns:
            key = pattern.letters[:1]
            by_first.setdefault(key, []).append(pattern)
        self._by_first = {key: tuple(values) for key, values in by_first.items()}

    @property
    def available(self) -> bool:
        return bool(self.patterns or self.exceptions)

    @classmethod
    def from_tex(cls, text: str) -> "FrenchPatternHyphenator":
        source = str(text or "")
        left_min = 2
        right_min = 2
        # Le fichier français documente hyphenmins dans son en-tête YAML.
        left_match = re.search(r"(?m)^\s*%\s*left:\s*(\d+)\s*$", source)
        right_match = re.search(r"(?m)^\s*%\s*right:\s*(\d+)\s*$", source)
        if left_match:
            left_min = int(left_match.group(1))
        if right_match:
            right_min = int(right_match.group(1))

        # Retirer commentaires TeX avant extraction des blocs.
        cleaned_lines = []
        for raw_line in source.splitlines():
            line = raw_line.split("%", 1)[0]
            if line.strip():
                cleaned_lines.append(line)
        cleaned = "\n".join(cleaned_lines)

        patterns: list[HyphenationPattern] = []
        for block in re.findall(r"\\patterns\s*\{(.*?)\}", cleaned, re.S):
            for token in re.findall(r"\S+", block):
                parsed = _parse_tex_pattern(token)
                if parsed is not None:
                    patterns.append(parsed)

        exceptions: dict[str, tuple[int, ...]] = {}
        for block in re.findall(r"\\hyphenation\s*\{(.*?)\}", cleaned, re.S):
            for token in re.findall(r"\S+", block):
                plain = token.replace("-", "").lower()
                if not plain:
                    continue
                positions: list[int] = []
                count = 0
                for ch in token:
                    if ch == "-":
                        positions.append(count)
                    else:
                        count += 1
                exceptions[plain] = tuple(positions)

        return cls(patterns, exceptions, left_min=left_min, right_min=right_min)

    @classmethod
    def from_file(cls, path: str | Path) -> "FrenchPatternHyphenator":
        return cls.from_tex(Path(path).read_text(encoding="utf-8", errors="replace"))

    def positions(
        self,
        word: str,
        *,
        min_left: int | None = None,
        min_right: int | None = None,
    ) -> tuple[int, ...]:
        raw = str(word or "").strip().replace("’", "'")
        # Les motifs français couvrent les mots alphabétiques ; les mots avec
        # tiret lexical restent traités comme des unités séparées.
        if not raw or "-" in raw or not all(ch.isalpha() or ch == "'" for ch in raw):
            return ()
        lower = raw.lower()
        direct = self.exceptions.get(lower)
        left = self.left_min if min_left is None else max(1, int(min_left))
        right = self.right_min if min_right is None else max(1, int(min_right))
        if direct is not None:
            return tuple(p for p in direct if p >= left and len(lower) - p >= right)

        decorated = "." + lower + "."
        values = [0] * (len(decorated) + 1)
        for start, ch in enumerate(decorated):
            candidates = self._by_first.get(ch, ())
            for pattern in candidates:
                if decorated.startswith(pattern.letters, start):
                    for offset, weight in enumerate(pattern.weights):
                        index = start + offset
                        if 0 <= index < len(values) and weight > values[index]:
                            values[index] = weight

        result: list[int] = []
        # Position p dans le mot == frontière après decorated[p].
        for p in range(left, len(lower) - right + 1):
            decorated_boundary = p + 1
            if decorated_boundary < len(values) and values[decorated_boundary] % 2 == 1:
                result.append(p)
        return tuple(result)


def _parse_tex_pattern(token: str) -> HyphenationPattern | None:
    token = str(token or "").strip()
    if not token:
        return None
    letters: list[str] = []
    weights: list[int] = [0]
    for ch in token:
        if ch.isdigit():
            weights[-1] = max(weights[-1], int(ch))
        else:
            letters.append(ch.lower())
            weights.append(0)
    value = "".join(letters)
    if not value:
        return None
    return HyphenationPattern(value, tuple(weights))


@lru_cache(maxsize=4)
def load_french_hyphenator(path: str = "") -> FrenchPatternHyphenator:
    candidate = Path(path) if path else project_hyphenation_pattern_path()
    try:
        if candidate.is_file():
            return FrenchPatternHyphenator.from_file(candidate)
    except Exception:
        pass
    return FrenchPatternHyphenator()


def controlled_hyphenation_reason(
    *,
    left: str,
    right: str,
    hyphenator: FrenchPatternHyphenator | None = None,
    min_word_length: int = 7,
    min_left: int = 3,
    min_right: int = 3,
    consecutive_count: int = 1,
    max_consecutive: int = 2,
    near_page_end: bool = False,
    is_last_word: bool = False,
) -> str | None:
    """Retourne `None` si une césure française contrôlée est acceptable."""
    left = _letters_only(left)
    right = _letters_only(right)
    if not left or not right:
        return "La coupure du mot n'a pas pu être vérifiée."
    word = left + right
    if len(word) < int(min_word_length):
        return "Ce mot est trop court pour qu'une césure soit utile."
    if len(left) < int(min_left) or len(right) < int(min_right):
        words = {1: "une", 2: "deux", 3: "trois", 4: "quatre", 5: "cinq"}
        left_label = words.get(int(min_left), str(int(min_left)))
        right_label = words.get(int(min_right), str(int(min_right)))
        return (
            f"Cette césure laisse moins de {left_label} lettres avant ou "
            f"moins de {right_label} lettres après le trait."
        )
    if int(consecutive_count) > max(0, int(max_consecutive)):
        return "Trop de lignes consécutives se terminent par une césure."
    if near_page_end:
        return "La coupure se trouve dans les dernières lignes avant le changement de page."
    if is_last_word and not bool(DEFAULT_CONTROLLED_HYPHENATION["last_word"]):
        return "Le dernier mot du paragraphe ne doit pas être coupé."

    engine = hyphenator or load_french_hyphenator()
    if engine.available:
        positions = engine.positions(word, min_left=min_left, min_right=min_right)
        if len(left) not in positions:
            return "Cette coupure ne correspond pas aux possibilités de césure françaises."
    return None


@dataclass(frozen=True, slots=True)
class ComposedLine:
    text: str
    paragraph_start: bool = False
    paragraph_end: bool = False
    hyphenated: bool = False
    natural_width: float = 0.0
    target_width: float = 0.0
    space_ratio: float = 1.0
    # Décalage de la première ligne d'un paragraphe. Il est exprimé dans la
    # même unité que `target_width` et `measure` (points dans TomeLinea).
    x_offset: float = 0.0


@dataclass(frozen=True, slots=True)
class CompositionResult:
    lines: tuple[ComposedLine, ...]
    hyphenator_available: bool
    unicode_engine_available: bool
    paragraph_count: int = 0


def _paragraphs(value: str) -> tuple[str, ...]:
    text = str(value or "").replace("\r\n", "\n").replace("\r", "\n")
    # Un saut de ligne physique isolé provient souvent de la mise en page
    # source ; un saut vide reste une frontière de paragraphe.
    chunks = re.split(r"\n\s*\n+", text)
    result = []
    for chunk in chunks:
        logical = " ".join(part.strip() for part in chunk.split("\n") if part.strip())
        if logical:
            result.append(logical)
    return tuple(result)


def _uax_words(paragraph: str) -> list[str]:
    units = unicode_line_units(paragraph)
    if not units:
        return []
    # Pour la composition latine, une unité UAX #14 terminée par espace devient
    # un token sans son espace ; NBSP reste dans le token et ne crée pas de
    # frontière.
    words: list[str] = []
    buffer = ""
    for unit in units:
        buffer += unit
        if buffer.endswith(" "):
            value = buffer[:-1]
            if value:
                words.append(value)
            buffer = ""
    if buffer:
        words.append(buffer)
    return words


def compose_text(
    text: str,
    *,
    width: float,
    measure: Callable[[str], float],
    alignment: str = "justify",
    hyphenation: str = "controlled",
    hyphenator: FrenchPatternHyphenator | None = None,
    min_word_length: int = 7,
    min_left: int = 3,
    min_right: int = 3,
    max_consecutive_hyphens: int = 2,
    first_line_indent: float = 0.0,
) -> CompositionResult:
    """Compose des paragraphes en utilisant des métriques réelles.

    L'algorithme optimise les fins de ligne à l'échelle du paragraphe au lieu de
    retenir systématiquement la première coupure possible. Pour le texte
    justifié, le coût pénalise fortement les lignes qui imposeraient des espaces
    trop étirés. Les césures ne sont introduites qu'avec les motifs français
    disponibles et la politique validée par le livre.
    """
    target = max(0.1, float(width))
    engine = hyphenator or load_french_hyphenator()
    lines: list[ComposedLine] = []
    paragraphs = _paragraphs(text)
    for p_index, paragraph in enumerate(paragraphs):
        paragraph_lines = _compose_paragraph(
            paragraph,
            width=target,
            measure=measure,
            alignment=alignment,
            hyphenation=hyphenation,
            hyphenator=engine,
            min_word_length=min_word_length,
            min_left=min_left,
            min_right=min_right,
            max_consecutive_hyphens=max_consecutive_hyphens,
            first_line_indent=max(0.0, float(first_line_indent)),
        )
        if paragraph_lines:
            first = paragraph_lines[0]
            paragraph_lines[0] = ComposedLine(
                text=first.text,
                paragraph_start=True,
                paragraph_end=first.paragraph_end,
                hyphenated=first.hyphenated,
                natural_width=first.natural_width,
                target_width=first.target_width,
                space_ratio=first.space_ratio,
                x_offset=first.x_offset,
            )
            last = paragraph_lines[-1]
            paragraph_lines[-1] = ComposedLine(
                text=last.text,
                paragraph_start=last.paragraph_start,
                paragraph_end=True,
                hyphenated=last.hyphenated,
                natural_width=last.natural_width,
                target_width=last.target_width,
                space_ratio=last.space_ratio,
                x_offset=last.x_offset,
            )
        lines.extend(paragraph_lines)

    return CompositionResult(
        lines=tuple(lines),
        hyphenator_available=engine.available,
        unicode_engine_available=_uax14_line_break_units is not None,
        paragraph_count=len(paragraphs),
    )


def _compose_paragraph(
    paragraph: str,
    *,
    width: float,
    measure: Callable[[str], float],
    alignment: str,
    hyphenation: str,
    hyphenator: FrenchPatternHyphenator,
    min_word_length: int,
    min_left: int,
    min_right: int,
    max_consecutive_hyphens: int,
    first_line_indent: float = 0.0,
) -> list[ComposedLine]:
    words = _uax_words(paragraph)
    if not words:
        return []

    # DP avec état « reste de mot » : contrairement à un simple emballage de
    # mots entiers, les césures françaises font partie des candidats de ligne.
    # Le moteur ne les choisit que si elles améliorent réellement la qualité de
    # justification et respectent la politique générale du livre.
    n = len(words)
    space_width = max(0.001, measure(" "))
    justified = str(alignment).lower() == "justify"
    controlled = str(hyphenation).lower() == "controlled" and hyphenator.available
    max_hyphens = max(0, int(max_consecutive_hyphens))

    indent = max(0.0, min(float(first_line_indent), width * 0.45))

    @lru_cache(maxsize=None)
    def solve(index: int, carry: str, consecutive: int, first_line: bool) -> tuple[float, tuple[ComposedLine, ...]]:
        if index >= n and not carry:
            return 0.0, ()

        line_offset = indent if first_line else 0.0
        line_width = max(0.1, width - line_offset)

        sequence: list[tuple[str, int | None]] = []
        if carry:
            sequence.append((carry, None))
        sequence.extend((words[pos], pos) for pos in range(index, n))

        best_cost = math.inf
        best_lines: tuple[ComposedLine, ...] = ()
        current_tokens: list[str] = []

        for local_pos, (word, original_index) in enumerate(sequence):
            current_tokens.append(word)
            current_text = " ".join(current_tokens)
            natural = measure(current_text)
            if natural > line_width * 1.015:
                current_tokens.pop()
                break

            # Candidat : terminer la ligne après un ou plusieurs mots entiers.
            if original_index is None:
                next_index = index
            else:
                next_index = original_index + 1
            is_last = next_index >= n
            line_cost = _line_cost(
                natural=natural,
                width=line_width,
                spaces=max(0, len(current_tokens) - 1),
                space_width=space_width,
                justified=justified,
                is_last=is_last,
            )
            tail_cost, tail_lines = solve(next_index, "", 0, False)
            total = line_cost + tail_cost
            if total < best_cost:
                best_cost = total
                best_lines = (
                    ComposedLine(
                        text=current_text,
                        paragraph_start=False,
                        paragraph_end=False,
                        hyphenated=False,
                        natural_width=natural,
                        target_width=line_width,
                        space_ratio=_space_ratio(natural, line_width, max(0, len(current_tokens) - 1), space_width),
                        x_offset=line_offset,
                    ),
                ) + tail_lines

            # Candidat : couper le mot courant. On ne coupe jamais un token qui
            # contient ponctuation, espaces insécables ou tiret lexical.
            if not controlled or consecutive >= max_hyphens:
                continue
            if not _hyphenatable_token(word):
                continue
            plain = word.replace("’", "'")
            if len(_letters_only(plain)) < int(min_word_length):
                continue
            positions = hyphenator.positions(plain, min_left=min_left, min_right=min_right)
            if not positions:
                continue
            base_tokens = current_tokens[:-1]
            for pos in reversed(positions):
                left = word[:pos] + "-"
                right = word[pos:]
                line_tokens = base_tokens + [left]
                trial = " ".join(line_tokens)
                trial_width = measure(trial)
                if trial_width > line_width * 1.015:
                    continue
                next_index = index if original_index is None else original_index + 1
                tail_cost, tail_lines = solve(next_index, right, consecutive + 1, False)
                spaces = max(0, len(line_tokens) - 1)
                # Une bonne césure reste légèrement moins souhaitable qu'une
                # ligne équivalente sans césure ; elle devient avantageuse si
                # elle évite une justification trop lâche/serrée.
                hyphen_penalty = 55.0 + 35.0 * consecutive
                line_cost = _line_cost(
                    natural=trial_width,
                    width=line_width,
                    spaces=spaces,
                    space_width=space_width,
                    justified=justified,
                    is_last=False,
                ) + hyphen_penalty
                total = line_cost + tail_cost
                if total < best_cost:
                    best_cost = total
                    best_lines = (
                        ComposedLine(
                            text=trial,
                            paragraph_start=False,
                            paragraph_end=False,
                            hyphenated=True,
                            natural_width=trial_width,
                            target_width=line_width,
                            space_ratio=_space_ratio(trial_width, line_width, spaces, space_width),
                            x_offset=line_offset,
                        ),
                    ) + tail_lines

        return best_cost, best_lines

    _cost, result = solve(0, "", 0, True)
    if result:
        return list(result)
    return _compose_greedy_with_hyphenation(
        words,
        width=width,
        measure=measure,
        alignment=alignment,
        hyphenation=hyphenation,
        hyphenator=hyphenator,
        min_word_length=min_word_length,
        min_left=min_left,
        min_right=min_right,
        max_consecutive_hyphens=max_consecutive_hyphens,
        first_line_indent=indent,
    )


def _hyphenatable_token(value: str) -> bool:
    raw = str(value or "").replace("’", "'")
    return bool(raw) and "-" not in raw and all(ch.isalpha() or ch == "'" for ch in raw)


def _line_cost(
    *,
    natural: float,
    width: float,
    spaces: int,
    space_width: float,
    justified: bool,
    is_last: bool,
) -> float:
    slack = max(0.0, width - natural)
    if is_last:
        # Une dernière ligne courte est normale.
        return (slack / max(width, 0.1)) ** 2 * 12.0
    if not justified:
        return (slack / max(width, 0.1)) ** 2 * 100.0
    if spaces <= 0:
        return 20000.0 + slack
    ratio = _space_ratio(natural, width, spaces, space_width)
    # Zone confortable : 0.85 à 1.65 fois l'espace naturel.
    if 0.85 <= ratio <= 1.65:
        return (ratio - 1.0) ** 2 * 35.0
    distance = min(abs(ratio - 0.85), abs(ratio - 1.65))
    return 1500.0 + distance * distance * 1500.0


def _space_ratio(natural: float, width: float, spaces: int, space_width: float) -> float:
    if spaces <= 0:
        return 1.0
    required_extra = width - natural
    return max(0.0, (space_width + required_extra / spaces) / max(space_width, 0.001))


def _compose_greedy_with_hyphenation(
    words: list[str],
    *,
    width: float,
    measure: Callable[[str], float],
    alignment: str,
    hyphenation: str,
    hyphenator: FrenchPatternHyphenator,
    min_word_length: int,
    min_left: int,
    min_right: int,
    max_consecutive_hyphens: int = 2,
    first_line_indent: float = 0.0,
) -> list[ComposedLine]:
    queue = list(words)
    result: list[ComposedLine] = []
    current = ""
    consecutive = 0
    first_line = True
    indent = max(0.0, min(float(first_line_indent), float(width) * 0.45))

    def current_target() -> tuple[float, float]:
        offset = indent if first_line else 0.0
        return max(0.1, float(width) - offset), offset

    def emit(text: str, *, hyphenated: bool) -> None:
        nonlocal first_line, consecutive
        target_width, offset = current_target()
        natural = measure(text)
        spaces = text.count(" ")
        result.append(ComposedLine(
            text=text,
            paragraph_start=False,
            paragraph_end=False,
            hyphenated=hyphenated,
            natural_width=natural,
            target_width=target_width,
            space_ratio=_space_ratio(natural, target_width, spaces, max(0.001, measure(" "))),
            x_offset=offset,
        ))
        first_line = False
        consecutive = consecutive + 1 if hyphenated else 0

    while queue:
        word = queue.pop(0)
        target_width, _offset = current_target()
        candidate = word if not current else current + " " + word
        if not current or measure(candidate) <= target_width:
            current = candidate
            continue

        did_hyphenate = False
        if str(hyphenation).lower() == "controlled" and hyphenator.available:
            plain = _letters_only(word)
            if len(plain) >= int(min_word_length):
                for pos in reversed(hyphenator.positions(plain, min_left=min_left, min_right=min_right)):
                    left = word[:pos] + "-"
                    trial = left if not current else current + " " + left
                    if measure(trial) <= target_width and consecutive < max(0, int(max_consecutive_hyphens)):
                        emit(trial, hyphenated=True)
                        queue.insert(0, word[pos:])
                        current = ""
                        did_hyphenate = True
                        break
        if did_hyphenate:
            continue

        emit(current, hyphenated=False)
        current = word

    if current:
        target_width, offset = current_target()
        natural = measure(current)
        result.append(ComposedLine(
            text=current, paragraph_start=False, paragraph_end=False, hyphenated=False,
            natural_width=natural, target_width=target_width, space_ratio=1.0, x_offset=offset,
        ))
    return result



@dataclass(frozen=True, slots=True)
class PillowTextMetrics:
    """Métriques FreeType via Pillow, sans dépendance MuPDF.

    Les longueurs sont exposées en points typographiques afin de rester
    compatibles avec les calculs de composition existants.
    """

    font_path: str
    font_size_pt: float
    dpi: int
    font: object
    line_height_pt: float
    ascender_pt: float
    descender_pt: float

    def measure(self, text: str) -> float:
        value = str(text or "")
        try:
            width_px = float(self.font.getlength(value))
        except Exception:
            # Repli Pillow pour les versions où getlength n'est pas disponible.
            box = self.font.getbbox(value)
            width_px = float(max(0, box[2] - box[0]))
        return width_px * 72.0 / float(self.dpi)


def pillow_text_metrics(
    font_path: str | Path,
    font_size_pt: float,
    *,
    dpi: int = 288,
) -> PillowTextMetrics:
    """Charge la police exacte avec FreeType/Pillow et retourne ses métriques.

    Pillow est déjà une dépendance de TomeLinea et utilise FreeType pour les
    polices TrueType/OpenType. Cette fonction remplace l'usage de MuPDF dans
    le nouveau moteur de composition du texte.
    """
    from PIL import ImageFont

    dpi = max(72, int(dpi))
    size_pt = max(0.1, float(font_size_pt))
    size_px = max(1, int(round(size_pt * dpi / 72.0)))
    font = ImageFont.truetype(str(font_path), size=size_px)
    try:
        ascent_px, descent_px = font.getmetrics()
    except Exception:
        ascent_px, descent_px = size_px, max(1, int(round(size_px * 0.2)))
    ascender_pt = float(ascent_px) * 72.0 / dpi
    descender_pt = float(descent_px) * 72.0 / dpi
    # Une ligne de livre a besoin au minimum de l'enveloppe réelle de la police.
    line_height_pt = max(size_pt, ascender_pt + descender_pt)
    return PillowTextMetrics(
        font_path=str(font_path),
        font_size_pt=size_pt,
        dpi=dpi,
        font=font,
        line_height_pt=line_height_pt,
        ascender_pt=ascender_pt,
        descender_pt=descender_pt,
    )


def render_composition_pillow(
    result: CompositionResult,
    *,
    font_path: str | Path,
    font_size_pt: float,
    width_mm: float,
    height_mm: float,
    scale_px_per_mm: float,
    alignment: str = "justify",
    color: tuple[float, float, float] = (0.0, 0.0, 0.0),
    line_pitch_mm: float | None = None,
    paragraph_gap_mm: float = 0.0,
):
    """Rend une composition TomeLinea avec Pillow/FreeType.

    La justification est appliquée uniquement aux lignes qui ne terminent pas
    un paragraphe. Le résultat est une image RGBA directement utilisable par
    l'interface Tk.
    """
    from PIL import Image, ImageDraw, ImageFont

    scale = max(0.25, float(scale_px_per_mm))
    width_px = max(1, int(round(max(0.1, float(width_mm)) * scale)))
    height_px = max(1, int(round(max(0.1, float(height_mm)) * scale)))
    size_px = max(1, int(round(max(0.1, float(font_size_pt)) * 25.4 / 72.0 * scale)))
    font = ImageFont.truetype(str(font_path), size=size_px)
    try:
        ascent_px, descent_px = font.getmetrics()
        natural_line_height_px = max(size_px, int(round(ascent_px + descent_px)))
    except Exception:
        natural_line_height_px = max(1, int(round(size_px * 1.18)))
    requested_pitch_px = (
        float(line_pitch_mm) * scale
        if line_pitch_mm is not None and float(line_pitch_mm) > 0
        else float(natural_line_height_px)
    )
    line_height_px = max(float(natural_line_height_px), requested_pitch_px)
    paragraph_gap_px = max(0.0, float(paragraph_gap_mm or 0.0) * scale)

    rgb = tuple(max(0, min(255, int(round(float(component) * 255)))) for component in color[:3])
    fill = rgb + (255,)
    image = Image.new("RGBA", (width_px, height_px), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    y = 0.0
    justify = str(alignment or "left").lower() == "justify"

    for line in result.lines:
        if y >= height_px:
            break
        text = str(line.text or "")
        words = text.split(" ")
        x_offset_px = max(0.0, float(line.x_offset) * 25.4 / 72.0 * scale)
        available_width_px = max(1.0, width_px - x_offset_px)
        use_justify = justify and not line.paragraph_end and len(words) >= 2
        if use_justify:
            widths = [float(draw.textlength(word, font=font)) for word in words]
            free = max(0.0, available_width_px - sum(widths))
            gap = free / max(1, len(words) - 1)
            x = x_offset_px
            for word, word_width in zip(words, widths):
                draw.text((x, y), word, font=font, fill=fill, anchor="lt")
                x += word_width + gap
        else:
            draw.text((x_offset_px, y), text, font=font, fill=fill, anchor="lt")
        y += line_height_px
        if line.paragraph_end:
            y += paragraph_gap_px
    return image

def line_spacing_issue(line: ComposedLine) -> str | None:
    """Diagnostic lisible d'une ligne justifiée trop serrée / trop lâche."""
    if line.paragraph_end:
        return None
    ratio = float(line.space_ratio)
    if ratio > 1.9:
        return "Cette ligne demanderait des espaces beaucoup trop larges pour être bien justifiée."
    if ratio < 0.72:
        return "Cette ligne demanderait des espaces trop serrés pour être bien justifiée."
    return None

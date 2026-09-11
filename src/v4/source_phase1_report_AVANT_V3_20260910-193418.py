from __future__ import annotations

"""Rapport temporaire de contrôle — TomeLinea V4 Phase 1."""

from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any
import json


def _v(value: Any, empty: str = "—") -> str:
    if value is None or value == "" or value == [] or value == {}:
        return empty
    if isinstance(value, bool):
        return "oui" if value else "non"
    if isinstance(value, float):
        return (f"{value:.4f}").rstrip("0").rstrip(".")
    return str(value)


def _e(value: Any) -> str:
    return escape(_v(value))


def _prop(props: dict[str, Any], *keys: str) -> Any:
    current: Any = props
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def write_phase1_report(
    model: dict[str, Any],
    output_dir: str | Path,
    *,
    basename: str | None = None,
) -> dict[str, str]:
    root = Path(output_dir).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)

    source_name = Path(model.get("source", {}).get("name", "source.docx")).stem
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in source_name).strip("_") or "source"
    base = basename or f"TL_PHASE1_{safe}_{stamp}"

    json_path = root / f"{base}_MODELE.json"
    html_path = root / f"{base}_RAPPORT.html"
    txt_path = root / f"{base}_RESUME.txt"

    json_path.write_text(json.dumps(model, ensure_ascii=False, indent=2), encoding="utf-8")

    doc = model.get("document", {})
    fonts = model.get("fonts", {})
    props = model.get("properties", {})
    ext = props.get("extended", {})
    sections = doc.get("sections", [])
    paragraphs = doc.get("paragraphs", [])
    tables = doc.get("tables", [])
    images = doc.get("images", [])
    warnings = model.get("warnings", [])

    summary_lines = [
        "TomeLinea V4 — CONTROLE PHASE 1 DOCX",
        "=====================================",
        f"Source : {model.get('source', {}).get('name', '')}",
        f"SHA-256 : {model.get('source', {}).get('sha256', '')}",
        f"Paragraphes : {len(paragraphs)}",
        f"Sections : {len(sections)}",
        f"Tableaux : {len(tables)}",
        f"Images placées : {len(images)}",
        f"Sauts de page explicites : {doc.get('explicit_page_break_count', 0)}",
        f"Pages mémorisées par Word (contrôle uniquement) : {_v(ext.get('cached_pages'))}",
        f"Polices utilisées/déclarées : {len(fonts.get('used_families', []))}",
        f"Familles de polices manquantes : {', '.join(fonts.get('missing_families', [])) or 'aucune'}",
        f"Variantes de polices manquantes : {', '.join(fonts.get('missing_faces', [])) or 'aucune'}",
        "",
        "IMPORTANT : aucune règle éditoriale n'a été appliquée et aucune pagination TomeLinea n'a été calculée.",
        f"Rapport détaillé : {html_path}",
        f"Modèle interne : {json_path}",
    ]
    txt_path.write_text("\n".join(summary_lines), encoding="utf-8")

    section_rows = []
    for section in sections:
        p = section.get("properties", {})
        page = p.get("page", {})
        margins = p.get("margins", {})
        section_rows.append(
            "<tr>"
            f"<td>{_e(section.get('section'))}</td>"
            f"<td>{_e(section.get('start_paragraph'))} → {_e(section.get('end_paragraph'))}</td>"
            f"<td>{_e(page.get('width_mm'))} × {_e(page.get('height_mm'))} mm</td>"
            f"<td>{_e(page.get('orientation'))}</td>"
            f"<td>H {_e(margins.get('top_mm'))} / B {_e(margins.get('bottom_mm'))} / G {_e(margins.get('left_mm'))} / D {_e(margins.get('right_mm'))} mm</td>"
            f"<td>{_e(p.get('section_break_type'))}</td>"
            f"<td>{_e((p.get('document_grid') or {}).get('line_pitch_pt'))} pt</td>"
            "</tr>"
        )

    font_rows = []
    for item in fonts.get("face_availability", fonts.get("availability", [])):
        font_rows.append(
            "<tr>"
            f"<td>{_e(item.get('family'))}</td>"
            f"<td>{_e(item.get('style'))}</td>"
            f"<td>{_e(item.get('status'))}</td>"
            f"<td>{_e(item.get('installed_family'))} / {_e(item.get('installed_style'))}</td>"
            f"<td>{_e(item.get('origin'))}</td>"
            "</tr>"
        )

    paragraph_rows = []
    paragraph_details = []
    for para in paragraphs:
        ep = para.get("effective", {})
        spacing = ep.get("spacing", {})
        indent = ep.get("indent", {})
        numbering = ep.get("numbering", {}) or {}
        runs = para.get("runs", [])
        first_run = next((r for r in runs if r.get("text")), runs[0] if runs else {})
        er = first_run.get("effective", {}) if isinstance(first_run, dict) else {}
        text = para.get("text", "").replace("\n", " ↵ ").replace("\t", " ⇥ ")
        if len(text) > 140:
            text = text[:137] + "…"
        paragraph_rows.append(
            "<tr>"
            f"<td>{_e(para.get('paragraph'))}</td>"
            f"<td>{_e(ep.get('style_id'))}</td>"
            f"<td>{escape(text)}</td>"
            f"<td>{_e(ep.get('alignment'))}</td>"
            f"<td>{_e(er.get('resolved_font_family'))}</td>"
            f"<td>{_e(er.get('size_pt'))}</td>"
            f"<td>{_e(spacing.get('before_pt'))} / {_e(spacing.get('after_pt'))}</td>"
            f"<td>{_e(spacing.get('line_multiple') or spacing.get('line_pt'))} ({_e(spacing.get('line_rule'))})</td>"
            f"<td>{_e(indent.get('left_mm'))} / {_e(indent.get('right_mm'))} / {_e(indent.get('first_line_mm'))}</td>"
            f"<td>{_e(numbering.get('num_id'))}:{_e(numbering.get('level'))} {_e(numbering.get('format'))}</td>"
            "</tr>"
        )
        run_rows = []
        for run in runs:
            rer = run.get("effective", {})
            rtext = run.get("text", "").replace("\n", " ↵ ").replace("\t", " ⇥ ")
            run_rows.append(
                "<tr>"
                f"<td>{_e(run.get('run'))}</td>"
                f"<td>{escape(rtext)}</td>"
                f"<td>{_e(rer.get('resolved_font_family'))}</td>"
                f"<td>{_e(rer.get('size_pt'))}</td>"
                f"<td>{_e(rer.get('bold'))}</td>"
                f"<td>{_e(rer.get('italic'))}</td>"
                f"<td>{_e(rer.get('color', {}).get('value') if isinstance(rer.get('color'), dict) else None)}</td>"
                f"<td><code>{escape(json.dumps(run.get('controls', []), ensure_ascii=False))}</code></td>"
                "</tr>"
            )
        paragraph_details.append(
            f"<details><summary>Paragraphe {_e(para.get('paragraph'))} — {escape(text or '(vide)')}</summary>"
            f"<p><b>Chaîne de style :</b> {escape(' → '.join(para.get('paragraph_style_chain', [])) or 'aucune')}</p>"
            f"<p><b>Propriétés directes :</b> <code>{escape(json.dumps(para.get('direct', {}), ensure_ascii=False))}</code></p>"
            f"<p><b>Propriétés effectives :</b> <code>{escape(json.dumps(ep, ensure_ascii=False))}</code></p>"
            "<table><thead><tr><th>Run</th><th>Texte</th><th>Police</th><th>pt</th><th>Gras</th><th>Italique</th><th>Couleur</th><th>Contrôles</th></tr></thead>"
            f"<tbody>{''.join(run_rows)}</tbody></table></details>"
        )

    image_rows = []
    for index, image in enumerate(images, start=1):
        image_rows.append(
            "<tr>"
            f"<td>{index}</td><td>{_e(image.get('paragraph_index'))}</td><td>{_e(image.get('mode'))}</td>"
            f"<td>{_e(image.get('part'))}</td><td>{_e(image.get('width_mm'))} × {_e(image.get('height_mm'))}</td>"
            f"<td>{_e(image.get('wrap'))}</td>"
            "</tr>"
        )

    table_rows = []
    for table in tables:
        table_rows.append(
            "<tr>"
            f"<td>{_e(table.get('table'))}</td><td>{_e(table.get('row_count'))}</td>"
            f"<td>{_e(table.get('style_id'))}</td><td>{_e(table.get('layout'))}</td>"
            f"<td>{_e(table.get('alignment'))}</td>"
            "</tr>"
        )

    special_cases = []
    for para in paragraphs:
        ep = para.get("effective", {})
        controls = [c for r in para.get("runs", []) for c in r.get("controls", [])]
        direct = para.get("direct", {})
        if controls or para.get("run_count") == 0 or (direct and set(direct) != {"style_id"}):
            special_cases.append({
                "paragraph": para.get("paragraph"),
                "direct": direct,
                "controls": controls,
                "run_count": para.get("run_count"),
                "alignment": ep.get("alignment"),
                "first_line_mm": (ep.get("indent") or {}).get("first_line_mm"),
            })
    exercised = {
        "tableaux": bool(tables),
        "images": bool(images),
        "listes": any((p.get("effective", {}).get("numbering") or {}).get("num_id") is not None for p in paragraphs),
        "hyperliens": bool(doc.get("hyperlink_count")),
        "modifications_suivies": any(doc.get("tracked_changes", {}).values()),
        "notes": bool(doc.get("footnotes") or doc.get("endnotes")),
        "controles_de_contenu": bool(doc.get("content_control_count")),
    }
    warning_html = "".join(f"<li>{escape(str(item))}</li>" for item in warnings) or "<li>Aucun avertissement.</li>"
    future = model.get("future_editorial_support", {})
    captured = future.get("captured_for_later", [])
    inventoried = future.get("inventoried_but_not_fully_normalized", [])
    captured_html = "".join(f"<li>{escape(str(item))}</li>" for item in captured)
    inventoried_html = "".join(f"<li>{escape(str(item))}</li>" for item in inventoried)

    html = f"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><title>TomeLinea — Contrôle Phase 1</title>
<style>
body{{font-family:Segoe UI,Arial,sans-serif;margin:28px;line-height:1.4;max-width:1800px}}h1{{margin-bottom:4px}}h2{{margin-top:32px;border-bottom:1px solid #aaa;padding-bottom:5px}}table{{border-collapse:collapse;width:100%;font-size:13px}}th,td{{border:1px solid #bbb;padding:5px 7px;vertical-align:top}}th{{background:#eee;position:sticky;top:0}}code{{white-space:pre-wrap;word-break:break-word;font-size:12px}}details{{margin:8px 0;padding:7px;border:1px solid #bbb}}summary{{cursor:pointer;font-weight:600}}.ok{{padding:10px 14px;border:1px solid #888}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:8px}}.card{{border:1px solid #bbb;padding:10px}}.muted{{color:#555}}
</style></head><body>
<h1>TomeLinea V4 — Rapport de contrôle Phase 1</h1>
<p class="muted">Analyse factuelle DOCX uniquement. Aucun Canvas, aucune pagination TomeLinea, aucune règle éditoriale appliquée.</p>
<div class="grid">
<div class="card"><b>Source</b><br>{_e(model.get('source',{}).get('name'))}</div>
<div class="card"><b>Paragraphes</b><br>{len(paragraphs)}</div>
<div class="card"><b>Sections</b><br>{len(sections)}</div>
<div class="card"><b>Tableaux / images</b><br>{len(tables)} / {len(images)}</div>
<div class="card"><b>Pages mémorisées par Word</b><br>{_e(ext.get('cached_pages'))} <span class="muted">(contrôle seulement)</span></div>
<div class="card"><b>Familles manquantes</b><br>{escape(', '.join(fonts.get('missing_families', [])) or 'aucune')}</div>
<div class="card"><b>Variantes manquantes</b><br>{escape(', '.join(fonts.get('missing_faces', [])) or 'aucune')}</div>
</div>
<h2>Contrat d'unités</h2>
<div class="ok"><code>{escape(json.dumps(model.get('unit_contract',{}), ensure_ascii=False, indent=2))}</code></div>
<h2>Avertissements</h2><ul>{warning_html}</ul>
<h2>Sections, format et marges</h2>
<table><thead><tr><th>Section</th><th>Paragraphes</th><th>Format</th><th>Orientation</th><th>Marges</th><th>Rupture</th><th>Grille ligne</th></tr></thead><tbody>{''.join(section_rows)}</tbody></table>
<h2>Polices — familles et variantes réellement requises</h2>
<table><thead><tr><th>Famille</th><th>Variante</th><th>État</th><th>Police trouvée</th><th>Origine</th></tr></thead><tbody>{''.join(font_rows)}</tbody></table>
<h2>Paragraphes — contrôle synthétique</h2>
<table><thead><tr><th>#</th><th>Style</th><th>Texte</th><th>Align.</th><th>Police</th><th>pt</th><th>Avant/Après pt</th><th>Interligne</th><th>Retraits G/D/1re mm</th><th>Liste</th></tr></thead><tbody>{''.join(paragraph_rows)}</tbody></table>
<h2>Détail des runs</h2>{''.join(paragraph_details)}
<h2>Images placées</h2>
<table><thead><tr><th>#</th><th>Paragraphe</th><th>Mode</th><th>Partie OOXML</th><th>Taille mm</th><th>Habillage</th></tr></thead><tbody>{''.join(image_rows)}</tbody></table>
<h2>Tableaux</h2>
<table><thead><tr><th>#</th><th>Lignes</th><th>Style</th><th>Disposition</th><th>Alignement</th></tr></thead><tbody>{''.join(table_rows)}</tbody></table>
<h2>Cas particuliers détectés dans cette Source</h2>
<pre>{escape(json.dumps(special_cases, ensure_ascii=False, indent=2))}</pre>
<h2>Branches réellement exercées par CE document test</h2>
<pre>{escape(json.dumps(exercised, ensure_ascii=False, indent=2))}</pre>
<p class="muted">« false » signifie seulement que ce livre test ne contient pas ce type d'élément ; ce n'est pas un échec d'analyse.</p>
<h2>Faits normalisés et conservés pour les futures règles éditoriales</h2><ul>{captured_html}</ul>
<h2>Inventorié mais pas encore normalisé en détail</h2><ul>{inventoried_html or '<li>aucun</li>'}</ul>
<h2>Autres contrôles</h2>
<pre>{escape(json.dumps({
    'settings': model.get('settings', {}),
    'tracked_changes': doc.get('tracked_changes', {}),
    'explicit_page_break_count': doc.get('explicit_page_break_count'),
    'last_rendered_page_break_count': doc.get('last_rendered_page_break_count'),
    'tab_count': doc.get('tab_count'),
    'hyperlink_count': doc.get('hyperlink_count'),
    'bookmark_count': doc.get('bookmark_count'),
    'content_control_count': doc.get('content_control_count'),
    'field_instructions': doc.get('field_instructions', []),
    'headers_footers': doc.get('headers_footers', []),
}, ensure_ascii=False, indent=2))}</pre>
<p><b>Modèle interne complet :</b> {escape(json_path.name)}</p>
</body></html>"""
    html_path.write_text(html, encoding="utf-8")

    return {
        "html": str(html_path),
        "json": str(json_path),
        "text": str(txt_path),
    }

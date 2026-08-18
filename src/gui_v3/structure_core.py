from __future__ import annotations

from copy import deepcopy


LEGACY_RULES_KEY = "automatic_follow_rules"
LEGACY_OVERRIDE_KEY = "auto_follow_override"
NEW_RULES_KEY = "page_auto_type_rules"
NEW_AFTER_OVERRIDE_KEY = "page_auto_after_override"


def migrate_structure_data(data: dict | None) -> tuple[dict, bool]:
    """Migre les restes de l'ancien moteur Page auto vers Avant/Après."""
    result = deepcopy(data) if isinstance(data, dict) else {}
    changed = False

    legacy_rules = result.pop(LEGACY_RULES_KEY, None)
    if legacy_rules is not None:
        changed = True

    rules = result.get(NEW_RULES_KEY)
    if not isinstance(rules, dict):
        rules = {}
        result[NEW_RULES_KEY] = rules
        changed = True
    else:
        rules = deepcopy(rules)
        result[NEW_RULES_KEY] = rules

    if isinstance(legacy_rules, dict):
        for source, target in legacy_rules.items():
            source = str(source or "").strip()
            target = str(target or "").strip()
            if not source or not target:
                continue
            entry = dict(rules.get(source, {})) if isinstance(rules.get(source), dict) else {}
            if not str(entry.get("after") or "").strip():
                entry["after"] = target
                rules[source] = entry
                changed = True

    items = result.get("items")
    if isinstance(items, list):
        migrated_items = []
        for raw in items:
            if not isinstance(raw, dict):
                migrated_items.append(raw)
                continue
            item = dict(raw)
            if LEGACY_OVERRIDE_KEY in item:
                if NEW_AFTER_OVERRIDE_KEY not in item:
                    item[NEW_AFTER_OVERRIDE_KEY] = item.get(LEGACY_OVERRIDE_KEY)
                item.pop(LEGACY_OVERRIDE_KEY, None)
                changed = True
            if str(item.get("automatic_kind") or "") == "follow_rule":
                item["automatic_kind"] = "page_auto_after"
                changed = True
            migrated_items.append(item)
        if migrated_items != items:
            result["items"] = migrated_items

    return result, changed


def structure_integrity_issues(data: dict | None) -> list[str]:
    """Contrôles de cohérence indépendants de Tkinter pour les tests Structure."""
    if not isinstance(data, dict):
        return ["structure absente"]

    issues: list[str] = []
    groups = [g for g in data.get("groups", []) if isinstance(g, dict)]
    items = [i for i in data.get("items", []) if isinstance(i, dict)]

    group_ids = [str(g.get("id") or "").strip() for g in groups]
    if any(not gid for gid in group_ids):
        issues.append("partie sans identifiant")
    if len(group_ids) != len(set(group_ids)):
        issues.append("identifiant de partie dupliqué")

    valid_groups = set(group_ids)
    item_ids = [str(i.get("id") or "").strip() for i in items]
    if any(not iid for iid in item_ids):
        issues.append("page sans identifiant")
    if len(item_ids) != len(set(item_ids)):
        issues.append("identifiant de page dupliqué")
    valid_item_ids = set(item_ids)

    for item in items:
        gid = str(item.get("plan_group") or "").strip()
        if gid and gid not in valid_groups:
            issues.append(f"page dans une partie inconnue: {item.get('id')}")
        parent = ""
        for key in ("recto_target_id", "linked_to", "parent_id", "source_page_id"):
            value = str(item.get(key) or "").strip()
            if value:
                parent = value
                break
        if str(item.get("automatic_kind") or "") in {"page_auto_before", "page_auto_after"}:
            if not parent:
                issues.append(f"page auto sans parent: {item.get('id')}")
            elif parent not in valid_item_ids:
                issues.append(f"parent de page auto inconnu: {item.get('id')}")

    if LEGACY_RULES_KEY in data:
        issues.append("ancien moteur automatic_follow_rules encore présent")
    for item in items:
        if LEGACY_OVERRIDE_KEY in item:
            issues.append(f"ancien override encore présent: {item.get('id')}")
        if str(item.get("automatic_kind") or "") == "follow_rule":
            issues.append(f"ancienne page follow_rule encore présente: {item.get('id')}")

    rules = data.get(NEW_RULES_KEY, {})
    if not isinstance(rules, dict):
        issues.append("page_auto_type_rules invalide")
    else:
        for source, entry in rules.items():
            if not str(source or "").strip():
                issues.append("règle Page auto sans type source")
            if not isinstance(entry, dict):
                issues.append(f"règle Page auto invalide: {source}")
                continue
            extra = set(entry) - {"before", "after"}
            if extra:
                issues.append(f"position Page auto inconnue pour {source}: {sorted(extra)}")

    return issues

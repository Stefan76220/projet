from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.v4 import editorial_persistence as v4
from tomelinea import persistence as v5


class V5PersistenceEquivalenceTests(unittest.TestCase):
    def test_public_v5_api_uses_frozen_v4_engine(self) -> None:
        self.assertEqual(v5.EDITORIAL_STATE_SCHEMA, v4.SCHEMA)
        self.assertIs(v5.source_fingerprint, v4.source_fingerprint)
        self.assertIs(v5.decision_key, v4.decision_key)
        self.assertIs(v5.load_decision_state, v4.load_editorial_state)
        self.assertIs(v5.save_decision_state, v4.save_editorial_state)
        self.assertIs(v5.record_choice, v4.record_editorial_choice)
        self.assertIs(v5.choices_for_plan, v4.persisted_choices_for_plan)

    def test_decision_key_uses_stable_id(self) -> None:
        event = {
            "domain": "page",
            "stable_id": "page-stable-42",
            "choice": "conserver",
        }
        self.assertEqual(
            v5.decision_key(event),
            "page:page-stable-42",
        )

    def test_table_decision_key_preserves_segment_and_table_id(self) -> None:
        event = {
            "domain": "table",
            "tableId": "table-stable-7",
            "segment": "debut",
            "choice": "page_suivante",
        }
        self.assertEqual(
            v5.decision_key(event),
            "table:debut:table-stable-7",
        )

    def test_record_and_reload_choice_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.docx"
            state_path = root / "state" / "editorial.json"
            source.write_bytes(b"TomeLinea source stable")

            event = {
                "domain": "page",
                "stable_id": "page-abc",
                "choice": "recto",
            }

            written = v5.record_choice(
                state_path,
                source,
                event,
            )

            loaded = v5.load_decision_state(
                state_path,
                source,
            )

            self.assertEqual(written, loaded)
            self.assertEqual(
                loaded["decisions"]["page:page-abc"]["choice"],
                "recto",
            )

            choices = v5.choices_for_plan(loaded)
            self.assertEqual(len(choices), 1)
            self.assertEqual(
                choices[0]["key"],
                "page:page-abc",
            )

    def test_source_change_invalidates_old_decisions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.docx"
            state_path = root / "editorial.json"

            source.write_bytes(b"version 1")

            v5.record_choice(
                state_path,
                source,
                {
                    "domain": "page",
                    "stable_id": "page-1",
                    "choice": "conserver",
                },
            )

            source.write_bytes(b"version 2")

            reloaded = v5.load_decision_state(
                state_path,
                source,
            )

            self.assertEqual(reloaded["decisions"], {})
            self.assertEqual(
                reloaded["source_fingerprint"],
                v5.source_fingerprint(source),
            )


if __name__ == "__main__":
    unittest.main()
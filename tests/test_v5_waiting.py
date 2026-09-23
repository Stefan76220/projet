from __future__ import annotations

import unittest

from src.gui_v4 import startup_runtime as v4_wait
from tomelinea.app import (
    FINISH_TAIL_MS,
    TARGET_CYCLE_MS,
    WAIT_HEIGHT,
    WAIT_LABELS,
    WAIT_WIDTH,
    WaitPhase,
    WaitSession,
    start_wait,
    wait_asset,
)


class FakeAnimation:
    def __init__(self) -> None:
        self.finish_calls = []

    def finish_after_cycle(self, *, pump=None, timeout=15.0) -> None:
        self.finish_calls.append(
            {
                "pump": pump,
                "timeout": timeout,
            }
        )


class V5WaitingTests(unittest.TestCase):
    def test_wait_visual_reuses_validated_v4_contract(self) -> None:
        self.assertEqual(WAIT_WIDTH, v4_wait.WAIT_WIDTH)
        self.assertEqual(WAIT_HEIGHT, v4_wait.WAIT_HEIGHT)
        self.assertEqual(TARGET_CYCLE_MS, v4_wait.TARGET_CYCLE_MS)
        self.assertEqual(FINISH_TAIL_MS, v4_wait.FINISH_TAIL_MS)
        self.assertEqual(wait_asset(), v4_wait.WAIT_MEDIA)
        self.assertTrue(wait_asset().is_file())

    def test_real_phase_labels_have_no_fake_percentage(self) -> None:
        labels = tuple(WAIT_LABELS.values())

        self.assertIn("Import de la Source", labels)
        self.assertIn("Analyse de la Source", labels)
        self.assertIn("Recomposition du Livre", labels)

        for label in labels:
            self.assertNotIn("%", label)
            self.assertNotIn("100", label)

    def test_start_wait_uses_injected_async_engine(self) -> None:
        fake = FakeAnimation()

        session = start_wait(
            WaitPhase.ANALYZE_SOURCE,
            "Structure, polices et ancrages",
            starter=lambda: fake,
        )

        self.assertIs(session.controller, fake)
        self.assertEqual(session.phase, WaitPhase.ANALYZE_SOURCE)
        self.assertEqual(session.label, "Analyse de la Source")
        self.assertEqual(session.detail, "Structure, polices et ancrages")
        self.assertFalse(session.finished)

    def test_phase_can_change_without_restarting_animation(self) -> None:
        fake = FakeAnimation()

        session = WaitSession(
            fake,
            WaitPhase.IMPORT_SOURCE,
        )

        before = session.controller

        snapshot = session.set_phase(
            WaitPhase.PREPARE_COMPOSITION,
            "Pagination des unités",
        )

        self.assertIs(session.controller, before)
        self.assertEqual(snapshot.phase, WaitPhase.PREPARE_COMPOSITION)
        self.assertEqual(snapshot.label, "Préparation de la Composition")
        self.assertEqual(snapshot.detail, "Pagination des unités")

    def test_finish_delegates_to_v4_end_of_cycle_once(self) -> None:
        fake = FakeAnimation()
        session = WaitSession(
            fake,
            WaitPhase.RECOMPOSE_BOOK,
        )

        marker = lambda: None

        session.finish(
            pump=marker,
            timeout=3.5,
        )
        session.finish(
            pump=None,
            timeout=99,
        )

        self.assertTrue(session.finished)
        self.assertEqual(len(fake.finish_calls), 1)
        self.assertIs(fake.finish_calls[0]["pump"], marker)
        self.assertEqual(fake.finish_calls[0]["timeout"], 3.5)

    def test_snapshot_contains_only_real_state_not_progress(self) -> None:
        fake = FakeAnimation()
        session = WaitSession(
            fake,
            WaitPhase.OPEN_PROJECT,
            "Lecture et reconstruction",
        )

        snapshot = session.snapshot

        self.assertEqual(snapshot.label, "Ouverture du projet")
        self.assertFalse(snapshot.finished)
        self.assertFalse(hasattr(snapshot, "percent"))
        self.assertFalse(hasattr(snapshot, "progress"))


if __name__ == "__main__":
    unittest.main()
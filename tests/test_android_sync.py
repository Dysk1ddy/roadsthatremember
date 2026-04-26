from __future__ import annotations

from pathlib import Path
import shutil
import unittest
import uuid

from tools.sync_android_port import apply_drift, compare_trees


class AndroidSyncTests(unittest.TestCase):
    def make_workspace_root(self) -> Path:
        root = Path.cwd() / "tests_output" / f"android_sync_{uuid.uuid4().hex}"
        root.mkdir(parents=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root

    def test_compare_trees_reports_changed_missing_and_stale_files(self) -> None:
        root = self.make_workspace_root()
        source_root = root / "dnd_game"
        target_root = root / "android_port" / "dnd_game"
        source_root.mkdir(parents=True)
        target_root.mkdir(parents=True)
        (source_root / "models.py").write_text("desktop model\n", encoding="utf-8")
        (target_root / "models.py").write_text("android model\n", encoding="utf-8")
        (source_root / "new_scene.py").write_text("new scene\n", encoding="utf-8")
        (target_root / "old_scene.py").write_text("old scene\n", encoding="utf-8")
        ignored_dir = source_root / "__pycache__"
        ignored_dir.mkdir()
        (ignored_dir / "ignored.pyc").write_bytes(b"cache")

        drift = compare_trees(source_root, target_root)

        self.assertEqual(
            {(item.kind, item.label) for item in drift},
            {
                ("changed", "models.py"),
                ("missing", "new_scene.py"),
                ("stale", "old_scene.py"),
            },
        )

    def test_apply_drift_copies_changed_and_missing_files(self) -> None:
        root = self.make_workspace_root()
        source_root = root / "dnd_game"
        target_root = root / "android_port" / "dnd_game"
        source_root.mkdir(parents=True)
        target_root.mkdir(parents=True)
        (source_root / "models.py").write_text("desktop model\n", encoding="utf-8")
        (target_root / "models.py").write_text("android model\n", encoding="utf-8")
        (source_root / "new_scene.py").write_text("new scene\n", encoding="utf-8")
        (target_root / "old_scene.py").write_text("old scene\n", encoding="utf-8")

        applied = apply_drift(compare_trees(source_root, target_root))

        self.assertEqual({item.kind for item in applied}, {"changed", "missing"})
        self.assertEqual((target_root / "models.py").read_text(encoding="utf-8"), "desktop model\n")
        self.assertEqual((target_root / "new_scene.py").read_text(encoding="utf-8"), "new scene\n")
        self.assertTrue((target_root / "old_scene.py").exists())


if __name__ == "__main__":
    unittest.main()

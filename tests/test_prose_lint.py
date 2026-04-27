from __future__ import annotations

from pathlib import Path
import unittest

from tools.prose_lint import lint_python_file, lint_text


class ProseLintTests(unittest.TestCase):
    def test_lint_text_catches_style_phrases_and_legacy_terms(self) -> None:
        findings = lint_text(
            "It is not a town, it is a ledger with walls.\nNeverwinter sends a clerk.\n",
            path=Path("sample.md"),
        )
        codes = [finding.code for finding in findings]

        self.assertIn("STYLE001", codes)
        self.assertIn("LEGACY001", codes)
        self.assertTrue(any("Neverwinter" in finding.message for finding in findings))

    def test_lint_text_honors_allow_directive(self) -> None:
        findings = lint_text(
            "Neverwinter appears in a retcon note. <!-- prose-lint: allow -->\n",
            path=Path("sample.md"),
        )

        self.assertEqual(findings, [])

    def test_lint_python_file_scans_public_strings_and_skips_internal_tokens(self) -> None:
        path = Path.cwd() / "tests_output" / "prose_lint_sample.py"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            'SCENE_KEY = "greywake_briefing"\n'
            'PUBLIC_LINE = "Phandalin keeps its gate shut."\n',
            encoding="utf-8",
        )
        try:
            findings = lint_python_file(path, checks=("legacy",))
        finally:
            path.unlink(missing_ok=True)

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].code, "LEGACY001")
        self.assertIn("Phandalin", findings[0].message)


if __name__ == "__main__":
    unittest.main()

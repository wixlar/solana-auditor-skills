"""Offline, dependency-free checks for the published Solana Auditor skill bundle."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "solana-auditor"


class BundleIntegrityTests(unittest.TestCase):
    def test_required_files(self):
        for path in [
            ROOT / "LICENSE",
            ROOT / "README.md",
            ROOT / "SECURITY.md",
            SKILL / "SKILL.md",
            SKILL / "references" / "judging.md",
            SKILL / "references" / "report-formatting.md",
            SKILL / "references" / "hacking-agents" / "shared-rules.md",
        ]:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertTrue(path.is_file())

    def test_specialist_and_attack_vector_coverage(self):
        agents = list((SKILL / "references" / "hacking-agents").glob("*-agent.md"))
        vectors = sorted((SKILL / "references" / "attack-vectors").glob("attack-vectors-*.md"))
        self.assertEqual(len(agents), 9)  # 8 regular specialists + optional protocol specialist
        self.assertEqual(len(vectors), 5)
        count = sum(len(re.findall(r"^## ", path.read_text(), re.M)) for path in vectors)
        self.assertEqual(count, 105)

    def test_version_consistency(self):
        package = (ROOT / "VERSION").read_text().strip()
        skill = (SKILL / "VERSION").read_text().strip()
        self.assertRegex(package, r"^[0-9]+$")
        self.assertEqual(package, skill)

    def test_published_identity_and_attribution(self):
        readme = (ROOT / "README.md").read_text()
        skill = (SKILL / "SKILL.md").read_text()
        self.assertIn("https://github.com/wixlar/solana-auditor-skills", readme)
        self.assertIn("https://github.com/wixlar/solana-auditor-skills", skill)
        self.assertIn("https://github.com/wixlar", (ROOT / "SECURITY.md").read_text())
        self.assertIn("pashov/skills", readme)
        self.assertIn("sanbir/solana-auditor-skills", readme)
        self.assertIn("MIT License", (ROOT / "LICENSE").read_text())

    def test_local_markdown_links_resolve(self):
        for document in ROOT.rglob("*.md"):
            content = document.read_text()
            for target in re.findall(r"(?<!!)\[[^\]]*\]\(([^)]+)\)", content):
                destination = target.split("#", 1)[0]
                if not destination or destination.startswith(("http:", "https:", "mailto:", "/")):
                    continue
                with self.subTest(document=document.relative_to(ROOT), link=target):
                    self.assertTrue((document.parent / destination).exists())


if __name__ == "__main__":
    unittest.main()

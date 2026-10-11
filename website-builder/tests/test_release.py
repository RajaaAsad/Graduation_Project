"""Publication checks catch staged and historical files, not only working copies."""

import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.check_release import check_release, inspect_content


class ReleaseTests(unittest.TestCase):
    def test_manual_upload_check_includes_local_secrets_and_caches(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / ".env").write_text("OPENAI_API_KEY=local-example\n")
            cache = root / ".ruff_cache"
            cache.mkdir()
            (cache / "CACHEDIR.TAG").write_text("cache")
            self.assertFalse(check_release(root))
            issues = check_release(root, all_files=True)
            self.assertTrue(any("Private configuration:" in issue for issue in issues))
            self.assertTrue(any("generated artifact:" in issue for issue in issues))

    def test_credentials_are_detected_without_echoing_the_value(self):
        credential = b"sk-" + b"a" * 32
        issues = inspect_content("app.py", credential)
        self.assertTrue(issues)
        self.assertNotIn(credential.decode(), "\n".join(issues))

    def test_private_artifacts_are_detected(self):
        for name in (
            ".env",
            "__pycache__/app.pyc",
            "model.safetensors",
            "data.xlsx",
            "output/index.html",
        ):
            self.assertTrue(inspect_content(name, b"example"))
        self.assertFalse(inspect_content(".env.example", b"OPENAI_API_KEY=your-example"))

    def test_staged_secret_is_found_when_working_copy_is_clean(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            subprocess.run(["git", "init", str(root)], check=True, capture_output=True)
            (root / "app.py").write_bytes(b"sk-" + b"a" * 32)
            subprocess.run(
                ["git", "-C", str(root), "add", "app.py"], check=True, capture_output=True
            )
            (root / "app.py").write_text("safe = True\n")
            issues = check_release(root)
            self.assertTrue(any("INDEX:" in issue for issue in issues))

    def test_deleted_secret_remains_detectable_in_history(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            git = ["git", "-C", str(root)]
            subprocess.run(git + ["init"], check=True, capture_output=True)
            (root / "app.py").write_bytes(b"sk-" + b"a" * 32)
            subprocess.run(git + ["add", "."], check=True, capture_output=True)
            subprocess.run(
                git
                + [
                    "-c",
                    "user.name=Test",
                    "-c",
                    "user.email=test@example.com",
                    "commit",
                    "-m",
                    "test",
                ],
                check=True,
                capture_output=True,
            )
            (root / "app.py").write_text("safe = True\n")
            subprocess.run(git + ["add", "."], check=True, capture_output=True)
            self.assertTrue(any("HISTORY:" in issue for issue in check_release(root)))

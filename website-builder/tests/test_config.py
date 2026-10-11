"""Environment precedence and working-directory independence."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from website_builder.config import PROJECT_ROOT, load_settings


class ConfigTests(unittest.TestCase):
    def test_environment_overrides_dotenv(self):
        with tempfile.TemporaryDirectory() as folder:
            env = Path(folder) / ".env"
            env.write_text(
                'OPENAI_API_KEY="local-key"\nOPENAI_MODEL=example-model\n', encoding="utf-8"
            )
            with patch.dict(os.environ, {"OPENAI_API_KEY": "environment-key"}, clear=True):
                settings = load_settings(env)
            self.assertEqual(settings.api_key, "environment-key")
            self.assertEqual(settings.model, "example-model")

    def test_placeholder_and_relative_path(self):
        with patch.dict(
            os.environ,
            {"OPENAI_API_KEY": "your-example", "INTENT_MODEL_PATH": "models/custom"},
            clear=True,
        ):
            settings = load_settings(PROJECT_ROOT / "nonexistent.env")
        self.assertFalse(settings.api_key)
        self.assertEqual(settings.intent_model_path, (PROJECT_ROOT / "models/custom").resolve())

"""Real Streamlit session tests with API responses mocked."""

import os
import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from website_builder.config import Settings
from website_builder.interview import Interview

APP = Path(__file__).resolve().parent.parent / "app.py"
HTML = "<html><head><title>Test</title></head><body><h1>Welcome</h1></body></html>"


class AppTests(unittest.TestCase):
    def test_every_page_can_complete_through_the_interface_without_credentials(self):
        from website_builder.interview import PAGE_TYPES

        with patch.dict(os.environ, {"OPENAI_API_KEY": "", "USE_ML_CLASSIFIERS": "false"}):
            for page_type in PAGE_TYPES:
                with self.subTest(page_type=page_type):
                    app = AppTest.from_file(str(APP)).run(timeout=20)
                    next(
                        button for button in app.button if button.label == PAGE_TYPES[page_type]
                    ).click().run()
                    while not app.session_state["interview"].complete:
                        step = app.session_state["interview"].current
                        answer = (
                            step.candidate_labels[0]
                            if step.candidate_labels
                            else "Example design detail"
                        )
                        app.chat_input[0].set_value(answer).run()
                        self.assertFalse(app.exception)
                    generate = next(
                        button for button in app.button if button.label == "Generate design"
                    )
                    self.assertTrue(generate.disabled)

    def test_startup_without_api_key_or_model_download(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "", "USE_ML_CLASSIFIERS": "false"}):
            app = AppTest.from_file(str(APP)).run(timeout=20)
            self.assertFalse(app.exception)
            self.assertTrue(app.chat_input[0].disabled)
            next(button for button in app.button if button.label == "Landing page").click().run()
            self.assertFalse(app.exception)
            self.assertEqual(app.session_state["interview"].page_type, "landing")
            app.chat_input[0].set_value("A neighborhood bookshop").run()
            self.assertEqual(len(app.session_state["interview"].answers), 1)

    def test_generation_failure_preserves_previous_design(self):
        with patch("website_builder.config.load_settings", return_value=Settings(api_key="test")):
            app = AppTest.from_file(str(APP)).run(timeout=20)
            interview = Interview("landing", index=25)
            app.session_state["interview"] = interview
            app.session_state["generated_html"] = HTML
            app.run()
            with patch(
                "website_builder.generation.generate_html", side_effect=RuntimeError("Retry later")
            ):
                next(
                    button for button in app.button if button.label == "Regenerate design"
                ).click().run()
            self.assertFalse(app.exception)
            self.assertEqual(app.session_state["generated_html"], HTML)
            self.assertTrue(app.error)

    def test_generation_and_new_design_reset(self):
        with patch("website_builder.config.load_settings", return_value=Settings(api_key="test")):
            app = AppTest.from_file(str(APP)).run(timeout=20)
            app.session_state["interview"] = Interview("landing", index=25)
            app.run()
            with patch("website_builder.generation.generate_html", return_value=HTML):
                next(
                    button for button in app.button if button.label == "Generate design"
                ).click().run()
            self.assertFalse(app.exception)
            self.assertEqual(app.session_state["generated_html"], HTML)
            next(
                button for button in app.button if button.label == "Start a new design"
            ).click().run()
            self.assertEqual(app.session_state["generated_html"], "")
            self.assertNotIn("interview", app.session_state)
            self.assertEqual(len(app.button), 8)

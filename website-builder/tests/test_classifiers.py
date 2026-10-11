"""Optional model routing with mocked inference; no model downloads."""

import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from website_builder.classifiers import _intent_pipeline, classify_answer
from website_builder.config import Settings


class ClassifierTests(unittest.TestCase):
    def test_intent_label_mapping_matches_trained_output(self):
        inference = Mock(return_value=[{"label": "LABEL_6", "score": 0.99}])
        with patch("website_builder.classifiers._intent_pipeline", return_value=inference):
            answer = classify_answer("a blue shade", "intent", [], Settings(use_ml=True))
        self.assertEqual(answer, "blue")
        inference.assert_called_once_with("a blue shade", truncation=True)

    def test_optional_zero_shot_routes_nonliteral_choices(self):
        inference = Mock(return_value={"labels": ["yes", "no"]})
        with patch("website_builder.classifiers._zero_shot_pipeline", return_value=inference):
            answer = classify_answer(
                "I would love that", "choice", ["yes", "no"], Settings(use_ml=True)
            )
        self.assertEqual(answer, "yes")

    def test_literal_choices_do_not_download_models(self):
        with patch("website_builder.classifiers._zero_shot_pipeline") as load:
            self.assertEqual(
                classify_answer("YES!", "choice", ["yes", "no"], Settings(use_ml=True)), "yes"
            )
        load.assert_not_called()

    def test_missing_weights_report_setup_error(self):
        with self.assertRaisesRegex(RuntimeError, "Local classifier not found"):
            _intent_pipeline(Path("nonexistent-model-folder"))

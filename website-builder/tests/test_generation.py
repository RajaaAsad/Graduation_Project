"""HTML handling and API contract tests; no paid requests."""

import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from website_builder.config import Settings
from website_builder.generation import generate_html, validate_html

HTML = (
    "<!doctype html><html><head><title>Example</title></head><body><h1>Welcome</h1></body></html>"
)


class GenerationTests(unittest.TestCase):
    def test_raw_and_fenced_html(self):
        for reply in (HTML, f"```html\n{HTML}\n```", f"```\n{HTML}\n```"):
            self.assertEqual(validate_html(reply), HTML)

    def test_partial_empty_and_active_html_are_rejected(self):
        fragments = [
            "",
            "Here is your code",
            "<script>alert(1)</script>",
            '<img src="javascript:alert(1)">',
            '<img src="https://example.com/a" onerror="alert(1)">',
            '<form action="https://example.com/collect">',
            '<iframe src="https://example.com">',
            '<meta http-equiv="refresh" content="0; url=https://example.com">',
            '<a href="java&#x09;script:alert(1)">Click</a>',
            '<link href="https://example.com/a.css">',
        ]
        for fragment in fragments:
            with self.subTest(fragment=fragment), self.assertRaises(ValueError):
                validate_html(
                    fragment
                    if not fragment.startswith("<")
                    else HTML.replace("<h1>Welcome</h1>", fragment)
                )

    def test_missing_document_sections_are_rejected(self):
        with self.assertRaises(ValueError):
            validate_html("<html><body>Incomplete</body></html>")

    def test_missing_key_never_calls_api(self):
        client = Mock()
        with self.assertRaises(RuntimeError):
            generate_html("brief", Settings(), client=client)
        client.responses.create.assert_not_called()

    def test_api_contract_and_edit_context(self):
        client = Mock()
        client.responses.create.return_value = SimpleNamespace(status="completed", output_text=HTML)
        code = generate_html(
            "brief", Settings(api_key="test"), existing_html=HTML, edit="Use blue", client=client
        )
        self.assertEqual(code, HTML)
        kwargs = client.responses.create.call_args.kwargs
        self.assertFalse(kwargs["store"])
        self.assertIn("Use blue", kwargs["input"])
        self.assertIn(HTML, kwargs["input"])
        self.assertEqual(kwargs["model"], Settings().model)

    def test_truncated_generation_is_not_accepted(self):
        client = Mock()
        client.responses.create.return_value = SimpleNamespace(
            status="incomplete", output_text=HTML
        )
        with self.assertRaises(ValueError):
            generate_html("brief", Settings(api_key="test"), client=client)

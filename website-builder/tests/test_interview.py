"""Branch and state regression tests for the eight supported interviews."""

import unittest

from website_builder.classifiers import AnswerError, classify_answer
from website_builder.config import Settings
from website_builder.interview import PAGE_TYPES, Interview, load_flows


class InterviewTests(unittest.TestCase):
    def test_every_flow_completes_on_both_branch_variants(self):
        for page_type in PAGE_TYPES:
            for prefer_last in (False, True):
                with self.subTest(page_type=page_type, prefer_last=prefer_last):
                    interview = Interview(page_type)
                    visited = []
                    while not interview.complete:
                        visited.append(interview.index)
                        step = interview.current
                        answer = (
                            step.candidate_labels[-1 if prefer_last else 0]
                            if step.candidate_labels
                            else "Example design detail"
                        )
                        interview.answer(answer, Settings())
                        self.assertLessEqual(len(visited), len(interview.steps))
                    self.assertEqual(len(visited), len(set(visited)))
                    self.assertIn("requirements", interview.design_brief())
                    self.assertEqual(interview.index, len(interview.steps))

    def test_color_skips_image_and_image_skips_color(self):
        for answer, expected in [("color", 1), ("image", 2)]:
            interview = Interview("signin")
            interview.answer(answer, Settings())
            self.assertEqual(interview.index, expected)
            interview.answer(
                "https://example.com/image.jpg" if answer == "image" else "blue", Settings()
            )
            self.assertEqual(interview.index, 3)

    def test_blog_contact_form_is_skipped_when_declined(self):
        interview = Interview("blog", index=15)
        interview.answer("no", Settings())
        self.assertEqual(interview.index, 17)
        interview = Interview("blog", index=15)
        interview.answer("yes", Settings())
        self.assertEqual(interview.index, 16)

    def test_unknown_choice_preserves_state(self):
        interview = Interview("signin")
        with self.assertRaises(AnswerError):
            interview.answer("maybe", Settings())
        self.assertEqual(interview.index, 0)
        self.assertEqual(interview.answers, [])

    def test_numeric_choices_are_strings(self):
        interview = Interview("landing", index=17)
        self.assertEqual(interview.answer("3", Settings()), "3")

    def test_free_text_no_is_preserved(self):
        self.assertEqual(
            classify_answer("No nonsense design", "text", [], Settings()), "No nonsense design"
        )

    def test_sessions_do_not_share_answers(self):
        first, second = Interview("signin"), Interview("signin")
        first.answer("color", Settings())
        self.assertEqual(second.answers, [])
        self.assertEqual(second.index, 0)

    def test_incomplete_brief_and_invalid_type_are_rejected(self):
        with self.assertRaises(ValueError):
            Interview("unknown")
        with self.assertRaises(ValueError):
            Interview("landing").design_brief()

    def test_all_flows_are_loaded(self):
        self.assertEqual(sum(len(flow) for flow in load_flows().values()), 177)

import unittest
from unittest.mock import patch

import app as app_module
from app import clean_feedback, count_keywords


class HelperTests(unittest.TestCase):
    def test_clean_feedback(self):
        self.assertEqual(clean_feedback("  GREAT Service!!!  "), "great service")

    def test_count_keywords_ignores_common_words(self):
        self.assertEqual(
            count_keywords(["The delivery was late", "delivery was slow"]),
            [{"word": "delivery", "count": 2}, {"word": "late", "count": 1},
             {"word": "slow", "count": 1}]
        )


class ApiTests(unittest.TestCase):
    def setUp(self):
        app_module.app.config["TESTING"] = True
        self.client = app_module.app.test_client()

    def test_post_feedback_requires_text(self):
        response = self.client.post("/feedback", json={"customer_feedback": " "})
        self.assertEqual(response.status_code, 400)

    def test_post_feedback_cleans_text_before_saving(self):
        response = self.client.post(
            "/feedback", json={"customer_feedback": "  Doesn't work!!!  "}
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["customer_feedback"], "doesn t work")
        self.assertEqual(response.json["category"], "Negative")

    def test_post_feedback_rejects_text_that_cleans_to_empty(self):
        response = self.client.post("/feedback", json={"customer_feedback": "!!!"})

        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()

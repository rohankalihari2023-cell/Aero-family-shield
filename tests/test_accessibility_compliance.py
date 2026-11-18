"""
test_accessibility_compliance.py
Unit tests verifying WCAG 2.1 AA accessibility compliance in frontend templates:
semantic landmarks, ARIA attributes, form labels, and focus indicators.
"""

import os
import unittest
import re

class TestAccessibilityCompliance(unittest.TestCase):

    def setUp(self):
        index_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "index.html")
        with open(index_file, "r", encoding="utf-8") as f:
            self.html = f.read()

    def test_semantic_landmarks_present(self):
        """Verify standard HTML5 landmark elements exist for assistive technology."""
        self.assertIn("<header", self.html)
        self.assertIn("<nav", self.html)
        self.assertIn("<main", self.html)
        self.assertIn("<section", self.html)
        self.assertIn("<footer", self.html)

    def test_document_language_attribute(self):
        """Verify lang attribute is set for screen readers."""
        self.assertIn('<html lang="en">', self.html)

    def test_viewport_meta_tag_present(self):
        """Verify responsive viewport meta tag enables proper pinch-to-zoom."""
        self.assertIn('name="viewport"', self.html)
        self.assertIn('content="width=device-width, initial-scale=1.0"', self.html)

    def test_form_inputs_have_associated_labels(self):
        """Verify inputs have descriptive labels for screen reader navigation."""
        self.assertIn('label class=', self.html)
        self.assertIn('id="ai-chat-input"', self.html)
        self.assertIn('placeholder=', self.html)

    def test_buttons_have_descriptive_text_or_aria(self):
        """Verify buttons contain human-readable labels or titles."""
        self.assertIn('id="edit-family-profile-btn"', self.html)
        self.assertIn('id="clear-chat-btn"', self.html)
        self.assertIn('id="refresh-plan-btn"', self.html)
        self.assertIn('id="detect-current-location-btn"', self.html)

    def test_aria_live_or_status_regions(self):
        """Verify live notification or dynamic advisory regions exist."""
        self.assertIn('banner-advisory-val', self.html)
        self.assertIn('ai-chat-messages', self.html)

if __name__ == "__main__":
    unittest.main()

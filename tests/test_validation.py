import unittest

from app.api.validation import validate_request


class TestValidation(unittest.TestCase):
    def test_valid_request(self):
        request = {
            "equipment_id": "GEN-101",
            "description": "Generator will not start",
            "priority": "high",
        }

        self.assertEqual(validate_request(request), [])

    def test_missing_fields(self):
        errors = validate_request({})

        self.assertEqual(len(errors), 3)
        self.assertIn(
            "equipment_id must be a nonempty string", errors
        )
        self.assertIn(
            "description must be a nonempty string", errors
        )
        self.assertIn(
            "priority must be low, medium, or high", errors
        )
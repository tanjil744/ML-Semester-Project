import copy
import json
import os
import tempfile
import unittest

# Support running both as:
#   python -m pytest Inspection/test_inspector.py   (from project root)
#   python Inspection/test_inspector.py             (from project root)
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Inspection.inspector import inspect_package, load_packing_list


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_detection(class_name, confidence=0.95, bbox=None):
    """Return a well-formed detection dict."""
    return {
        "class_name": class_name,
        "confidence": confidence,
        "bbox": bbox if bbox is not None else [0, 0, 50, 60],
    }


def correct_package():
    """Two pencils, one eraser, one ruler — the exact expected contents."""
    return [
        make_detection("pencil"),
        make_detection("pencil"),
        make_detection("eraser"),
        make_detection("ruler"),
    ]


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------

class TestCorrectPackage(unittest.TestCase):

    def test_status_is_correct(self):
        result = inspect_package(correct_package())
        self.assertEqual(result["status"], "correct")

    def test_is_correct_flag_is_true(self):
        self.assertTrue(inspect_package(correct_package())["is_correct"])

    def test_no_error_messages(self):
        self.assertEqual(inspect_package(correct_package())["error_messages"], [])

    def test_no_unexpected_items(self):
        self.assertEqual(inspect_package(correct_package())["unexpected_items"], {})

    def test_detected_counts_match_expected(self):
        result = inspect_package(correct_package())
        self.assertEqual(result["detected_counts"], result["expected_counts"])

    def test_message_says_correct(self):
        self.assertIn("Correct", inspect_package(correct_package())["message"])

    def test_skipped_is_zero(self):
        self.assertEqual(inspect_package(correct_package())["skipped_low_confidence"], 0)


# ---------------------------------------------------------------------------
# Missing-item tests
# ---------------------------------------------------------------------------

class TestMissingItems(unittest.TestCase):

    def test_one_pencil_missing(self):
        detections = [make_detection("pencil"), make_detection("eraser"),
                      make_detection("ruler")]
        result = inspect_package(detections)
        self.assertEqual(result["status"], "incorrect")
        self.assertIn("1 pencil missing", result["error_messages"])

    def test_both_pencils_missing(self):
        detections = [make_detection("eraser"), make_detection("ruler")]
        result = inspect_package(detections)
        self.assertIn("2 pencils missing", result["error_messages"])

    def test_eraser_missing(self):
        detections = [make_detection("pencil"), make_detection("pencil"),
                      make_detection("ruler")]
        result = inspect_package(detections)
        self.assertIn("1 eraser missing", result["error_messages"])

    def test_ruler_missing(self):
        detections = [make_detection("pencil"), make_detection("pencil"),
                      make_detection("eraser")]
        result = inspect_package(detections)
        self.assertIn("1 ruler missing", result["error_messages"])

    def test_multiple_items_missing(self):
        result = inspect_package([])           # nothing detected
        errors = result["error_messages"]
        self.assertGreaterEqual(len(errors), 3)  # pencil(s), eraser, ruler

    def test_message_contains_incorrect(self):
        detections = [make_detection("pencil"), make_detection("eraser"),
                      make_detection("ruler")]
        self.assertIn("Incorrect", inspect_package(detections)["message"])


# ---------------------------------------------------------------------------
# Extra-item tests
# ---------------------------------------------------------------------------

class TestExtraItems(unittest.TestCase):

    def test_extra_pencil(self):
        detections = correct_package() + [make_detection("pencil")]
        result = inspect_package(detections)
        self.assertIn("1 extra pencil", result["error_messages"])

    def test_two_extra_pencils(self):
        detections = correct_package() + [make_detection("pencil"),
                                          make_detection("pencil")]
        result = inspect_package(detections)
        self.assertIn("2 extra pencils", result["error_messages"])

    def test_extra_eraser(self):
        detections = correct_package() + [make_detection("eraser")]
        result = inspect_package(detections)
        self.assertIn("1 extra eraser", result["error_messages"])

    def test_extra_ruler(self):
        detections = correct_package() + [make_detection("ruler")]
        result = inspect_package(detections)
        self.assertIn("1 extra ruler", result["error_messages"])

    def test_status_is_incorrect_for_extra(self):
        detections = correct_package() + [make_detection("ruler")]
        self.assertEqual(inspect_package(detections)["status"], "incorrect")


# ---------------------------------------------------------------------------
# Mixed missing + extra
# ---------------------------------------------------------------------------

class TestMixedErrors(unittest.TestCase):

    def test_missing_pencil_and_extra_eraser(self):
        detections = [
            make_detection("pencil"),               # one pencil instead of two
            make_detection("eraser"),
            make_detection("eraser"),               # extra eraser
            make_detection("ruler"),
        ]
        result = inspect_package(detections)
        errors = result["error_messages"]
        self.assertIn("1 pencil missing", errors)
        self.assertIn("1 extra eraser", errors)
        self.assertEqual(len(errors), 2)

    def test_multiple_mixed_errors(self):
        detections = [make_detection("eraser"), make_detection("ruler"),
                      make_detection("ruler")]
        result = inspect_package(detections)
        errors = result["error_messages"]
        # 2 pencils missing  +  1 extra ruler
        self.assertIn("2 pencils missing", errors)
        self.assertIn("1 extra ruler", errors)


# ---------------------------------------------------------------------------
# Empty and minimal detections
# ---------------------------------------------------------------------------

class TestEmptyDetections(unittest.TestCase):

    def test_empty_list_is_incorrect(self):
        result = inspect_package([])
        self.assertEqual(result["status"], "incorrect")

    def test_all_counts_zero(self):
        result = inspect_package([])
        for count in result["detected_counts"].values():
            self.assertEqual(count, 0)

    def test_expected_counts_keys_present(self):
        result = inspect_package([])
        self.assertIn("pencil", result["expected_counts"])
        self.assertIn("eraser", result["expected_counts"])
        self.assertIn("ruler",  result["expected_counts"])


# ---------------------------------------------------------------------------
# Confidence-threshold tests
# ---------------------------------------------------------------------------

class TestConfidenceThreshold(unittest.TestCase):

    def test_low_confidence_detection_is_skipped(self):
        detections = [
            make_detection("pencil", confidence=0.20),   # below 0.50
            make_detection("pencil"),
            make_detection("eraser"),
            make_detection("ruler"),
        ]
        result = inspect_package(detections)
        self.assertEqual(result["detected_counts"]["pencil"], 1)
        self.assertEqual(result["skipped_low_confidence"], 1)

    def test_exactly_at_threshold_is_accepted(self):
        detections = [
            make_detection("pencil", confidence=0.50),
            make_detection("pencil"),
            make_detection("eraser"),
            make_detection("ruler"),
        ]
        self.assertTrue(inspect_package(detections)["is_correct"])

    def test_custom_threshold_filters_correctly(self):
        detections = [
            make_detection("pencil", confidence=0.70),
            make_detection("pencil", confidence=0.70),
            make_detection("eraser"),
            make_detection("ruler"),
        ]
        # With threshold 0.80 both pencils are skipped
        result = inspect_package(detections, confidence_threshold=0.80)
        self.assertEqual(result["detected_counts"]["pencil"], 0)
        self.assertEqual(result["skipped_low_confidence"], 2)

    def test_threshold_zero_accepts_all(self):
        detections = [make_detection("pencil", confidence=0.01),
                      make_detection("pencil", confidence=0.01),
                      make_detection("eraser",  confidence=0.01),
                      make_detection("ruler",   confidence=0.01)]
        self.assertTrue(inspect_package(detections, 0.0)["is_correct"])

    def test_threshold_one_skips_non_perfect(self):
        result = inspect_package(correct_package(), confidence_threshold=1.0)
        # 0.95 < 1.0 → all skipped
        self.assertEqual(result["skipped_low_confidence"], 4)
        self.assertEqual(result["status"], "incorrect")


# ---------------------------------------------------------------------------
# Unexpected-item tests
# ---------------------------------------------------------------------------

class TestUnexpectedItems(unittest.TestCase):

    def test_single_unexpected_item(self):
        detections = correct_package() + [make_detection("scissors")]
        result = inspect_package(detections)
        self.assertFalse(result["is_correct"])
        self.assertEqual(result["unexpected_items"], {"scissors": 1})
        self.assertIn("1 unexpected scissors", result["error_messages"])

    def test_multiple_unexpected_items(self):
        detections = correct_package() + [
            make_detection("scissors"),
            make_detection("scissors"),
            make_detection("tape"),
        ]
        result = inspect_package(detections)
        self.assertEqual(result["unexpected_items"]["scissors"], 2)
        self.assertEqual(result["unexpected_items"]["tape"], 1)

    def test_unexpected_item_message_is_correct(self):
        detections = correct_package() + [make_detection("tape"),
                                          make_detection("tape")]
        result = inspect_package(detections)
        self.assertIn("2 unexpected tapes", result["error_messages"])


# ---------------------------------------------------------------------------
# Input-mutation guard
# ---------------------------------------------------------------------------

class TestInputNotMutated(unittest.TestCase):

    def test_detections_list_unchanged(self):
        detections = correct_package()
        original = copy.deepcopy(detections)
        inspect_package(detections)
        self.assertEqual(detections, original)


# ---------------------------------------------------------------------------
# Custom packing list path
# ---------------------------------------------------------------------------

class TestCustomPackingList(unittest.TestCase):

    def test_custom_list_single_item(self):
        custom = {"pencil": 3}
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as fh:
            json.dump(custom, fh)
            tmp_path = fh.name

        try:
            detections = [make_detection("pencil")] * 3
            result = inspect_package(detections, packing_list_path=tmp_path)
            self.assertTrue(result["is_correct"])
        finally:
            os.unlink(tmp_path)

    def test_missing_packing_list_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            inspect_package([], packing_list_path="/nonexistent/path.json")


# ---------------------------------------------------------------------------
# Validation / error-path tests
# ---------------------------------------------------------------------------

class TestValidationErrors(unittest.TestCase):

    def test_detections_not_a_list(self):
        with self.assertRaises(ValueError):
            inspect_package("pen")

    def test_detections_is_dict(self):
        with self.assertRaises(ValueError):
            inspect_package({"class_name": "pencil"})

    def test_confidence_threshold_too_high(self):
        with self.assertRaises(ValueError):
            inspect_package([], confidence_threshold=1.5)

    def test_confidence_threshold_negative(self):
        with self.assertRaises(ValueError):
            inspect_package([], confidence_threshold=-0.1)

    def test_confidence_threshold_is_bool(self):
        with self.assertRaises(ValueError):
            inspect_package([], confidence_threshold=True)

    def test_detection_not_a_dict(self):
        with self.assertRaises(ValueError):
            inspect_package(["pencil"])

    def test_missing_class_name_key(self):
        with self.assertRaises(ValueError):
            inspect_package([{"confidence": 0.9, "bbox": [0, 0, 10, 20]}])

    def test_empty_class_name(self):
        with self.assertRaises(ValueError):
            inspect_package([{"class_name": "", "confidence": 0.9,
                              "bbox": [0, 0, 10, 20]}])

    def test_confidence_out_of_range(self):
        with self.assertRaises(ValueError):
            inspect_package([make_detection("pencil", confidence=1.5)])

    def test_confidence_is_bool(self):
        d = make_detection("pencil")
        d["confidence"] = True        # bool is a subclass of int — must reject
        with self.assertRaises(ValueError):
            inspect_package([d])

    def test_bbox_wrong_length(self):
        d = make_detection("pencil")
        d["bbox"] = [0, 0, 10]       # only 3 values
        with self.assertRaises(ValueError):
            inspect_package([d])

    def test_bbox_inverted_x(self):
        d = make_detection("pencil")
        d["bbox"] = [50, 0, 10, 20]  # x2 < x1
        with self.assertRaises(ValueError):
            inspect_package([d])

    def test_bbox_inverted_y(self):
        d = make_detection("pencil")
        d["bbox"] = [0, 50, 10, 20]  # y2 < y1
        with self.assertRaises(ValueError):
            inspect_package([d])

    def test_bbox_equal_x(self):
        d = make_detection("pencil")
        d["bbox"] = [10, 0, 10, 20]  # x1 == x2 → zero width
        with self.assertRaises(ValueError):
            inspect_package([d])

    def test_bbox_contains_string(self):
        d = make_detection("pencil")
        d["bbox"] = [0, 0, "ten", 20]
        with self.assertRaises(ValueError):
            inspect_package([d])

    def test_bbox_contains_bool(self):
        d = make_detection("pencil")
        d["bbox"] = [0, 0, True, 20]  # bool in coords
        with self.assertRaises(ValueError):
            inspect_package([d])


# ---------------------------------------------------------------------------
# load_packing_list() direct tests
# ---------------------------------------------------------------------------

class TestLoadPackingList(unittest.TestCase):

    def test_returns_dict(self):
        result = load_packing_list()
        self.assertIsInstance(result, dict)

    def test_contains_expected_keys(self):
        result = load_packing_list()
        for key in ("pencil", "eraser", "ruler"):
            self.assertIn(key, result)

    def test_all_values_are_positive_ints(self):
        for qty in load_packing_list().values():
            self.assertIsInstance(qty, int)
            self.assertGreater(qty, 0)

    def test_bad_json_raises(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as fh:
            fh.write("[1, 2, 3]")    # a list, not a dict
            tmp_path = fh.name
        try:
            with self.assertRaises(ValueError):
                load_packing_list(tmp_path)
        finally:
            os.unlink(tmp_path)

    def test_negative_quantity_raises(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as fh:
            json.dump({"pencil": -1}, fh)
            tmp_path = fh.name
        try:
            with self.assertRaises(ValueError):
                load_packing_list(tmp_path)
        finally:
            os.unlink(tmp_path)

    def test_bool_quantity_raises(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as fh:
            json.dump({"pencil": True}, fh)
            tmp_path = fh.name
        try:
            with self.assertRaises(ValueError):
                load_packing_list(tmp_path)
        finally:
            os.unlink(tmp_path)


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main(verbosity=2)
"""
demo.py — Example outputs for the Packing Inspection Logic (Part 3)
====================================================================
Runs four representative scenarios using simulated model detections
so that Part 3 can be demonstrated independently of a trained model.

Run from the project root:

    python Inspection/demo.py
"""

import sys
import os

# Allow running from the project root as  python Inspection/demo.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Inspection.inspector import inspect_package


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def make_detection(class_name, confidence=0.92, x1=10, y1=10, x2=120, y2=200):
    """Build a minimal but valid detection dict."""
    return {
        "class_name": class_name,
        "confidence": confidence,
        "bbox": [x1, y1, x2, y2],
    }


def print_report(title, result):
    """Pretty-print one inspection result."""
    width = 60
    bar = "─" * width

    print(f"\n┌{bar}┐")
    print(f"│  Scenario : {title:<{width - 14}}│")
    print(f"├{bar}┤")

    exp = result["expected_counts"]
    det = result["detected_counts"]
    unx = result["unexpected_items"]
    skp = result["skipped_low_confidence"]

    # Build count table
    all_items = sorted(set(list(exp) + list(det) + list(unx)))
    print(f"│  {'Item':<20} {'Expected':>8}  {'Detected':>8}           │")
    print(f"│  {'----':<20} {'--------':>8}  {'--------':>8}           │")
    for item in all_items:
        e = exp.get(item, "—")
        d = det.get(item, unx.get(item, 0))
        marker = "  ✓" if e == d else "  ✗"
        if item in unx:
            marker = "  ?"
        print(f"│  {item:<20} {str(e):>8}  {str(d):>8} {marker}        │")

    if skp:
        print(f"│  (skipped {skp} low-confidence detection(s))              │")

    print(f"├{bar}┤")
    status_icon = "✅" if result["is_correct"] else "❌"
    print(f"│  {status_icon}  {result['message']:<{width - 5}}│")
    print(f"└{bar}┘")


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------

SCENARIOS = [
    (
        "Scenario 1 — Correct package",
        [
            make_detection("pencil"),
            make_detection("pencil"),
            make_detection("eraser"),
            make_detection("ruler"),
        ],
    ),
    (
        "Scenario 2 — One pencil missing",
        [
            make_detection("pencil"),        # only one
            make_detection("eraser"),
            make_detection("ruler"),
        ],
    ),
    (
        "Scenario 3 — Extra ruler added",
        [
            make_detection("pencil"),
            make_detection("pencil"),
            make_detection("eraser"),
            make_detection("ruler"),
            make_detection("ruler"),         # extra ruler
        ],
    ),
    (
        "Scenario 4 — Mixed: pencil missing + extra eraser",
        [
            make_detection("pencil"),        # one pencil instead of two
            make_detection("eraser"),
            make_detection("eraser"),        # extra eraser
            make_detection("ruler"),
        ],
    ),
    (
        "Scenario 5 — Unexpected item (scissors) in package",
        [
            make_detection("pencil"),
            make_detection("pencil"),
            make_detection("eraser"),
            make_detection("ruler"),
            make_detection("scissors"),      # not in packing list
        ],
    ),
    (
        "Scenario 6 — Low-confidence detections filtered out",
        [
            make_detection("pencil", confidence=0.90),
            make_detection("pencil", confidence=0.30),   # below 0.50 → skipped
            make_detection("eraser", confidence=0.85),
            make_detection("ruler",  confidence=0.20),   # below 0.50 → skipped
        ],
    ),
    (
        "Scenario 7 — Empty package (nothing detected)",
        [],
    ),
]


def main():
    print("\n" + "=" * 62)
    print("  PACKING INSPECTION — EXAMPLE OUTPUTS  (Part 3 Demo)")
    print("=" * 62)

    for title, detections in SCENARIOS:
        result = inspect_package(detections)
        print_report(title, result)

    print("\nDemo complete.\n")


if __name__ == "__main__":
    main()

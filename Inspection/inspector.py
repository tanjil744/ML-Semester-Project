import json
from pathlib import Path


# ---------------------------------------------------------------------------
# Location of the configurable packing list
# ---------------------------------------------------------------------------
_PACKING_LIST_FILE = Path(__file__).with_name("packing_list.json")

# Default confidence threshold — detections below this are ignored
DEFAULT_CONFIDENCE_THRESHOLD = 0.50


# ---------------------------------------------------------------------------
# Public helper: load and validate packing_list.json
# ---------------------------------------------------------------------------

def load_packing_list(filepath=None):
    """Load the expected item counts from a JSON file.

    Parameters
    ----------
    filepath : str or Path, optional
        Path to a packing list JSON file.  Defaults to the
        ``packing_list.json`` that lives next to this module.

    Returns
    -------
    dict[str, int]
        Mapping of item name → expected count (all values ≥ 0).

    Raises
    ------
    FileNotFoundError
        If the JSON file does not exist.
    ValueError
        If the file content is not a valid packing list.
    """
    path = Path(filepath) if filepath else _PACKING_LIST_FILE

    if not path.is_file():
        raise FileNotFoundError(
            f"Packing list not found: {path}\n"
            "Create a packing_list.json next to inspector.py, e.g.:\n"
            '  {"pencil": 2, "eraser": 1, "ruler": 1}'
        )

    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    if not isinstance(data, dict) or not data:
        raise ValueError(
            "packing_list.json must be a non-empty JSON object, e.g. "
            '{"pencil": 2, "eraser": 1, "ruler": 1}'
        )

    for name, qty in data.items():
        if not isinstance(name, str) or not name.strip():
            raise ValueError(
                f"Item names must be non-empty strings; got: {name!r}"
            )
        if type(qty) is not int or qty < 0:
            # type() used deliberately — bool is a subclass of int
            raise ValueError(
                f"Quantity for '{name}' must be a non-negative integer; "
                f"got: {qty!r}"
            )

    return dict(data)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _validate_detection(detection):
    """Raise ValueError if a single detection dict is malformed."""
    if not isinstance(detection, dict):
        raise ValueError(
            f"Each detection must be a dict; got {type(detection).__name__}."
        )

    # --- class_name ---
    name = detection.get("class_name")
    if not isinstance(name, str) or not name.strip():
        raise ValueError(
            "Every detection must have a non-empty string 'class_name'. "
            f"Got: {name!r}"
        )

    # --- confidence ---
    conf = detection.get("confidence")
    if (
        not isinstance(conf, (int, float))
        or isinstance(conf, bool)
        or not (0.0 <= conf <= 1.0)
    ):
        raise ValueError(
            f"'confidence' for '{name}' must be a float in [0, 1]; "
            f"got: {conf!r}"
        )

    # --- bbox ---
    bbox = detection.get("bbox")
    if (
        not isinstance(bbox, (list, tuple))
        or len(bbox) != 4
        or any(
            not isinstance(v, (int, float)) or isinstance(v, bool)
            for v in bbox
        )
        or bbox[2] <= bbox[0]
        or bbox[3] <= bbox[1]
    ):
        raise ValueError(
            f"'bbox' for '{name}' must be [x1, y1, x2, y2] with "
            f"x2 > x1 and y2 > y1; got: {bbox!r}"
        )


def _pluralise(count, singular):
    """Return 'singular' or 'singulars' depending on count."""
    return singular if count == 1 else singular + "s"


def _build_error_messages(expected, detected, unexpected):
    """Produce a list of human-readable error strings."""
    errors = []

    for item in sorted(expected):
        exp = expected[item]
        det = detected.get(item, 0)
        diff = exp - det

        if diff > 0:
            errors.append(f"{diff} {_pluralise(diff, item)} missing")
        elif diff < 0:
            extra = -diff
            errors.append(f"{extra} extra {_pluralise(extra, item)}")

    for item in sorted(unexpected):
        count = unexpected[item]
        errors.append(f"{count} unexpected {_pluralise(count, item)}")

    return errors


# ---------------------------------------------------------------------------
# Main public function
# ---------------------------------------------------------------------------

def inspect_package(detections, confidence_threshold=DEFAULT_CONFIDENCE_THRESHOLD,
                    packing_list_path=None):
    """Check a list of model detections against the expected packing list.

    This is the single function the application calls.

    Parameters
    ----------
    detections : list[dict]
        Raw output from the object-detection model.  Each element must be a
        dict with keys ``class_name`` (str), ``confidence`` (float 0–1), and
        ``bbox`` ([x1, y1, x2, y2]).
    confidence_threshold : float, optional
        Detections whose confidence is strictly below this value are ignored.
        Must be in [0, 1].  Default is 0.50.
    packing_list_path : str or Path, optional
        Override the default ``packing_list.json`` location.  Useful for
        testing with a custom list.

    Returns
    -------
    dict
        A structured inspection report (see module docstring for fields).

    Raises
    ------
    ValueError
        If ``detections`` is not a list, ``confidence_threshold`` is out of
        range, or any individual detection is malformed.
    FileNotFoundError
        If the packing list file cannot be found.
    """
    # ---- validate top-level inputs ----------------------------------------
    if not isinstance(detections, list):
        raise ValueError(
            f"'detections' must be a list; got {type(detections).__name__}."
        )

    if (
        not isinstance(confidence_threshold, (int, float))
        or isinstance(confidence_threshold, bool)
        or not (0.0 <= confidence_threshold <= 1.0)
    ):
        raise ValueError(
            f"'confidence_threshold' must be a float in [0, 1]; "
            f"got: {confidence_threshold!r}"
        )

    # ---- load packing list ------------------------------------------------
    expected_counts = load_packing_list(packing_list_path)

    # ---- count detections -------------------------------------------------
    detected_counts = {item: 0 for item in expected_counts}
    unexpected_items = {}   # items seen but not in the packing list
    skipped_count = 0       # detections below the confidence threshold

    for detection in detections:
        _validate_detection(detection)

        item = detection["class_name"].strip()
        conf = detection["confidence"]

        if conf < confidence_threshold:
            skipped_count += 1
            continue

        if item in detected_counts:
            detected_counts[item] += 1
        else:
            unexpected_items[item] = unexpected_items.get(item, 0) + 1

    # ---- compare and build report -----------------------------------------
    error_messages = _build_error_messages(
        expected_counts, detected_counts, unexpected_items
    )

    if error_messages:
        status = "incorrect"
        message = "Incorrect package: " + "; ".join(error_messages) + "."
    else:
        status = "correct"
        message = "Correct package: all required items are present."

    return {
        "status":                  status,
        "is_correct":              not error_messages,
        "expected_counts":         expected_counts,
        "detected_counts":         detected_counts,
        "unexpected_items":        unexpected_items,
        "error_messages":          error_messages,
        "message":                 message,
        "skipped_low_confidence":  skipped_count,
    }

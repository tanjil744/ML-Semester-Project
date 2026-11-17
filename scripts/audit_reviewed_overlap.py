"""Read-only cross-split image screening for an extracted YOLO dataset.

Requires Pillow. Compares 64-bit difference hashes across train/valid/test,
including rotations and reflections. Candidates require visual review.
Writes one JSON report outside the dataset; never edits images or labels.
"""

import argparse
import hashlib
import itertools
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

try:
    from PIL import Image, __version__ as PILLOW_VERSION
except ImportError:
    raise SystemExit("Pillow is missing. Install it with: py -m pip install Pillow")

SPLITS = ("train", "valid", "test")
EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
TRANSFORMS = (
    ("identity", None),
    ("flip_left_right", Image.Transpose.FLIP_LEFT_RIGHT),
    ("flip_top_bottom", Image.Transpose.FLIP_TOP_BOTTOM),
    ("rotate_90", Image.Transpose.ROTATE_90),
    ("rotate_180", Image.Transpose.ROTATE_180),
    ("rotate_270", Image.Transpose.ROTATE_270),
    ("transpose", Image.Transpose.TRANSPOSE),
    ("transverse", Image.Transpose.TRANSVERSE),
)


def file_hash(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def difference_hash(gray):
    pixels = gray.resize((9, 8), Image.Resampling.LANCZOS).tobytes()
    value = 0
    for y in range(8):
        for x in range(8):
            value = (value << 1) | int(pixels[y * 9 + x] > pixels[y * 9 + x + 1])
    return value


def source_key(path):
    # This catches export spelling variants, but is only a filename heuristic.
    prefix = Path(path).name.split(".rf.")[0]
    return re.sub(r"(?:_jpg|_png|\.jpg|\.png)$", "", prefix, flags=re.I)


def reviewed_group_checks(root, records):
    log = root / "split_corrections.json"
    if not log.is_file():
        return {"available": False, "note": "No split_corrections.json found."}
    try:
        data = json.loads(log.read_text(encoding="utf-8-sig"))
        by_path = {record["path"]: record for record in records}
        checks = []
        for group in data["groups"]:
            expected = [group["target_split"] + "/images/" + Path(member["path"]).name
                        for member in group["members"]]
            problems = []
            for member, relative in zip(group["members"], expected):
                actual = by_path.get(relative)
                if actual is None:
                    problems.append("Missing or undecodable: " + relative)
                elif actual["sha256"] != member["sha256"]:
                    problems.append("Content differs: " + relative)
            keys = set(group["family_keys"])
            unexpected = [record["path"] for record in records
                          if source_key(record["path"]) in keys
                          and record["path"] not in expected]
            problems.extend("Unreviewed family member: " + name for name in unexpected)
            checks.append({"pair": group["pair"], "target_split": group["target_split"],
                           "expected_members": len(expected), "passed": not problems,
                           "problems": problems})
        return {"available": True, "groups": checks,
                "all_passed": bool(checks) and all(check["passed"] for check in checks)}
    except (OSError, UnicodeError, ValueError, KeyError, TypeError) as error:
        return {"available": True, "all_passed": False, "error": str(error)}


def audit(root, threshold=4):
    counts = {}
    records, errors = [], []
    for split in SPLITS:
        folder = root / split / "images"
        if not folder.is_dir():
            raise ValueError(f"Missing image folder: {folder}")
        images = sorted(path for path in folder.iterdir()
                        if path.is_file() and path.suffix.lower() in EXTENSIONS)
        if not images:
            raise ValueError(f"No images found in: {folder}")
        counts[split] = len(images)
        print(f"Reading {split}: {len(images)} images", flush=True)
        for index, path in enumerate(images, 1):
            relative = path.relative_to(root).as_posix()
            try:
                sha256 = file_hash(path)
                with Image.open(path) as image:
                    image.load()
                    width, height = image.size
                    gray = image.convert("L")
                    hashes = [difference_hash(gray if operation is None else gray.transpose(operation))
                              for _, operation in TRANSFORMS]
                records.append({"path": relative, "split": split, "sha256": sha256,
                                "width": width, "height": height, "hashes": hashes})
            except (OSError, ValueError, Image.DecompressionBombError) as error:
                errors.append({"path": relative, "error": str(error)})
            if index % 250 == 0:
                print(f"  Read {index}/{len(images)}", flush=True)

    by_split = {split: [record for record in records if record["split"] == split]
                for split in SPLITS}
    exact, filenames = defaultdict(list), defaultdict(list)
    for record in records:
        exact[record["sha256"]].append(record)
        filenames[source_key(record["path"])].append(record)
    exact_groups = [{"sha256": key, "files": [r["path"] for r in members]}
                    for key, members in sorted(exact.items())
                    if len({r["split"] for r in members}) > 1]
    filename_groups = [{"normalized_prefix": key, "files": [r["path"] for r in members]}
                       for key, members in sorted(filenames.items())
                       if len({r["split"] for r in members}) > 1]

    candidates = []
    compared = 0
    for left_split, right_split in itertools.combinations(SPLITS, 2):
        print(f"Comparing {left_split} vs {right_split}...", flush=True)
        for left in by_split[left_split]:
            left_hash = left["hashes"][0]
            for right in by_split[right_split]:
                compared += 1
                distances = [(left_hash ^ value).bit_count() for value in right["hashes"]]
                distance = min(distances)
                if distance <= threshold:
                    best = distances.index(distance)
                    candidates.append({"left": left["path"], "right": right["path"],
                                       "distance": distance,
                                       "right_transform": TRANSFORMS[best][0],
                                       "byte_identical": left["sha256"] == right["sha256"]})
    candidates.sort(key=lambda pair: (pair["distance"], pair["left"], pair["right"]))
    for index, pair in enumerate(candidates, 1):
        pair["candidate_id"] = index
    inventory = [{key: record[key] for key in ("path", "sha256", "width", "height")}
                 for record in records]
    return {
        "schema_version": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "dataset": str(root), "pillow_version": PILLOW_VERSION,
        "method": {"hash": "64-bit horizontal difference hash",
                   "grayscale_resize": "9x8, LANCZOS", "threshold": threshold,
                   "right_image_transforms": [name for name, _ in TRANSFORMS],
                   "comparison": "Left base hash versus eight transformed hashes of right; each cross-split pair once."},
        "split_image_counts": counts, "decoded_images": len(records), "decode_errors": errors,
        "cross_split_pairs_compared": compared,
        "exact_cross_split_duplicate_groups": exact_groups,
        "normalized_filename_cross_split_groups": filename_groups,
        "perceptual_candidate_count": len(candidates), "perceptual_candidates": candidates,
        "reviewed_source_groups": reviewed_group_checks(root, records),
        "images": inventory,
        "limitations": [
            "Perceptual matches are screening candidates, not automatically confirmed duplicates.",
            "Similar layouts can produce false positives; related captures can be missed.",
            "Arbitrary cropping and source reuse within mosaics are not comprehensively detected.",
            "Filename normalization is heuristic and does not establish provenance.",
            "Pillow versions and resampling can affect borderline distances.",
            "Labels, visual annotation accuracy, and model performance are not checked.",
            "A zero-candidate result would not prove complete split independence.",
        ],
        "credit": "Stationery v7 by Lalaworkspace, CC BY 4.0.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path, help="Extracted dataset root containing train/valid/test")
    parser.add_argument("--output", type=Path, default=Path("split_overlap_results.json"))
    parser.add_argument("--threshold", type=int, default=4)
    args = parser.parse_args()
    root, output = args.dataset.resolve(), args.output.resolve()
    if not 0 <= args.threshold <= 64:
        parser.error("threshold must be between 0 and 64")
    if not root.is_dir():
        parser.error("dataset folder does not exist")
    if output.is_relative_to(root):
        parser.error("write the report outside the dataset folder")
    if output.suffix.lower() != ".json":
        parser.error("output filename must end in .json")
    if output.exists():
        parser.error("report already exists; choose a new --output filename")
    if not output.parent.is_dir():
        parser.error("output parent directory does not exist")
    try:
        report = audit(root, args.threshold)
        with output.open("x", encoding="utf-8") as stream:
            json.dump(report, stream, indent=2)
            stream.write("\n")
    except (OSError, ValueError) as error:
        parser.exit(1, f"Stopped: {error}\n")
    print("\nSPLIT OVERLAP SCREENING")
    print(f"Decoded images: {report['decoded_images']}")
    print(f"Decode errors: {len(report['decode_errors'])}")
    print(f"Cross-split image pairs compared: {report['cross_split_pairs_compared']}")
    print(f"Byte-identical cross-split groups: {len(report['exact_cross_split_duplicate_groups'])}")
    print(f"Normalized filename cross-split groups: {len(report['normalized_filename_cross_split_groups'])}")
    print(f"Perceptual candidate pairs: {report['perceptual_candidate_count']}")
    checks = report["reviewed_source_groups"]
    if checks.get("available"):
        passed = sum(group["passed"] for group in checks.get("groups", []))
        print(f"Previously reviewed groups passing: {passed}/{len(checks.get('groups', []))}")
    print(f"JSON report saved: {output}")
    print("Candidates require visual review. No images or labels were changed.")
    if report["decode_errors"] or (checks.get("available") and not checks.get("all_passed")):
        parser.exit(2, "Some images or reviewed groups could not be verified; inspect the JSON report.\n")


if __name__ == "__main__":
    main()

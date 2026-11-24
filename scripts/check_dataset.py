"""Check a downloaded YOLO dataset using Python's standard library."""

import argparse
import hashlib
import math
from collections import Counter, defaultdict
from pathlib import Path

CLASSES = {
    0: "eraser",
    1: "pencil",
    2: "pencil sharpener",
    3: "ruler",
}
SPLITS = ("train", "valid", "test")
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def file_hash(path):
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_dataset(root):
    issues = []
    hashes = defaultdict(list)
    print("DATASET CHECK")
    print("Expected classes:", CLASSES)
    print("")

    for split in SPLITS:
        image_dir = root / split / "images"
        label_dir = root / split / "labels"

        if not image_dir.is_dir() or not label_dir.is_dir():
            issues.append(f"{split}: missing images or labels folder")
            continue

        images = sorted(
            path for path in image_dir.iterdir()
            if path.is_file()
            and path.suffix.lower() in IMAGE_EXTENSIONS
        )
        labels = sorted(label_dir.glob("*.txt"))
        image_stems = {path.stem for path in images}
        label_stems = {path.stem for path in labels}
        counts = Counter()
        empty_labels = 0

        if not images:
            issues.append(f"{split}: no images found")

        stem_counts = Counter(path.stem for path in images)
        for stem, count in stem_counts.items():
            if count > 1:
                issues.append(
                    f"{split}: multiple images share filename stem {stem}"
                )

        for stem in sorted(image_stems - label_stems):
            issues.append(f"{split}: missing label for {stem}")

        for stem in sorted(label_stems - image_stems):
            issues.append(f"{split}: label has no image: {stem}")

        for image_path in images:
            try:
                hashes[file_hash(image_path)].append(
                    (split, image_path.relative_to(root).as_posix())
                )
            except OSError as error:
                issues.append(f"{split}: cannot read {image_path.name}: {error}")

        for label_path in labels:
            name = label_path.relative_to(root).as_posix()
            try:
                lines = label_path.read_text(
                    encoding="utf-8-sig"
                ).splitlines()
            except (OSError, UnicodeError) as error:
                issues.append(f"{name}: cannot read label: {error}")
                continue

            if not any(line.strip() for line in lines):
                empty_labels += 1
                continue

            seen_boxes = set()

            for line_number, line in enumerate(lines, start=1):
                if not line.strip():
                    continue

                location = f"{name}, line {line_number}"
                fields = line.split()

                if len(fields) != 5:
                    issues.append(f"{location}: expected 5 values")
                    continue

                try:
                    class_id = int(fields[0])
                    x, y, width, height = map(float, fields[1:])
                except ValueError:
                    issues.append(f"{location}: invalid numeric values")
                    continue

                if class_id not in CLASSES:
                    issues.append(f"{location}: unknown class ID {class_id}")
                    continue

                values = (x, y, width, height)
                if not all(math.isfinite(value) for value in values):
                    issues.append(f"{location}: non-finite coordinates")
                    continue

                if not (
                    0 <= x <= 1
                    and 0 <= y <= 1
                    and 0 < width <= 1
                    and 0 < height <= 1
                ):
                    issues.append(f"{location}: invalid coordinate range")
                    continue

                tolerance = 0.00001
                if (
                    x - width / 2 < -tolerance
                    or y - height / 2 < -tolerance
                    or x + width / 2 > 1 + tolerance
                    or y + height / 2 > 1 + tolerance
                ):
                    issues.append(f"{location}: box extends outside image")
                    continue

                box = (class_id, x, y, width, height)
                if box in seen_boxes:
                    issues.append(f"{location}: duplicate annotation")
                    continue

                seen_boxes.add(box)
                counts[class_id] += 1

        print(f"{split}: {len(images)} images, {len(labels)} label files")
        print(f"  Empty label files: {empty_labels}")
        for class_id, class_name in CLASSES.items():
            print(f"  {class_name}: {counts[class_id]} valid boxes")
        print("")

    duplicate_groups = [
        group for group in hashes.values() if len(group) > 1
    ]
    cross_split_groups = [
        group for group in duplicate_groups
        if len({split for split, _ in group}) > 1
    ]

    print(f"Exact duplicate image groups: {len(duplicate_groups)}")
    print(f"Groups spanning different splits: {len(cross_split_groups)}")

    for index, group in enumerate(duplicate_groups, start=1):
        print(f"\nDuplicate group {index}:")
        for split, name in group:
            print(f"  {name}")

    print(f"\nFile and annotation issues: {len(issues)}")
    for issue in issues:
        print(f"- {issue}")

    print("\nLIMITATIONS")
    print("- Hashes detect identical file bytes only.")
    print("- Resized, flipped, or similar images require further checks.")
    print("- Image decoding and visual label accuracy are not checked.")
    print("- Empty labels may be valid background images; review them.")
    print("- Class names must be checked against data.yaml.")
    print("- This report does not establish readiness for training.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path, help="Extracted dataset folder")
    args = parser.parse_args()

    if not args.dataset.is_dir():
        parser.error("Dataset folder does not exist.")

    check_dataset(args.dataset)

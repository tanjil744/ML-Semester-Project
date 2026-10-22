"""Convert YOLO polygons to boxes and remove duplicate annotations."""

import argparse
import json
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path


def prepare(root):
    changes = []
    errors = []
    totals = {"polygons_converted": 0, "duplicates_removed": 0}

    for split in ("train", "valid", "test"):
        folder = root / split / "labels"

        if not folder.is_dir():
            errors.append(f"Missing folder: {folder}")
            continue

        for path in sorted(folder.glob("*.txt")):
            original = path.read_bytes()
            output, seen = [], set()
            converted = removed = 0

            lines = original.decode("utf-8-sig").splitlines()

            for number, line in enumerate(lines, 1):
                if not line.strip():
                    output.append(line)
                    continue

                try:
                    fields = line.split()
                    class_id = int(fields[0])

                    if class_id not in range(4):
                        raise ValueError("class ID must be 0, 1, 2, or 3")

                    values = [Decimal(value) for value in fields[1:]]

                    if not all(value.is_finite() for value in values):
                        raise ValueError("non-finite coordinate")

                    polygon = len(values) >= 6 and len(values) % 2 == 0

                    if polygon:
                        if not all(0 <= value <= 1 for value in values):
                            raise ValueError("polygon coordinate outside [0, 1]")

                        xs, ys = values[::2], values[1::2]
                        left, right = min(xs), max(xs)
                        top, bottom = min(ys), max(ys)

                        values = [
                            (left + right) / 2,
                            (top + bottom) / 2,
                            right - left,
                            bottom - top,
                        ]

                    elif len(values) != 4:
                        raise ValueError("unsupported annotation format")

                    x, y, width, height = values

                    if not (
                        0 <= x <= 1
                        and 0 <= y <= 1
                        and 0 < width <= 1
                        and 0 < height <= 1
                    ):
                        raise ValueError("invalid box coordinates")

                    tolerance = Decimal("0.00001")

                    if (
                        x - width / 2 < -tolerance
                        or y - height / 2 < -tolerance
                        or x + width / 2 > 1 + tolerance
                        or y + height / 2 > 1 + tolerance
                    ):
                        raise ValueError("box extends outside image")

                    if polygon:
                        converted += 1

                    box = (class_id, *values)

                    if box in seen:
                        removed += 1
                        continue

                    seen.add(box)

                    if polygon:
                        line = str(class_id) + " " + " ".join(
                            format(value, "f") for value in values
                        )

                    output.append(line)

                except (ValueError, InvalidOperation) as error:
                    errors.append(
                        f"{path.relative_to(root)} line {number}: {error}"
                    )

            if converted or removed:
                updated = ("\n".join(output) + "\n").encode("utf-8")
                changes.append((path, original, updated, converted, removed))
                totals["polygons_converted"] += converted
                totals["duplicates_removed"] += removed

    if errors:
        raise SystemExit(
            "No files changed. Resolve these issues first:\n"
            + "\n".join(errors)
        )

    if not changes:
        print("No polygon conversions or duplicate removals needed.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    backup = root.parent / ("Label_Backup_" + timestamp)
    backup.mkdir()
    records = []

    # Back up all affected files before changing any labels.
    for path, original, updated, converted, removed in changes:
        relative = path.relative_to(root)
        destination = backup / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(original)

        records.append({
            "file": relative.as_posix(),
            "polygons_converted": converted,
            "duplicates_removed": removed,
        })

    report = {
        "dataset": str(root),
        "totals": totals,
        "files": records,
        "note": (
            "Format cleanup only; visual accuracy "
            "and split overlap are not verified."
        ),
    }

    (backup / "changes.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )

    for path, original, updated, converted, removed in changes:
        path.write_bytes(updated)

    print(f"Changed files: {len(changes)}")
    print(f"Polygons converted: {totals['polygons_converted']}")
    print(f"Duplicate annotations removed: {totals['duplicates_removed']}")
    print(f"Original files and changes.json saved in: {backup}")
    print("Run check_dataset.py again to verify the result.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path)
    args = parser.parse_args()

    if not args.dataset.is_dir():
        parser.error("Dataset folder does not exist.")

    prepare(args.dataset.resolve())

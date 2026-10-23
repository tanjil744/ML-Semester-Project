
import argparse
from pathlib import Path
from collections import Counter

from ultralytics import YOLO


# Class IDs from data.yaml
CLASS_NAMES = {
    0: "eraser",
    1: "pencil",
    2: "pencil sharpener",
    3: "ruler",
}

# Required items in a complete package
REQUIRED_ITEMS = {
    "pencil": 2,
    "eraser": 1,
    "ruler": 1,
}


def inspect_package(model, image_path, output_dir="runs/predictions",
                    confidence=0.25):
    """Detect stationery items and check package completeness."""

    image_path = Path(image_path)

    if not image_path.is_file():
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    results = model.predict(
        source=str(image_path),
        conf=confidence,
        save=True,
        project=output_dir,
        name="inspection",
        exist_ok=True,
        verbose=False,
    )

    result = results[0]
    detected_items = Counter()

    if result.boxes is not None:
        for box in result.boxes:
            class_id = int(box.cls.item())
            item_name = CLASS_NAMES.get(
                class_id, f"class_{class_id}"
            )
            detected_items[item_name] += 1

    print("\n--- PACKAGE INSPECTION REPORT ---")

    print("\nDetected items:")
    if detected_items:
        for item, count in sorted(detected_items.items()):
            print(f"  {item}: {count}")
    else:
        print("  No items detected.")

    missing_items = []
    incorrect_counts = []

    for item, required_count in REQUIRED_ITEMS.items():
        detected_count = detected_items[item]

        if detected_count < required_count:
            missing_items.append(
                f"{item}: need {required_count}, "
                f"detected {detected_count}"
            )
        elif detected_count > required_count:
            incorrect_counts.append(
                f"{item}: need {required_count}, "
                f"detected {detected_count}"
            )

    if not missing_items and not incorrect_counts:
        print("\nResult: PACKAGE COMPLETE")
    else:
        print("\nResult: PACKAGE NEEDS REVIEW")

        for issue in missing_items:
            print(f"  Missing/insufficient: {issue}")

        for issue in incorrect_counts:
            print(f"  Excess quantity: {issue}")

    print(
        f"\nAnnotated image saved under: "
        f"{output_dir}/inspection/"
    )

    return detected_items


def main():
    parser = argparse.ArgumentParser(
        description="Inspect a stationery package using YOLO"
    )

    parser.add_argument(
        "--weights",
        required=True,
        help="Path to trained best.pt weights",
    )
    parser.add_argument(
        "--image",
        required=True,
        help="Path to the package image",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.25,
        help="Detection confidence threshold (default: 0.25)",
    )

    args = parser.parse_args()

    weights_path = Path(args.weights)

    if not weights_path.is_file():
        raise FileNotFoundError(
            f"Model weights not found: {weights_path}"
        )

    model = YOLO(str(weights_path))

    inspect_package(
        model=model,
        image_path=args.image,
        confidence=args.conf,
    )


if __name__ == "__main__":
    main()

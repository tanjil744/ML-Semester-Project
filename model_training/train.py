import argparse
from pathlib import Path
from ultralytics import YOLO


def main():
    parser = argparse.ArgumentParser(
        description="Train a YOLO model for packaging quality inspection"
    )

    parser.add_argument("--data", required=True, help="Path to data.yaml")
    parser.add_argument("--model", default="yolo11n.pt")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--project", default="runs/packaging")
    parser.add_argument("--name", default="baseline")

    args = parser.parse_args()

    data_path = Path(args.data).resolve()

    if not data_path.is_file():
        raise FileNotFoundError(
            f"Dataset YAML not found: {data_path}"
        )

    # Load pre-trained YOLO weights
    model = YOLO(args.model)

    # Fine-tune the model on the packaging dataset
    model.train(
        data=str(data_path),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        patience=10,
        seed=42,
        project=args.project,
        name=args.name,
        plots=True,
    )

    # Locate the best checkpoint
    best_weights = (
        Path(args.project)
        / args.name
        / "weights"
        / "best.pt"
    )

    print(f"\nTraining finished. Best model: {best_weights}")
    print("Next: evaluate this checkpoint on the validation set.")


if __name__ == "__main__":
    main()

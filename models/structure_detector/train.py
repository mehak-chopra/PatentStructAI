"""
Run with:

python -m models.structure_detector.train --version v2

or

python -m models.structure_detector.train \
    --version v2 \
    --epochs 300 \
    --batch 8 \
    --imgsz 640 \
    --model yolov8n.pt
"""

from pathlib import Path
import argparse

from ultralytics import YOLO


# =====================================================
# Command Line Arguments
# =====================================================

parser = argparse.ArgumentParser(
    description="Train the PatentStructAI chemical structure detector."
)

parser.add_argument(
    "--version",
    required=True,
    help="Dataset version (v1, v2, v3...)"
)

parser.add_argument(
    "--model",
    default="yolov8n.pt",
    help="YOLO model checkpoint."
)

parser.add_argument(
    "--epochs",
    type=int,
    default=300,
    help="Maximum number of training epochs."
)

parser.add_argument(
    "--batch",
    type=int,
    default=8,
    help="Batch size."
)

parser.add_argument(
    "--imgsz",
    type=int,
    default=640,
    help="Training image size."
)

parser.add_argument(
    "--patience",
    type=int,
    default=30,
    help="Early stopping patience."
)

args = parser.parse_args()

DATASET_VERSION = args.version

DATASET_YAML = Path(
    f"annotations/datasets/{DATASET_VERSION}/data.yaml"
)

if not DATASET_YAML.exists():

    raise FileNotFoundError(
        f"Dataset not found:\n{DATASET_YAML}"
    )


# =====================================================
# Model
# =====================================================

model = YOLO(
    args.model
)


# =====================================================
# Experiment Name
# =====================================================

MODEL_NAME = Path(
    args.model
).stem

EXPERIMENT_NAME = (
    f"{MODEL_NAME}_{DATASET_VERSION}"
)


# =====================================================
# Training Summary
# =====================================================

print()
print("=" * 55)
print("PatentStructAI Detector Training")
print("=" * 55)

print(f"Dataset Version : {DATASET_VERSION}")
print(f"Dataset         : {DATASET_YAML}")
print(f"Model           : {args.model}")
print(f"Experiment      : {EXPERIMENT_NAME}")
print(f"Epochs          : {args.epochs}")
print(f"Batch Size      : {args.batch}")
print(f"Image Size      : {args.imgsz}")
print(f"Patience        : {args.patience}")

print()


# =====================================================
# Train
# =====================================================

model.train(

    data=str(DATASET_YAML),

    epochs=args.epochs,

    imgsz=args.imgsz,

    batch=args.batch,

    patience=args.patience,

    project="models/structure_detector/experiments",

    name=EXPERIMENT_NAME,

    optimizer="auto",

    seed=42,

    deterministic=True,

    pretrained=True,

    plots=True,

    save=True,

    exist_ok=False
)
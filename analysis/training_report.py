"""
Run:

python -m analysis.training_report --experiment yolov8n_v2
"""

from pathlib import Path
import argparse
import sys
import yaml
import pandas as pd


# =====================================================
# Command Line Arguments
# =====================================================

parser = argparse.ArgumentParser(
    description=(
        "Generate a training report for a "
        "PatentStructAI detector experiment."
    )
)

parser.add_argument(
    "--experiment",
    required=True,
    help=(
        "Experiment folder name "
        "(example: yolov8n_v2)"
    )
)

args = parser.parse_args()

EXPERIMENT_NAME = args.experiment


# =====================================================
# Experiment Paths
# =====================================================

EXPERIMENT_ROOT = (
    Path(
        "models/structure_detector/experiments"
    )
    / EXPERIMENT_NAME
)

RESULTS_CSV = (
    EXPERIMENT_ROOT /
    "results.csv"
)

ARGS_YAML = (
    EXPERIMENT_ROOT /
    "args.yaml"
)

BEST_WEIGHTS = (
    EXPERIMENT_ROOT /
    "weights" /
    "best.pt"
)

LAST_WEIGHTS = (
    EXPERIMENT_ROOT /
    "weights" /
    "last.pt"
)


# =====================================================
# Validation
# =====================================================

if not EXPERIMENT_ROOT.exists():

    print(
        f"Experiment not found:\n"
        f"{EXPERIMENT_ROOT}"
    )

    sys.exit(1)

if not RESULTS_CSV.exists():

    print(
        "results.csv not found."
    )

    sys.exit(1)

if not ARGS_YAML.exists():

    print(
        "args.yaml not found."
    )

    sys.exit(1)


# =====================================================
# Load Files
# =====================================================

results = pd.read_csv(
    RESULTS_CSV
)

with open(
    ARGS_YAML,
    "r",
    encoding="utf-8"
) as file:

    args_yaml = yaml.safe_load(
        file
    )


# =====================================================
# Helper Functions
# =====================================================

def exists(path):

    return (
        "✓"
        if path.exists()
        else
        "✗"
    )


def round_metric(value):

    return round(
        float(value),
        4
    )


def hours(seconds):

    return (
        seconds / 3600
    )


def get_best_epoch():

    best_index = (
        results[
            "metrics/mAP50-95(B)"
        ].idxmax()
    )

    return (
        best_index,
        results.iloc[
            best_index
        ]
    )

# =====================================================
# Training Statistics
# =====================================================

best_epoch_index, best_row = (
    get_best_epoch()
)

best_epoch = int(
    best_row["epoch"]
)

epochs_completed = int(
    results["epoch"].max()
)

best_precision = round_metric(
    best_row[
        "metrics/precision(B)"
    ]
)

best_recall = round_metric(
    best_row[
        "metrics/recall(B)"
    ]
)

best_map50 = round_metric(
    best_row[
        "metrics/mAP50(B)"
    ]
)

best_map5095 = round_metric(
    best_row[
        "metrics/mAP50-95(B)"
    ]
)

best_box_loss = round_metric(
    best_row[
        "train/box_loss"
    ]
)

best_cls_loss = round_metric(
    best_row[
        "train/cls_loss"
    ]
)

best_dfl_loss = round_metric(
    best_row[
        "train/dfl_loss"
    ]
)

training_time_seconds = float(
    results.iloc[-1]["time"]
)

training_time_hours = hours(
    training_time_seconds
)

average_epoch_time = (
    training_time_seconds /
    epochs_completed
)


# =====================================================
# Model Configuration
# =====================================================

model_name = args_yaml.get(
    "model",
    "Unknown"
)

dataset_path = args_yaml.get(
    "data",
    "Unknown"
)

image_size = args_yaml.get(
    "imgsz",
    "Unknown"
)

batch_size = args_yaml.get(
    "batch",
    "Unknown"
)

optimizer = args_yaml.get(
    "optimizer",
    "Unknown"
)

requested_epochs = args_yaml.get(
    "epochs",
    "Unknown"
)

patience = args_yaml.get(
    "patience",
    "Unknown"
)

device = args_yaml.get(
    "device",
    "Unknown"
)


# =====================================================
# Output Files
# =====================================================

OUTPUT_FILES = {

    "Best Weights":
        BEST_WEIGHTS,

    "Last Weights":
        LAST_WEIGHTS,

    "Results Plot":
        EXPERIMENT_ROOT /
        "results.png",

    "Confusion Matrix":
        EXPERIMENT_ROOT /
        "confusion_matrix.png",

    "Normalized Confusion Matrix":
        EXPERIMENT_ROOT /
        "confusion_matrix_normalized.png",

    "Precision-Recall Curve":
        EXPERIMENT_ROOT /
        "BoxPR_curve.png",

    "Precision Curve":
        EXPERIMENT_ROOT /
        "BoxP_curve.png",

    "Recall Curve":
        EXPERIMENT_ROOT /
        "BoxR_curve.png",

    "F1 Curve":
        EXPERIMENT_ROOT /
        "BoxF1_curve.png",

    "Label Distribution":
        EXPERIMENT_ROOT /
        "labels.jpg"

}

# =====================================================
# Report
# =====================================================

def performance_rating():

    if best_map5095 >= 0.95:

        return (
            "★★★★★ Excellent",
            "Model achieved excellent validation performance. Recommended checkpoint: weights/best.pt"
        )

    if best_map5095 >= 0.90:

        return (
            "★★★★☆ Very Good",
            "Minor improvements may still be possible."
        )

    if best_map5095 >= 0.80:

        return (
            "★★★☆☆ Good",
            "Consider additional training."
        )

    return (
        "★★☆☆☆ Needs Improvement",
        "Improve the dataset or tune hyperparameters."
    )


def print_report():

    rating, verdict = (
        performance_rating()
    )

    print()

    print("=" * 55)
    print(
        "PatentStructAI Training Report"
    )
    print("=" * 55)

    print()

    print(
        "Ultralytics YOLO Detector"
    )

    print()

    print("-" * 40)
    print("Experiment")
    print("-" * 40)

    print(
        f"Experiment Name : "
        f"{EXPERIMENT_NAME}"
    )

    print(
        f"Model           : "
        f"{model_name}"
    )

    print(
        f"Dataset         : "
        f"{dataset_path}"
    )

    print(
        f"Image Size      : "
        f"{image_size}"
    )

    print(
        f"Batch Size      : "
        f"{batch_size}"
    )

    print(
        f"Optimizer       : "
        f"{optimizer}"
    )

    print(
        f"Device          : "
        f"{device}"
    )

    print()

    print("-" * 40)
    print("Training")
    print("-" * 40)

    print(
        f"Requested Epochs : "
        f"{requested_epochs}"
    )

    print(
        f"Completed Epochs : "
        f"{epochs_completed}"
    )

    print(
        f"Best Epoch       : "
        f"{best_epoch}"
    )

    print(
        f"Early Stop       : "
        f"{patience}"
    )

    print()

    print(
        f"Training Time    : "
        f"{training_time_hours:.2f} hours"
    )

    print(
        f"Average/Epoch    : "
        f"{average_epoch_time:.2f} sec"
    )

    print()

    print("-" * 40)
    print("Best Validation Metrics")
    print("-" * 40)

    print(
        f"Precision   : "
        f"{best_precision:.4f}"
    )

    print(
        f"Recall      : "
        f"{best_recall:.4f}"
    )

    print(
        f"mAP50       : "
        f"{best_map50:.4f}"
    )

    print(
        f"mAP50-95    : "
        f"{best_map5095:.4f}"
    )

    print()

    print("-" * 40)
    print("Training Loss")
    print("-" * 40)

    print(
        f"Box Loss    : "
        f"{best_box_loss:.4f}"
    )

    print(
        f"Cls Loss    : "
        f"{best_cls_loss:.4f}"
    )

    print(
        f"DFL Loss    : "
        f"{best_dfl_loss:.4f}"
    )

    print()

    print("-" * 40)
    print("Generated Files")
    print("-" * 40)

    for name, path in OUTPUT_FILES.items():

        print(
            f"{exists(path)} {name}"
        )

    print()

    print("-" * 40)
    print("Overall Performance")
    print("-" * 40)

    print(rating)
    print(verdict)

    print()

    print("-" * 40)
    print("Experiment Folder")
    print("-" * 40)

    print(
        EXPERIMENT_ROOT.as_posix()
    )

    print()

    print("=" * 55)


# =====================================================
# Main
# =====================================================

def main():

    print_report()


if __name__ == "__main__":

    main()
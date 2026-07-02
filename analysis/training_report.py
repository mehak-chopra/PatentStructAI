"""
PatentStructAI Training Report

Examples
--------

Generate a report for a single experiment

python -m analysis.training_report --experiment yolov8n_v2

Show the leaderboard of all experiments

python -m analysis.training_report --leaderboard

Compare two experiments

python -m analysis.training_report --compare yolov8n_v1 yolov8n_v2
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
        "PatentStructAI Training Report Utility"
    )
)

mode = parser.add_mutually_exclusive_group(
    required=True
)

mode.add_argument(

    "--experiment",

    help=(
        "Generate a report for a single experiment "
        "(example: yolov8n_v2)"
    )

)

mode.add_argument(

    "--leaderboard",

    action="store_true",

    help=(
        "Show all experiments ranked by performance."
    )

)

mode.add_argument(

    "--compare",

    nargs=2,

    metavar=(
        "EXPERIMENT_1",
        "EXPERIMENT_2"
    ),

    help=(
        "Compare two experiments."
    )

)

parser.add_argument(

    "--markdown",

    action="store_true",

    help=(
        "Also generate REPORT.md inside the experiment folder."
    )

)

args = parser.parse_args()

EXPERIMENT_NAME = (
    args.experiment
)


# =====================================================
# Experiment Helpers
# =====================================================

EXPERIMENTS_ROOT = Path(
    "models/structure_detector/experiments"
)


def experiment_paths(experiment_name):

    root = (
        EXPERIMENTS_ROOT /
        experiment_name
    )

    return {

        "root": root,

        "results":
            root / "results.csv",

        "args":
            root / "args.yaml",

        "best":
            root / "weights" / "best.pt",

        "last":
            root / "weights" / "last.pt"

    }


def discover_experiments():

    if not EXPERIMENTS_ROOT.exists():

        return []

    experiments = []

    for folder in sorted(
        EXPERIMENTS_ROOT.iterdir()
    ):

        if not folder.is_dir():

            continue

        if (
            folder /
            "results.csv"
        ).exists():

            experiments.append(
                folder.name
            )

    return experiments


def load_experiment(
    experiment_name
):

    paths = experiment_paths(
        experiment_name
    )

    if not paths["root"].exists():

        print(
            f"Experiment not found:\n"
            f"{paths['root']}"
        )

        sys.exit(1)

    if not paths["results"].exists():

        print(
            "results.csv not found."
        )

        sys.exit(1)

    if not paths["args"].exists():

        print(
            "args.yaml not found."
        )

        sys.exit(1)

    results = pd.read_csv(
        paths["results"]
    )

    with open(
        paths["args"],
        "r",
        encoding="utf-8"
    ) as file:

        args_yaml = yaml.safe_load(
            file
        )

    return (
        results,
        args_yaml,
        paths
    )


# =====================================================
# Load Experiment
# =====================================================

if args.experiment:

    results, args_yaml, PATHS = (

        load_experiment(
            args.experiment
        )

    )

    EXPERIMENT_ROOT = PATHS["root"]

    RESULTS_CSV = PATHS["results"]

    ARGS_YAML = PATHS["args"]

    BEST_WEIGHTS = PATHS["best"]

    LAST_WEIGHTS = PATHS["last"]

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


def get_best_epoch(results_df):

    best_index = (
        results_df[
            "metrics/mAP50-95(B)"
        ].idxmax()
    )

    return (
        best_index,
        results_df.iloc[
            best_index
        ]
    )


def get_training_statistics(results_df):

    _, best_row = (
        get_best_epoch(
            results_df
        )
    )

    epochs_completed = int(
        results_df["epoch"].max()
    )

    training_time_seconds = float(
        results_df.iloc[-1]["time"]
    )

    return {

        "best_epoch":
            int(best_row["epoch"]),

        "epochs_completed":
            epochs_completed,

        "precision":
            round_metric(
                best_row[
                    "metrics/precision(B)"
                ]
            ),

        "recall":
            round_metric(
                best_row[
                    "metrics/recall(B)"
                ]
            ),

        "map50":
            round_metric(
                best_row[
                    "metrics/mAP50(B)"
                ]
            ),

        "map5095":
            round_metric(
                best_row[
                    "metrics/mAP50-95(B)"
                ]
            ),

        "box_loss":
            round_metric(
                best_row[
                    "train/box_loss"
                ]
            ),

        "cls_loss":
            round_metric(
                best_row[
                    "train/cls_loss"
                ]
            ),

        "dfl_loss":
            round_metric(
                best_row[
                    "train/dfl_loss"
                ]
            ),

        "training_seconds":
            training_time_seconds,

        "training_hours":
            hours(
                training_time_seconds
            ),

        "average_epoch_time":
            training_time_seconds /
            epochs_completed

    }


def get_model_configuration(config):

    return {

        "model":
            config.get(
                "model",
                "Unknown"
            ),

        "dataset":
            config.get(
                "data",
                "Unknown"
            ),

        "image_size":
            config.get(
                "imgsz",
                "Unknown"
            ),

        "batch_size":
            config.get(
                "batch",
                "Unknown"
            ),

        "optimizer":
            config.get(
                "optimizer",
                "Unknown"
            ),

        "requested_epochs":
            config.get(
                "epochs",
                "Unknown"
            ),

        "patience":
            config.get(
                "patience",
                "Unknown"
            ),

        "device":
            config.get(
                "device",
                "Unknown"
            )

    }


# =====================================================
# Analysis Helpers
# =====================================================

def improvement(results_df):

    first = float(
        results_df.iloc[0][
            "metrics/mAP50-95(B)"
        ]
    )

    last = float(
        results_df.iloc[-1][
            "metrics/mAP50-95(B)"
        ]
    )

    return round(
        last - first,
        4
    )


def plateau_epoch(results_df):

    metric = (
        results_df[
            "metrics/mAP50-95(B)"
        ]
    )

    running_best = metric.cummax()

    threshold = 0.001

    for i in range(

        len(metric) - 20

    ):

        future_best = (

            running_best.iloc[
                i + 20
            ]

        )

        current = (

            running_best.iloc[i]

        )

        if (

            future_best - current

        ) < threshold:

            return int(
                results_df.iloc[i][
                    "epoch"
                ]
            )

    return None


def convergence_status(results_df):

    plateau = plateau_epoch(
        results_df
    )

    if plateau is None:

        return (
            "Training continued improving until the final epoch."
        )

    return (

        f"Validation performance plateaued around epoch {plateau}."

    )


def recommendation(results_df):

    plateau = plateau_epoch(
        results_df
    )

    best_epoch = int(

        get_best_epoch(
            results_df
        )[1]["epoch"]

    )

    if plateau is None:

        return (
            "Continue using the current training configuration."
        )

    return (

        f"Best checkpoint: epoch {best_epoch}. "
        f"Future runs may reduce max epochs to around {plateau + 20}."

    )


def experiment_summary(

    experiment_name

):

    results_df, args_df, _ = (

        load_experiment(
            experiment_name
        )

    )

    stats = (

        get_training_statistics(
            results_df
        )

    )

    return {

        "experiment":
            experiment_name,

        "model":
            args_df.get(
                "model",
                "-"
            ),

        "epochs":
            stats[
                "epochs_completed"
            ],

        "precision":
            stats[
                "precision"
            ],

        "recall":
            stats[
                "recall"
            ],

        "map50":
            stats[
                "map50"
            ],

        "map5095":
            stats[
                "map5095"
            ],

        "training_hours":
            round(
                stats[
                    "training_hours"
                ],
                2
            )

    }


# =====================================================
# Parsed Statistics
# =====================================================

if args.experiment:

    stats = get_training_statistics(
        results
    )

    config = get_model_configuration(
        args_yaml
    )

    best_epoch = stats[
        "best_epoch"
    ]

    epochs_completed = stats[
        "epochs_completed"
    ]

    best_precision = stats[
        "precision"
    ]

    best_recall = stats[
        "recall"
    ]

    best_map50 = stats[
        "map50"
    ]

    best_map5095 = stats[
        "map5095"
    ]

    best_box_loss = stats[
        "box_loss"
    ]

    best_cls_loss = stats[
        "cls_loss"
    ]

    best_dfl_loss = stats[
        "dfl_loss"
    ]

    training_time_seconds = stats[
        "training_seconds"
    ]

    training_time_hours = stats[
        "training_hours"
    ]

    average_epoch_time = stats[
        "average_epoch_time"
    ]


    model_name = config[
        "model"
    ]

    dataset_path = config[
        "dataset"
    ]

    image_size = config[
        "image_size"
    ]

    batch_size = config[
        "batch_size"
    ]

    optimizer = config[
        "optimizer"
    ]

    requested_epochs = config[
        "requested_epochs"
    ]

    patience = config[
        "patience"
    ]

    device = config[
        "device"
    ]


# =====================================================
# Output Files
# =====================================================

if args.experiment:

    OUTPUT_FILES = {

        "Best Weights":
            BEST_WEIGHTS,

        "Last Weights":
            LAST_WEIGHTS,

        "Results Plot":
            EXPERIMENT_ROOT / "results.png",

        "Confusion Matrix":
            EXPERIMENT_ROOT / "confusion_matrix.png",

        "Normalized Confusion Matrix":
            EXPERIMENT_ROOT / "confusion_matrix_normalized.png",

        "Precision-Recall Curve":
            EXPERIMENT_ROOT / "BoxPR_curve.png",

        "Precision Curve":
            EXPERIMENT_ROOT / "BoxP_curve.png",

        "Recall Curve":
            EXPERIMENT_ROOT / "BoxR_curve.png",

        "F1 Curve":
            EXPERIMENT_ROOT / "BoxF1_curve.png",

        "Label Distribution":
            EXPERIMENT_ROOT / "labels.jpg"

    }


# =====================================================
# Report Helpers
# =====================================================

def divider(title=None):

    print()

    print("-" * 40)

    if title:

        print(title)
        print("-" * 40)


def performance_rating():

    score = best_map5095

    if score >= 0.95:

        return (
            "★★★★★ Excellent",
            "Model achieved excellent validation performance.\n"
            "Recommended checkpoint: weights/best.pt"
        )

    if score >= 0.90:

        return (
            "★★★★☆ Very Good",
            "Suitable for most inference tasks."
        )

    if score >= 0.80:

        return (
            "★★★☆☆ Good",
            "Performance is acceptable but additional training may improve results."
        )

    return (

        "★★☆☆☆ Needs Improvement",

        "Dataset quality or hyperparameters should be improved."

    )


def print_key_value(title, value):

    print(
        f"{title:<18}: {value}"
    )


def print_generated_files():

    divider("Generated Files")

    for name, path in OUTPUT_FILES.items():

        print(
            f"{exists(path)} {name}"
        )


def print_experiment():

    divider("Experiment")

    print_key_value(
        "Experiment",
        EXPERIMENT_NAME
    )

    print_key_value(
        "Model",
        model_name
    )

    print_key_value(
        "Dataset",
        dataset_path
    )

    print_key_value(
        "Image Size",
        image_size
    )

    print_key_value(
        "Batch Size",
        batch_size
    )

    print_key_value(
        "Optimizer",
        optimizer
    )

    print_key_value(
        "Device",
        device
    )


def print_training():

    divider("Training")

    print_key_value(
        "Requested Epochs",
        requested_epochs
    )

    print_key_value(
        "Completed Epochs",
        epochs_completed
    )

    print_key_value(
        "Best Epoch",
        best_epoch
    )

    print_key_value(
        "Patience",
        patience
    )

    print_key_value(
        "Training Time",
        f"{training_time_hours:.2f} hours"
    )

    print_key_value(
        "Average / Epoch",
        f"{average_epoch_time:.2f} sec"
    )


def print_metrics():

    divider("Best Validation Metrics")

    print_key_value(
        "Precision",
        f"{best_precision:.4f}"
    )

    print_key_value(
        "Recall",
        f"{best_recall:.4f}"
    )

    print_key_value(
        "mAP50",
        f"{best_map50:.4f}"
    )

    print_key_value(
        "mAP50-95",
        f"{best_map5095:.4f}"
    )


def print_losses():

    divider("Training Loss")

    print_key_value(
        "Box Loss",
        f"{best_box_loss:.4f}"
    )

    print_key_value(
        "Cls Loss",
        f"{best_cls_loss:.4f}"
    )

    print_key_value(
        "DFL Loss",
        f"{best_dfl_loss:.4f}"
    )


def print_summary():

    rating, verdict = performance_rating()

    divider("Overall Performance")

    print(rating)

    print()

    print(verdict)

    print()

    divider("Training Analysis")

    print(
        convergence_status(
            results
        )
    )

    print()

    print(
        f"Total Improvement : "
        f"{improvement(results):.4f}"
    )

    print()

    divider("Recommendation")

    print(
        recommendation(
            results
        )
    )


def print_footer():

    divider("Experiment Folder")

    print(
        EXPERIMENT_ROOT.as_posix()
    )

    print()

    print("=" * 55)


# =====================================================
# Report
# =====================================================

def print_leaderboard():

    divider(
        "Experiment Leaderboard"
    )

    summaries = []

    for experiment in discover_experiments():

        summaries.append(
            experiment_summary(
                experiment
            )
        )

    summaries.sort(

        key=lambda x:
        x["map5095"],

        reverse=True

    )

    print(

        f"{'Rank':<6}"
        f"{'Experiment':<18}"
        f"{'mAP50-95':<12}"
        f"{'Precision':<12}"
        f"{'Recall':<12}"

    )

    print("-" * 60)

    for rank, summary in enumerate(

        summaries,

        start=1

    ):

        print(

            f"{rank:<6}"
            f"{summary['experiment']:<18}"
            f"{summary['map5095']:<12.4f}"
            f"{summary['precision']:<12.4f}"
            f"{summary['recall']:<12.4f}"

        )

def print_comparison():

    exp1, exp2 = args.compare

    left = experiment_summary(
        exp1
    )

    right = experiment_summary(
        exp2
    )

    divider(
        "Experiment Comparison"
    )

    print(
        f"{'Metric':<15}"
        f"{exp1:<18}"
        f"{exp2}"
    )

    print("-" * 55)

    metrics = [

        "precision",

        "recall",

        "map50",

        "map5095"

    ]

    for metric in metrics:

        print(

            f"{metric:<15}"

            f"{left[metric]:<18.4f}"

            f"{right[metric]:.4f}"

        )

        winner = (
        exp1
        if left["map5095"] >
        right["map5095"]
        else exp2
    )

# -----------------------------
# Improvement calculations
# -----------------------------

    p1 = left["precision"]
    p2 = right["precision"]

    r1 = left["recall"]
    r2 = right["recall"]

    m50_1 = left["map50"]
    m50_2 = right["map50"]

    m95_1 = left["map5095"]
    m95_2 = right["map5095"]

    print()

    print(f"Overall Winner : {winner}")

    print()

    print("Improvements")
    print("-" * 30)

    print(
        f"Precision : {(p2 - p1) * 100:+.2f}%"
    )

    print(
        f"Recall    : {(r2 - r1) * 100:+.2f}%"
    )

    print(
        f"mAP50     : {(m50_2 - m50_1) * 100:+.2f}%"
    )

    print(
        f"mAP50-95  : {(m95_2 - m95_1) * 100:+.2f}%"
    )

def print_report():

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

    print_experiment()

    print_training()

    print_metrics()

    print_losses()

    print_generated_files()

    print_summary()

    print_footer()


# =====================================================
# Main
# =====================================================

def main():

    if args.leaderboard:

        print_leaderboard()
        return

    if args.compare:

        print_comparison()
        return

    print_report()

if __name__ == "__main__":

    main()
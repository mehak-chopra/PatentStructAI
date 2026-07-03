"""
PatentStructAI Model Evaluation

Example
-------

Evaluate a trained detector

python -m analysis.evaluate --experiment yolov8n_v2
python -m analysis.evaluate --experiment yolov8n_v2 --save-images
"""

from pathlib import Path
import argparse
import json
import shutil
import sys
import yaml

from ultralytics import YOLO
from datetime import datetime

# =====================================================
# Command Line Arguments
# =====================================================

parser = argparse.ArgumentParser(
    description=(
        "Evaluate a trained PatentStructAI "
        "chemical structure detector."
    )
)

parser.add_argument(
    "--experiment",
    required=True,
    help=(
        "Experiment folder "
        "(example: yolov8n_v2)"
    )
)

parser.add_argument(
    "--conf",
    type=float,
    default=0.25,
    help=(
        "Confidence threshold "
        "used during evaluation."
    )
)

parser.add_argument(
    "--device",
    default=None,
    help=(
        "Override evaluation device "
        "(cpu, cuda, cuda:0, etc.)."
    )
)

parser.add_argument(
    "--save-json",
    action="store_true",
    help=(
        "Save evaluation metrics "
        "as JSON."
    )
)

parser.add_argument(
    "--save-images",
    action="store_true",
    help=(
        "Save prediction images."
    )
)

args = parser.parse_args()

EXPERIMENT_NAME = args.experiment

EXPERIMENTS_ROOT = Path(
    "models/structure_detector/experiments"
)

EVALUATIONS_ROOT = Path(
    "models/structure_detector/evaluations"
)

# =====================================================
# Experiment Paths
# =====================================================

def experiment_paths(name):

    experiment = (
        EXPERIMENTS_ROOT /
        name
    )

    evaluation = (
        EVALUATIONS_ROOT /
        name
    )

    return {

        "experiment":
            experiment,

        "evaluation":
            evaluation,

        "plots":
            evaluation /
            "plots",

        "predictions":
            evaluation /
            "predictions",

        "metrics":
            evaluation /
            "evaluation_metrics.json",

        "report":
            evaluation /
            "evaluation_report.txt",

        "weights":
            experiment /
            "weights" /
            "best.pt",

        "args":
            experiment /
            "args.yaml"

    }

# =====================================================
# Validation
# =====================================================

def validate_experiment(paths):

    if not paths["experiment"].exists():

        print(
            "Experiment not found."
        )

        sys.exit(1)

    if not paths["weights"].exists():

        print(
            "best.pt not found."
        )

        sys.exit(1)

    if not paths["args"].exists():

        print(
            "args.yaml not found."
        )

        sys.exit(1)


# =====================================================
# Evaluation Workspace
# =====================================================

def prepare_workspace(paths):

    paths["evaluation"].mkdir(
        parents=True,
        exist_ok=True
    )

    paths["plots"].mkdir(
        exist_ok=True
    )

    paths["predictions"].mkdir(
        exist_ok=True
    )

# =====================================================
# Initialization
# =====================================================

PATHS = experiment_paths(
    EXPERIMENT_NAME
)

validate_experiment(
    PATHS
)

prepare_workspace(
    PATHS
)

# =====================================================
# Load Configuration
# =====================================================

def load_configuration(paths):

    with open(
        paths["args"],
        "r",
        encoding="utf-8"
    ) as file:

        config = yaml.safe_load(
            file
        )

    return config


CONFIG = load_configuration(
    PATHS
)

DATASET_YAML = Path(
    CONFIG["data"]
)

if not DATASET_YAML.exists():

    print(
        f"Dataset configuration not found:\n"
        f"{DATASET_YAML}"
    )

    sys.exit(1)


MODEL_CONFIG = {

    "model":
        CONFIG.get(
            "model",
            "Unknown"
        ),

    "batch":
        CONFIG.get(
            "batch",
            1
        ),

    "imgsz":
        CONFIG.get(
            "imgsz",
            640
        ),

    "device":
        (
            args.device
            if args.device is not None
            else CONFIG.get(
                "device",
                "cpu"
            )
        ),

    "dataset":
        DATASET_YAML

}

# =====================================================
# Model Evaluation
# =====================================================

def evaluate_model():

    print()

    print("=" * 55)
    print("PatentStructAI Model Evaluation")
    print("=" * 55)

    print()

    print(
        f"Experiment : {EXPERIMENT_NAME}"
    )

    print(
        f"Weights    : {PATHS['weights']}"
    )

    print(
        f"Dataset    : {MODEL_CONFIG['dataset']}"
    )

    print()

    print(
        "Loading model..."
    )

    model = YOLO(
        PATHS["weights"]
    )

    print(
        "Running evaluation..."
    )

    results = model.val(

        data=str(
            MODEL_CONFIG["dataset"]
        ),

        imgsz=MODEL_CONFIG[
            "imgsz"
        ],

        batch=MODEL_CONFIG[
            "batch"
        ],

        device=MODEL_CONFIG[
            "device"
        ],

        conf=args.conf,

        split="test",

        project=str(
            PATHS["evaluation"]
        ),

        name="evaluation",

        exist_ok=True,

        plots=True,

        save=args.save_images,

        save_json=args.save_json,

        verbose=True

    )

    return results

# =====================================================
# Organize Evaluation Outputs
# =====================================================

def organize_outputs(results):

    source = Path(
        results.save_dir
    )

    if not source.exists():

        return

    plot_map = {

        "BoxF1_curve.png":
            "f1_curve.png",

        "BoxP_curve.png":
            "precision_curve.png",

        "BoxPR_curve.png":
            "precision_recall_curve.png",

        "BoxR_curve.png":
            "recall_curve.png",

        "confusion_matrix.png":
            "confusion_matrix.png",

        "confusion_matrix_normalized.png":
            "confusion_matrix_normalized.png"

    }

    for original, renamed in plot_map.items():

        src = source / original

        if src.exists():

            shutil.copy2(

                src,

                PATHS["plots"] / renamed

            )

    for image in source.glob("val_batch*_pred.jpg"):

        new_name = image.name.replace(
            "val_batch",
            "test_batch"
        )

        shutil.copy2(

            image,

            PATHS["predictions"] / new_name

        )

    for image in source.glob("val_batch*_labels.jpg"):

        new_name = image.name.replace(
            "val_batch",
            "test_batch"
        )

        shutil.copy2(

            image,

            PATHS["predictions"] / new_name

        )

    try:

        shutil.rmtree(source)

    except Exception:

        pass

    print()

    print(
        "Evaluation outputs organized."
    )

# =====================================================
# Save Evaluation Metrics
# =====================================================

def save_metrics(results):

    metrics = {

    "experiment":
        EXPERIMENT_NAME,

    "timestamp":
        datetime.now().isoformat(),

    "confidence_threshold":
        args.conf,

    "split":
        "test",

    "weights":
        str(PATHS["weights"]),

    "model":
        MODEL_CONFIG["model"],

    "image_size":
        MODEL_CONFIG["imgsz"],

    "batch_size":
        MODEL_CONFIG["batch"],

    "device":
        MODEL_CONFIG["device"],

    "dataset":
        str(MODEL_CONFIG["dataset"]),

    "test_images":
        int(results.nt_per_image.sum()),

    "test_instances":
        int(results.nt_per_class.sum()),

    "precision":
        float(results.box.mp),

    "recall":
        float(results.box.mr),

    "map50":
        float(results.box.map50),

    "map5095":
        float(results.box.map),

    "speed_ms_per_image":
        results.speed

}

    with open(

        PATHS["metrics"],

        "w",

        encoding="utf-8"

    ) as file:

        json.dump(

            metrics,

            file,

            indent=4

        )

    return metrics

# =====================================================
# Save Human Readable Report
# =====================================================

def evaluation_rating(metrics):

    score = metrics["map5095"]

    if score >= 0.95:

        return (

            "★★★★★ Excellent",

            "Model generalizes extremely well on the held-out test dataset."

        )

    if score >= 0.90:

        return (

            "★★★★☆ Very Good",

            "Suitable for production with minor improvements possible."

        )

    if score >= 0.80:

        return (

            "★★★☆☆ Good",

            "Usable but additional training is recommended."

        )

    return (

        "★★☆☆☆ Needs Improvement",

        "Collect more data or improve training."

    )

def save_report(metrics):

    rating, verdict = evaluation_rating(
        metrics
    )

    lines = [

        "=" * 55,

        "PatentStructAI Evaluation Report",

        "=" * 55,

        "",

        f"Experiment : {metrics['experiment']}",

        f"Timestamp  : {metrics['timestamp']}",

        "",

        "-" * 40,

        "Model",

        "-" * 40,

        f"Checkpoint : {metrics['weights']}",

        f"Architecture : {metrics['model']}",

        f"Image Size : {metrics['image_size']}",

        f"Batch Size : {metrics['batch_size']}",

        f"Device     : {metrics['device']}",

        "",

        "-" * 40,

        "Dataset",

        "-" * 40,

        f"Dataset YAML : {metrics['dataset']}",

        f"Evaluation Split : {metrics['split']}",

        f"Images : {metrics['test_images']}",

        f"Instances : {metrics['test_instances']}",

        "",

        "-" * 40,

        "Test Metrics",

        "-" * 40,

        f"Precision : {metrics['precision']:.4f}",

        f"Recall    : {metrics['recall']:.4f}",

        f"mAP50     : {metrics['map50']:.4f}",

        f"mAP50-95  : {metrics['map5095']:.4f}",

        "",

        "-" * 40,

        "Inference Speed (ms/image)",

        "-" * 40,

        f"Preprocess : {metrics['speed_ms_per_image']['preprocess']:.2f}",

        f"Inference  : {metrics['speed_ms_per_image']['inference']:.2f}",

        f"Postprocess: {metrics['speed_ms_per_image']['postprocess']:.2f}",

        "",

        "-" * 40,

        "Overall Verdict",

        "-" * 40,

        rating,

        verdict,

        "",

        "-" * 40,

        "Reproducibility",

        "-" * 40,

        f"Confidence Threshold : {metrics['confidence_threshold']}",

        f"Evaluation Split     : {metrics['split']}",

        ""

    ]

    with open(

        PATHS["report"],

        "w",

        encoding="utf-8"

    ) as file:

        file.write(
            "\n".join(lines)
        )

# =====================================================
# Run Evaluation
# =====================================================

RESULTS = evaluate_model()

METRICS = save_metrics(
    RESULTS
)

save_report(
    METRICS
)

organize_outputs(
    RESULTS
)

print()

print(
    "Evaluation completed successfully."
)

print(
    f"Metrics     : {PATHS['metrics']}"
)

print(
    f"Report      : {PATHS['report']}"
)

print(
    f"Plots       : {PATHS['plots']}"
)

print(
    f"Predictions : {PATHS['predictions']}"
)

print()

print("=" * 55)

print(
    f"Precision : {METRICS['precision']:.4f}"
)

print(
    f"Recall    : {METRICS['recall']:.4f}"
)

print(
    f"mAP50     : {METRICS['map50']:.4f}"
)

print(
    f"mAP50-95  : {METRICS['map5095']:.4f}"
)

print("=" * 55)

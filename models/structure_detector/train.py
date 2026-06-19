from ultralytics import YOLO


model = YOLO(
    "yolov8n.pt"
)

model.train(
    data="annotations/dataset.yaml",
    epochs=50,
    imgsz=640,
    batch=8,
    project="models/structure_detector",
    name="chemical_detector_v1"
)
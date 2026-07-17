from pathlib import Path

from ultralytics import YOLO


class PageClassifier:

    def __init__(
        self,
        weights,
        device="cpu",
        confidence=0.50
    ):

        self.weights = Path(weights)
        self.device = device
        self.confidence = confidence

        if not self.weights.exists():
            raise FileNotFoundError(self.weights)

        self.model = YOLO(str(self.weights))

    def predict(self, image):

        image = Path(image)

        results = self.model.predict(
            source=str(image),
            device=self.device,
            verbose=False
        )[0]

        probs = results.probs

        class_index = int(probs.top1)

        confidence = float(probs.top1conf)

        label = results.names[class_index]

        if confidence < self.confidence:
            label = "uncertain"

        return {
            "image": str(image),
            "label": label,
            "confidence": confidence
        }

    def predict_batch(self, images):

        return [
            self.predict(image)
            for image in images
        ]
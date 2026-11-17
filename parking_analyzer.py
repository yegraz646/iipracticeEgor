from __future__ import annotations

import os
import time
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

# COCO: car, motorcycle, bus, truck
VEHICLE_CLASSES = {2, 3, 5, 7}
RED = (35, 35, 235)  # BGR


class ParkingAnalyzer:
    """Обнаруживает транспортные средства и выделяет их красными рамками."""

    def __init__(self) -> None:
        self.model = None
        self.model_status = "not_loaded"
        self.weights = os.getenv("YOLO_WEIGHTS", "yolov8n.pt")

    def _load_model(self):
        if self.model is None:
            from ultralytics import YOLO
            self.model = YOLO(self.weights)
            self.model_status = f"loaded:{self.weights}"
        return self.model

    def analyze(self, image_path: Path):
        started = time.perf_counter()
        frame = cv2.imread(str(image_path))
        if frame is None:
            raise ValueError("Не удалось открыть изображение")

        height, width = frame.shape[:2]
        prediction = self._load_model()(frame, verbose=False, conf=0.25)[0]
        output = frame.copy()
        occupied_count = 0

        for box in prediction.boxes:
            if int(box.cls[0].item()) not in VEHICLE_CLASSES:
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            x1 = max(0, min(width - 1, x1))
            y1 = max(0, min(height - 1, y1))
            x2 = max(0, min(width - 1, x2))
            y2 = max(0, min(height - 1, y2))
            if x2 <= x1 or y2 <= y1:
                continue

            cv2.rectangle(
                output, (x1, y1), (x2, y2),
                RED, max(2, width // 500), cv2.LINE_AA
            )
            occupied_count += 1

        elapsed = round((time.perf_counter() - started) * 1000, 1)
        rgb = cv2.cvtColor(output, cv2.COLOR_BGR2RGB)
        return {
            "image": Image.fromarray(rgb),
            "occupied": occupied_count,
            "processing_ms": elapsed,
        }

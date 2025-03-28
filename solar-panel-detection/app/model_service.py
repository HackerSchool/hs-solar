import os
import uuid

from flask import Flask

from PIL import Image, ImageOps
from io import BytesIO

from ultralytics import YOLO
import numpy as np


__model = None
__imgs_path = ""


def init_app(app: Flask):
    global __imgs_path, __model
    __imgs_path = app.config.get("STATIC_FOLDER", "").rstrip("/") + "/results"
    if not os.path.exists(__imgs_path):
        os.mkdir(__imgs_path)
    __model = YOLO(app.config.get("YOLO_PATH", ""))


def predict_image(image: BytesIO) -> dict:
    image = Image.open(image)
    img = ImageOps.fit(image, (400, 400), Image.LANCZOS)
    img = np.asarray(img.convert("RGB"))

    img_id = str(uuid.uuid4())
    if os.path.exists(__imgs_path + "/" + img_id):
        os.remove(__imgs_path + "/" + img_id)

    results = __model.predict(
        img, imgsz=400, save=True, project=__imgs_path, name=img_id
    )

    for result in results:
        boxes = (
            result.boxes.xyxy.cpu().numpy()
        )  # bounding boxes in (x1, y1, x2, y2) format
        scores = result.boxes.conf.cpu().numpy()  # confidence scores
        class_ids = result.boxes.cls.cpu().numpy()  # class indices

        results = []
        for box, score, class_id in zip(boxes, scores, class_ids):
            results.append(
                {
                    "class": class_ids,
                    "confidence": scores,
                    "bounding box": [*box],
                }
            )

        return {"results": [], "image": f"results/{img_id}"}

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
    )  # always one image, one result

    if len(results) == 0:
        raise ValueError("No results from prediction.")

    result_response: list = []

    boxes = (
        results[0].boxes.xyxy.cpu().numpy().tolist()
    )  # bounding boxes in (x1, y1, x2, y2) format
    scores = results[0].boxes.conf.cpu().numpy().tolist()  # confidence scores
    class_ids = results[0].boxes.cls.cpu().numpy().tolist()  # class indices
    for box, score, class_id in zip(boxes, scores, class_ids):
        result_response.append(
            {
                "label": results[0].names[int(class_id)],
                "score": score,
                "bounding_box": [*box],
            }
        )

    return {
        "results": result_response,
        "image": f"results/{img_id}",
    }

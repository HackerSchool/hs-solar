import os
import uuid

from PIL import Image, ImageOps
from io import BytesIO

from ultralytics import YOLO
import numpy as np


class ModelService:
    def __init__(self, model_path: str, images_folder: str):
        self.__model = YOLO(model_path)
        self.__imgs_folder = images_folder.rstrip("/") + "/results"
        if self.__imgs_folder.startswith("../"):
            self.__imgs_folder = self.__imgs_folder[3:]

        if not os.path.exists(self.__imgs_folder):
            os.makedirs(self.__imgs_folder)

    def predict_image(self, image: BytesIO) -> dict:
        image = Image.open(image)
        img = ImageOps.fit(image, (416, 416), Image.LANCZOS)
        img = img.convert("RGB")

        img_id = str(uuid.uuid4())
        if os.path.exists(self.__imgs_folder + "/" + img_id):
            os.remove(self.__imgs_folder + "/" + img_id)

        results = self.__model.predict(
            img, imgsz=416, save=True, project=self.__imgs_folder, name=img_id
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

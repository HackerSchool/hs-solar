import os


class AppConfig:
    STATIC_FOLDER = "../static/"
    TEMPLATE_FOLDER = "templates/"
    YOLO_PATH = os.getenv("YOLO_PATH", "")
    MAPS_API_KEY = os.getenv("MAPS_API_KEY", "")

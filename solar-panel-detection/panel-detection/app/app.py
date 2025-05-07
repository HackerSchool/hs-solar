from flask import Flask, request, render_template, redirect, abort, json

from config import AppConfig
from model_service import ModelService
from maps_service import MapsService
import utils

app = Flask(
    __name__,
    template_folder=AppConfig.TEMPLATE_FOLDER,
    static_folder=AppConfig.STATIC_FOLDER,
    static_url_path="",
)
app.config.from_object(AppConfig)

model_service = ModelService(AppConfig.YOLO_PATH, AppConfig.STATIC_FOLDER)
maps_service = MapsService(AppConfig.MAPS_API_KEY)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predict_image", methods=["POST"])
def predict_image():
    if "image" not in request.files:
        abort(400, description="No image part in the request")

    image_file = request.files["image"]

    try:
        predictions: dict = model_service.predict_image(image_file.stream)
    except Exception as e:
        abort(500, description=f"Internal server error: {str(e)}")

    return predictions


@app.route("/predict_coordinates", methods=["GET"])
def predict_coordinates():
    if "lat" not in request.args:
        abort(400, description="Missing 'lat' query parameters")
    if "long" not in request.args:
        abort(400, description="Missing 'long' query parameters")

    try:
        lat = float(request.args.get("lat"))
        long = float(request.args.get("long"))
    except (TypeError, ValueError):
        abort(400, description="Invalid or missing 'lat' or 'long' query parameters.")

    try:
        image = maps_service.get_image(lat, long)
    except Exception as e:
        abort(500, description=f"Could't complete request to Google Maps: {str(e)}")

    try:
        predictions: dict = model_service.predict_image(image)
    except Exception as e:
        abort(500, description=f"Internal server error: {str(e)}")

    detections = []
    for res in predictions["results"]:
        top_x, top_y = res["bounding_box"][0], res["bounding_box"][1]
        bot_x, bot_y = res["bounding_box"][2], res["bounding_box"][3]

        corners = ((top_x, top_y), (bot_x, top_y), (bot_x, bot_y), (top_x, bot_y))
        detections += [
            {
                "corners": utils.bbox_pixels_to_coords(corners, lat, long, 20),
                "confidence": res["score"],
            },
        ]

    return {"image": predictions["image"], "detections": detections}


@app.route("/results/<uuid>")
def result_image(uuid):
    return redirect(f"/results/{uuid}/image0.jpg")


from werkzeug.exceptions import HTTPException


@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    response = e.get_response()
    response.data = json.dumps(
        {
            "code": e.code,
            "name": e.name,
            "description": e.description,
        }
    )
    response.content_type = "application/json"
    return response

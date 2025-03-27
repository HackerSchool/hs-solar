from flask import Flask
from flask import request
from flask import jsonify
from flask import render_template
from flask import redirect

import model_service
import config

app = Flask(
    __name__,
    template_folder=config.AppConfig.TEMPLATE_FOLDER,
    static_folder=config.AppConfig.STATIC_FOLDER,
    static_url_path="",
)
app.config.from_object(config.AppConfig)

model_service.init_app(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No image part in the request"}), 400
    image_file = request.files["image"]

    try:
        predictions: dict = model_service.predict_image(image_file.stream)
    except Exception as e:
        return jsonify({"error": "Internal server error", "message": str(e)}), 500

    return jsonify(predictions)


@app.route("/results/<uuid>")
def result_image(uuid):
    return redirect(f"/results/{uuid}/image0.jpg")

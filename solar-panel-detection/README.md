Here we have a small flask application to detect solar panels in aerial images. 

# Object Detection
The application uses a YOLOv8 large model trained for solar panels detection. To train a model please see the `model_training` folder, which is a copy of https://github.com/sanjaboekle/solar_panel_object_detection with slight adjustments to our use case. If you want you can also use our trained model that can be found [here]("https://drive.google.com/file/d/19t13gnt_ca1ZbydcphA6H72n1OYAVuQ3/view?usp=sharing").

# Model

You can either train your model as explained in [Object Detection](#object-detection) or download our model running

```sh
pip install --upgrade gdown
gdown 19t13gnt_ca1ZbydcphA6H72n1OYAVuQ3 # model
gdown 1O2-prSI8FjUeYndnvJaMwEzTj1yN8YtA # evaluation metrics
```

# Docker

You run it with Docker, which automatically downloads the model.

First build the image, this might take a while, but you only need to do it once:
```sh
docker build -t hs-solar:latest .
```

Then run the container:
```sh
docker run -p 5000:5000 -e MAPS_API_KEY=<YOUR-GOOGLE-CLOUD-API-KEY> hs-solar
```

# Endpoints

You can browse to the `/` and you will have an interface where you can upload photos and see the corresponding detection result.

For integration with other applications a request to `/predict_coordinates?lat=<latitude>&long=<longitude>` can be made.
The endpoint returns a JSON response with a list of the detected solar panels. The response has the confidence score of each detected panel and the coordinates of its corners, from top left and following a clockwise orientation.
You can also view the result of the detection by browsing to `/results/<uuid>`.

Example:
```json
{
  "detections": [
    {
      "confidence": 0.6933447122573853,
      "corners": [
        [
          38.68975936142172,
          -9.312412767056307
        ],
        [
          38.68975936142172,
          -9.312361813475112
        ],
        [
          38.68972286418007,
          -9.312361813475112
        ],
        [
          38.68972286418007,
          -9.312412767056307
        ]
      ]
    }
  ],
  "image": "results/6fc540d9-e63f-4318-aef7-ae8f9b999beb"
}
```

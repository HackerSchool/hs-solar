Here we have a small flask application to detect solar panels in aerial images. 

# Object Detection
The application uses a YOLOv8 large model trained for solar panels detection. To train a model please see the `model_training` folder, which is a copy of https://github.com/sanjaboekle/solar_panel_object_detection with slight adjustments to our use case. If you want you can also use our trained model that can be found [here]("https://drive.google.com/file/d/19t13gnt_ca1ZbydcphA6H72n1OYAVuQ3/view?usp=sharing").

# Installation

The development was made using Python 3.13.2.

To install simply run
`pip install -r requirements.txt`

## Model

You can either train your model as explained in [Object Detection](#object-detection) or download our model running

```sh
pip install --upgrade gdown
gdown 19t13gnt_ca1ZbydcphA6H72n1OYAVuQ3 # model
gdown 1O2-prSI8FjUeYndnvJaMwEzTj1yN8YtA # evaluation metrics
```

# Running

Place the path to your model in `config.py` and run `flask run` in the `app` directory.

# Endpoints

Ideally this application will be integrated into a wider system expecting images in `/predict` endpoint and returning JSON with bounding box values and confidence levels of solar panels detected. It also stores the image with labels on the detected solar panels and returns a reference to it for visual inspection.

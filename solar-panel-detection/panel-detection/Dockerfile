FROM python:3.11-slim

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

WORKDIR /hs-solar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

RUN pip install --upgrade gdown
RUN gdown 19t13gnt_ca1ZbydcphA6H72n1OYAVuQ3

ENV YOLO_PATH="best.torchscript"
ENV FLASK_APP="app/app.py"

CMD ["flask", "run", "--host=0.0.0.0"]
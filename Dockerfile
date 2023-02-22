FROM python:3.8.10

WORKDIR /app

COPY ./main.py ./
COPY ./config.json ./
COPY ./requirements.txt ./

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

RUN pip3 install -r requirements.txt

CMD ["python", "./main.py"]


import json
import os
import time

from flask import Flask, jsonify


output_folder = "/opt/deepdream/outputs" 
path_prefix = "/outputs"

output_file = "images.json"
images_extensions = [
    ".jpg",
    ".jpeg",
    ".png",
]


app = Flask(__name__)
app.debug = True

@app.route("/api/ping")
def home():
    return "pong"


def list_output_images(output_folder):
    return [
        f for f in os.listdir(output_folder) 
        if os.path.splitext(f)[-1].lower() in images_extensions
    ]


def generate_images_dict(images):
    result = []
    for index, f in enumerate(images):
        result.append({
            "id": index,
            "name": f,
            "src": "{}/{}".format(path_prefix, f),
        })
    return result


@app.route("/api/outputs")
def outputs():
    images = list_output_images(output_folder)
    result = generate_images_dict(images)
    return json.dumps(result, indent=4)

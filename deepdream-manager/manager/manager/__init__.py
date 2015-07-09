import json
import os
import time
import uuid

from flask import Flask, jsonify, request, redirect, url_for, render_template, abort
from flask.ext.uploads import (
    UploadSet, configure_uploads, IMAGES,
    UploadNotAllowed
)
import requests

output_folder = "/opt/deepdream/outputs" 
input_folder = "/opt/deepdream/inputs" 
path_prefix = "/outputs"

output_file = "images.json"
images_extensions = [
    ".jpg",
    ".jpeg",
    ".png",
]


app = Flask(__name__)
app.debug = True

app.config['UPLOADED_PHOTOS_DEST'] = input_folder
uploaded_photos = UploadSet('photos', IMAGES)
configure_uploads(app, uploaded_photos)


@app.route("/api/ping")
def home():
    return "pong"


def download_file(url, local_filename):
    # todo check mimetype
    # todo check size
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()


@app.route('/api/upload', methods=['GET', 'POST'])
def upload():
    """Upload a new file."""
    if request.method == 'POST':

        filename = str(uuid.uuid4()) + ".jpg"

        url = request.form.get("url", None)
        if url:
            path = os.path.join(input_folder, filename)
            download_file(url, path)
            return redirect(url_for('view', path=filename))


        photo = request.files.get('photo', None)
        if photo:
            try:
                filename = uploaded_photos.save(photo, name=filename)
            except UploadNotAllowed:
                return abort(403)

        return redirect(url_for('view', path=filename))

    return render_template("upload.html")


def list_images(output_folder):
    return sorted([
        f for f in os.listdir(output_folder) 
        if os.path.splitext(f)[-1].lower() in images_extensions
    ])


def generate_images_dict(images):
    result = []
    for index, f in enumerate(images):
        result.append({
            "id": index,
            "name": f,
            "details": url_for('view', path=f),
            "src": "{}/{}".format(path_prefix, f),
        })
    return result


@app.route("/api/stats")
def stats():
    input_list = sorted(list_images(input_folder))
    output_list = sorted(list_images(output_folder))

    result = []

    for f in input_list:
        result.append(
            (f, f in output_list, url_for('view', path=f))
        )

    html = "<ul>"
    for f, finished, link in result:
        html += """<li><a href="%s">%s - %s</a>""" % (link, f, finished)
    html += "</ul>"
    return html
            
@app.route("/api/stats2")
def stats2():
    input_list = sorted(list_images(input_folder))
    output_list = sorted(list_images(output_folder))

    result = []

    for f in input_list:
        result.append(
            (f, f in output_list, url_for('view', path=f))
        )
    return render_template("images.html", images=result)


@app.route("/api/view/<path>")
def view(path):
    return render_template("compare.html", image=path)


@app.route("/api/outputs")
def outputs():
    images = list_images(output_folder)
    result = generate_images_dict(images)
    return json.dumps(result, indent=4)

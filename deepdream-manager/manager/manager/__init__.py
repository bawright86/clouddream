import json
import os
import time

from flask import Flask, jsonify, request, redirect, url_for
from flask.ext.uploads import (
    UploadSet, configure_uploads, IMAGES,
    UploadNotAllowed
)

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


@app.route('/api/upload', methods=['GET', 'POST'])
def upload():
    """Upload a new file."""
    if request.method == 'POST':
        photo = request.files.get('photo')
        try:
            filename = uploaded_photos.save(photo)
        except UploadNotAllowed:
            return "nope"

        return redirect(url_for('home'))
    return (
        u'<form method="POST" enctype="multipart/form-data">'
        u'  <input name="photo" type="file">'
        u'  <button type="submit">Upload</button>'
        u'</form>'
    )

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
            

@app.route("/api/view/<path>")
def view(path):
    return """
        <img src="/inputs/%s"><img src="/outputs/%s">
    """ % (path, path)


@app.route("/api/outputs")
def outputs():
    images = list_images(output_folder)
    result = generate_images_dict(images)
    return json.dumps(result, indent=4)

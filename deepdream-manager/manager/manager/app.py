import json
import os
import time
import uuid

from flask import Flask, jsonify, request, redirect, url_for, render_template, abort
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.uploads import (
    UploadSet, configure_uploads, IMAGES,
    UploadNotAllowed
)
from redis import Redis
from rq import Queue
import requests


from models import (
    Image,
    Job,
    db,
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
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////opt/deepdream/database.db'


app.config['UPLOADED_PHOTOS_DEST'] = input_folder
uploaded_photos = UploadSet('photos', IMAGES)
configure_uploads(app, uploaded_photos)


redis = Redis(
    host=os.getenv("DEEPDREAM_REDIS_PORT_6379_TCP_ADDR"),
    port=os.getenv("DEEPDREAM_REDIS_PORT_6379_TCP_PORT")
)
compute_queue = Queue('compute', connection=redis)

db.init_app(app)
db.app = app
db.create_all()


def get_or_create_image(filename, folder):
    image = db.session.query(Image).filter_by(
        filename=filename, folder=folder
    ).first()
    if not image:
        image = Image(
            filename=filename, 
            folder=folder,
        )
        db.session.add(image)
        db.session.commit()
    return image


@app.route("/api/image/<image_id>/job", methods=["POST"])
def new_job(image_id):
    image = Image.query.get(image_id)
    if not image:
        abort(404)

    try:
        parameters = request.form["parameters"]
        json.loads(parameters)
    except:
        abort(400)

    job = Job(source_image_id=image_id,
              parameters=parameters)
    db.session.add(job)
    db.session.commit()

    compute_queue.enqueue_call(
        func='worker.process_job', timeout=3600, kwargs={"job_id": job.id}
    )
    return redirect(url_for('view', image_id=image.id))


@app.route("/api/scan")
def scan():

    for folder in [input_folder, output_folder]:
        for filename in list_images(folder):
            get_or_create_image(filename, folder)

    for input_image in Image.query.filter_by(folder=input_folder):
        result_images = Image.query.filter(
            Image.folder == output_folder, 
            Image.filename == input_image.filename
        )
        for output_image in result_images:
            job = Job.query.filter(
                Job.source_image_id == input_image.id, 
                Job.result_image_id == output_image.id,
            ).first()
            if not job:
                job = Job(
                    source_image_id=input_image.id,
                    result_image_id=output_image.id,
                )
                db.session.add(job)
                db.session.commit()

    return str(db.session.query(Image).all())


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
            image = get_or_create_image(filename, input_folder)
            return redirect(url_for('view', image_id=image.id))


        photo = request.files.get('photo', None)
        if photo:
            try:
                filename = uploaded_photos.save(photo, name=filename)
            except UploadNotAllowed:
                return abort(403)
        image = get_or_create_image(filename, input_folder)
        return redirect(url_for('view', image=image.id))

    return render_template("upload.html")


def list_images(outoput_folder):
    return sorted([
        f for f in os.listdir(output_folder) 
        if os.path.splitext(f)[-1].lower() in images_extensions
    ])


@app.route("/api/image")
def images():
    source_images = Image.query.join((Job, Job.source_image_id==Image.id)).all()
    return render_template("images.html", source_images=source_images)
            

@app.route("/api/job")
def jobs():
    jobs = Job.query.order_by(Job.id)
    return render_template("jobs.html", jobs=jobs)

@app.route("/api/image/<image_id>")
def view(image_id):
    image = Image.query.get(image_id)
    return render_template("image.html", image=image)

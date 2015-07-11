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
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////opt/deepdream/database.db'
db = SQLAlchemy(app)

app.config['UPLOADED_PHOTOS_DEST'] = input_folder
uploaded_photos = UploadSet('photos', IMAGES)
configure_uploads(app, uploaded_photos)


class Image(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    folder = db.Column(db.String(100), nullable=False)
    source = db.Column(db.String(300), nullable=True)
    added = db.Column(db.DateTime, default=db.func.now())
    
    @property
    def fullpath(self):
        return os.path.join(self.folder, self.filename)

    def __repr__(self):
        return "<Image id=%s>" % self.id

class Job(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    source_image_id = db.Column(db.Integer, db.ForeignKey(Image.id))
    result_image_id = db.Column(db.Integer, db.ForeignKey(Image.id))
    parameters = db.Column(db.String(300), nullable=True)
    started = db.Column(db.DateTime, nullable=True)
    finished = db.Column(db.DateTime, nullable=True)
    log = db.Column(db.String(3000), nullable=True)

    source_image = db.relationship(
        'Image', backref=db.backref('jobs', lazy='dynamic'),
        foreign_keys=[source_image_id]
    )
    result_image = db.relationship(
        'Image', foreign_keys=[result_image_id]
    )

    def __repr__(self):
        return "<Job id=%s source_image_id=%s, result_image_id=%s>" % (
            self.id, self.source_image_id, self.result_image_id
        )

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


@app.route("/api/stats")
def stats():
    source_images = Image.query.join((Job, Job.source_image_id==Image.id)).all()
    return render_template("home.html", source_images=source_images)
            

@app.route("/api/view/<image_id>")
def view(image_id):
    image = Image.query.get(image_id)
    return render_template("compare.html", image=image)

import datetime
import os

from sqlalchemy.orm.session import object_session

from flask.ext.sqlalchemy import SQLAlchemy
from utils import create_thumbnail

db = SQLAlchemy()


class Image(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    folder = db.Column(db.String(100), nullable=False)
    source = db.Column(db.String(300), nullable=True)
    added = db.Column(db.DateTime, default=db.func.now())
    
    def create_thumbnail(self, size=(500, 333)):
        _, thumbnail_filename = create_thumbnail(self.fullpath, size)
        folder, filename = os.path.split(thumbnail_filename)
        thumbnail = Thumbnail(
            image_id=self.id, 
            width=size[0], 
            height=size[1], 
            folder=folder, 
            filename=filename
        )
        object_session(self).add(thumbnail)
        object_session(self).commit()

    @property
    def fullpath(self):
        return os.path.join(self.folder, self.filename)

    def __repr__(self):
        return "<Image id=%s>" % self.id

class Thumbnail(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey(Image.id))
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    filename = db.Column(db.String(100), nullable=False)
    folder = db.Column(db.String(100), nullable=False)

    image = db.relationship(
        'Image', backref=db.backref('thumbnails', lazy='dynamic'),
        foreign_keys=[image_id]
    )

    @property
    def fullpath(self):
        return os.path.join(self.folder, self.filename)

    def __repr__(self):
        return "<Thumbnail id=%s>" % self.id
    


class Job(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    source_image_id = db.Column(db.Integer, db.ForeignKey(Image.id))
    result_image_id = db.Column(db.Integer, db.ForeignKey(Image.id))
    parameters = db.Column(db.String(300), nullable=False, default="{}")
    started = db.Column(db.DateTime, nullable=True)
    finished = db.Column(db.DateTime, nullable=True)
    log = db.Column(db.String(3000), nullable=True)
    status = db.Column(db.String(30), nullable=False, default="PENDING")

    source_image = db.relationship(
        'Image', backref=db.backref('jobs', lazy='dynamic'),
        foreign_keys=[source_image_id]
    )
    result_image = db.relationship(
        'Image', foreign_keys=[result_image_id]
    )

    @property
    def duration(self):
        if not self.started:
            return None

        if self.finished:
            finished = self.finished
        else:
            finished = datetime.datetime.utcnow()
            
        return finished - self.started
        

    def __repr__(self):
        return "<Job id=%s source_image_id=%s, result_image_id=%s>" % (
            self.id, self.source_image_id, self.result_image_id
        )

import os

from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()


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

    def __repr__(self):
        return "<Job id=%s source_image_id=%s, result_image_id=%s>" % (
            self.id, self.source_image_id, self.result_image_id
        )

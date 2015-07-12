import datetime
import json
import os
import uuid

import caffe

from app import db, Job, get_or_create_image

from deepdream import process_image


def process_job(job_id):
    job = Job.query.get(job_id)
    if not job or job.status in ("COMPLETED", "FAILED"):
        return
    
    try:
        job.status = "PROCESSING"
        job.started = datetime.datetime.utcnow()
        db.session.commit()

        output_folder = "/opt/deepdream/outputs"

        parameters_dict = json.loads(job.parameters)
        output_filename = str(uuid.uuid4()) + ".jpg"
        output_path = os.path.join(output_folder, output_filename) 
        process_image(job.source_image.fullpath, output_path, **parameters_dict)

        image = get_or_create_image(output_filename, output_folder)
        job.result_image_id = image.id
        job.status = "COMPLETED"
        job.finished = datetime.datetime.utcnow()
        db.session.commit()
    except Exception as e:
        job.status = "FAILED"
        job.log = str(e)
        db.session.commit()
        raise


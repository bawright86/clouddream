import os
from PIL import Image, ImageOps


def create_thumbnail(path, size):
    image = Image.open(path)
    
    image.thumbnail(size, Image.ANTIALIAS)
    folder, filename = os.path.split(path)
    thumbnail_filename = os.path.join(
        folder,
        "tn_%s" % filename,
    )
    image.save(thumbnail_filename)
    return image, thumbnail_filename

    

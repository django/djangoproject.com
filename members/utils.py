from io import BytesIO

from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image


def get_temporary_image():
    # Testing utility.
    io = BytesIO()
    size = (200, 200)
    color = (255, 0, 0, 0)
    image = Image.new('RGB', size, color)
    image.save(io, format='JPEG')
    image_file = InMemoryUploadedFile(io, None, 'foo.jpg', 'jpeg', 1, None)
    image_file.seek(0)
    return image_file

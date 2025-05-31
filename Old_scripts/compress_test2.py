import pyguetzli
from PIL import Image

image = Image.open("./_DSC0155.jpg")
optimized_jpeg = pyguetzli.process_pil_image(image, quality=85)

with open('new.jpg', 'wb')as fp:
    fp.write(optimized_jpeg)
    fp.close()

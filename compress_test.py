import pyguetzli

input_jpeg_bytes = open("./_DSC0155.jpg", "rb").read()
optimized_jpeg = pyguetzli.process_jpeg_bytes(input_jpeg_bytes, quality=85)
input_jpeg_bytes.close()


with open('new.jpg', 'wb')as fp:
    fp.write(optimized_jpeg)
    fp.close()

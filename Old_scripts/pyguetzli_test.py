import pyguetzli

input_jpeg_bytes = open("./pics/test.jpg", "rb").read()
optimized_jpeg = pyguetzli.process_jpeg_bytes(input_jpeg_bytes)
file = open("./pics/optimized.jpg","wb")
file.write(input_jpeg_bytes)
file.close()
    

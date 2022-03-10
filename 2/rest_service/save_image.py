import base64

with open("image_base64", "r") as f:
    base64_img = f.read()

base64_bytes = base64_img.encode("utf-8")
with open("image_saved.jpg", "wb") as image:
    image.write(base64.decodebytes(base64_bytes))
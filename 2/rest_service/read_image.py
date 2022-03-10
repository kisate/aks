import base64

with open("image.jpg", "rb") as image:
    b64string = base64.b64encode(image.read())
print(b64string.decode('utf-8'))
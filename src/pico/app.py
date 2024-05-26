import requests

url = 'http://<server-ip>:5000/predict'
image_path = 'path/to/image.jpg' 

with open(image_path, 'rb') as image_file:
    files = {'file': image_file}
    response = requests.post(url, files=files)

print(response.json())

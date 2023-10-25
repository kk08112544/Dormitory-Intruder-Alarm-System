# import requests

# url = 'https://notify-api.line.me/api/notify'
# token = 'G4JlVIkXZmgVCa2UhWa6VTGXCUZqSbC0lJn3DuBBPHv'
# message = "Hello World"
# headers = {
#     'Content-Type': 'application/x-www-form-urlencoded',
#     'Authorization': f'Bearer {token}'  # Note the space after 'Bearer'
# }

# data = {'message': message}

# response = requests.post(url, headers=headers, data=data)

# print(response.text)
import requests

url = 'https://notify-api.line.me/api/notify'
token = 'G4JlVIkXZmgVCa2UhWa6VTGXCUZqSbC0lJn3DuBBPHv'
message = "Hello World"

# Prepare the headers with your authorization token
headers = {
    'Authorization': f'Bearer {token}'
}

# Capture an image (you'll need to install OpenCV for this)
import cv2
camera = cv2.VideoCapture(0)  # Use the default camera (0) or specify a file path
return_code, image = camera.read()
camera.release()
cv2.imwrite('captured_image.jpg', image)

# Open the image file and send it
with open('captured_image.jpg', 'rb') as file:
    image_data = {'imageFile': file}
    data = {'message': message}

    # Send the message and image using a POST request
    response = requests.post(url, headers=headers, data=data, files=image_data)

print(response.text)

'''
This code hasn't yet been tested!  Freshly pulled from ChatGPT.
'''
import face_recognition
from PIL import Image
import requests
from io import BytesIO

def crop_faces_from_image(image_url):
    # Load the image from the URL
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))

    # Convert the image to a numpy array
    img_array = face_recognition.load_image_file(BytesIO(response.content))

    # Find all face locations in the image
    face_locations = face_recognition.face_locations(img_array)

    if not face_locations:
        print(f"No faces found in the image: {image_url}")
        return []

    # Initialize a list to store cropped face PNGs
    cropped_faces = []

    # Iterate through each face found in the image
    for i, (top, right, bottom, left) in enumerate(face_locations):
        # Crop the image to the detected face
        cropped_img = img.crop((left, top, right, bottom))

        # Convert the cropped image to PNG format
        cropped_img_png = BytesIO()
        cropped_img.save(cropped_img_png, format="PNG")
        cropped_img_png.seek(0)

        # Add the PNG image to the list
        cropped_faces.append(cropped_img_png)

    return cropped_faces

# Example usage
image_url = "https://example.com/path/to/group_image.jpg"
png_faces = crop_faces_from_image(image_url)

# Save each PNG file locally for verification
for i, face_png in enumerate(png_faces):
    with open(f"cropped_face_{i + 1}.png", "wb") as f:
        f.write(face_png.getvalue())

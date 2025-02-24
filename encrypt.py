import io
import cv2
import numpy as np
from utils import text_to_bin
from flask import request, send_file

END_MARKER = "<<<END>>>"

def hide_message(image_bytes, message, password=""):
    """Hides a message inside an image using LSB encoding."""
    file_bytes = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    
    if img is None:
        return None, "Invalid image file!"

    if password:
        message = f"PASSWORD:{password}::{message}"
    
    message += END_MARKER  # Append END_MARKER
    print("Message: ", message)
    binary_msg = text_to_bin(message)
    max_bytes = img.shape[0] * img.shape[1] * 3 // 8

    if len(binary_msg) > max_bytes * 8:
        return None, "Message too long for the image! Try encrypting with larger image size."

    flat_pixels = img.flatten()
    for i in range(len(binary_msg)):
        flat_pixels[i] = (flat_pixels[i] & 0xFE) | int(binary_msg[i])

    img = flat_pixels.reshape(img.shape)

    success, encoded_image = cv2.imencode(".png", img)
    if not success:
        return None, "Failed to encode image."

    return io.BytesIO(encoded_image.tobytes()), None

def encrypt_route():
    """Handles encryption request via Flask API."""
    if "image" not in request.files:
        return "Missing image file", 400

    file = request.files["image"]
    password = request.form.get("password", "")

    print("Pass in route: ", password)

    # Handle message input (either text or file)
    if "message" in request.form and request.form["message"]:
        message = request.form["message"]
    elif "messageFile" in request.files and request.files["messageFile"].filename:
        message_file = request.files["messageFile"]
        message = message_file.read().decode("utf-8")
    else:
        return "No message provided", 400

    img_bytes = file.read()
    encrypted_image, error = hide_message(img_bytes, message, password)

    if error:
        return error, 400

    response = send_file(encrypted_image, as_attachment=True, download_name="encrypted.png", mimetype="image/png")
    
    return response

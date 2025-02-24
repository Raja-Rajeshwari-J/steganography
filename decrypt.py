import cv2
import numpy as np
from utils import bin_to_text
from flask import request, jsonify

END_MARKER = "<<<END>>>"

def extract_message(image_bytes, password=""):
    """Extracts a hidden message from an image using LSB decoding."""
    file_bytes = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    if img is None:
        return None, "Invalid image file!"

    binary_data = []
    flat_pixels = img.flatten()
    
    # Read hidden bits quickly
    for i in range(0, len(flat_pixels), 8):
        byte = "".join(str(flat_pixels[i+j] & 1) for j in range(8))
        binary_data.append(byte)
        extracted_text = bin_to_text("".join(binary_data))
        if END_MARKER in extracted_text:
            break # Stop early if END_MARKER is found
    
    extracted_text = extracted_text.split(END_MARKER)[0]

    warning = None

    # Check for password protection
    if extracted_text.startswith("PASSWORD:"):
        parts = extracted_text.split("::", 1)

        # If message was encrypted with a password
        if len(parts) == 2:
            stored_password, extracted_text = parts
            stored_password = stored_password.replace("PASSWORD:", "")

            if not password:
                return None, "This message requires a password!"
            
            if stored_password != password:
                return None, "Incorrect password!"
    elif password:
        warning = "No password is required"

    return extracted_text, warning

def decrypt_route():
    """Handles decryption request via Flask API."""
    if "image" not in request.files:
        return jsonify({"error": "Missing image file"}), 400

    file = request.files["image"]
    password = request.form.get("password", "")

    img_bytes = file.read()
    extracted_text, warning = extract_message(img_bytes, password)

    if extracted_text is None:
        return jsonify({"error": warning}), 400
    
    response = {"message" : extracted_text}

    if warning and "No password is required" in warning:
        response["warning"] = "No password was required for this message decryption, but decryption succeeded."

    return jsonify(response)

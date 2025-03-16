from flask import Flask, request, jsonify

from utils.image import (
    convert_from_base64,
    convert_to_base64,
    process_image,
    extract_general_information,
)
from utils.text import process_general_information, process_table_information

app = Flask(__name__)


@app.route("/api/invoice_detector", methods=["POST"])
def predict():

    data = request.get_json()
    image_encoded_str = data["image"]
    # print(base64_encoded_str)

    image = convert_from_base64(image_encoded_str)
    print(image.shape)

    cropped, binary, table_roi, table_information = process_image(image)

    p1_image_encoded_str = convert_to_base64(cropped)
    p2_image_encoded_str = convert_to_base64(binary)
    p3_image_encoded_str = convert_to_base64(table_roi)

    general_information = extract_general_information(cropped)
    profile_info, order_summary = process_general_information(general_information)

    return {
        "original": image_encoded_str,
        "gray": p1_image_encoded_str,
        "binary": p2_image_encoded_str,
        "cropped": p3_image_encoded_str,
        "invoice_information": general_information,
        "profile": profile_info,
        "order_details": table_information,
        "order_summary": order_summary,
    }

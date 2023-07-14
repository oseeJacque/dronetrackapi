import os

import cv2
from flask import Flask, flash, request, redirect, url_for, jsonify, send_file, render_template
from werkzeug.utils import secure_filename

from src.predictions.detect_drone_in_image import detect_drone_in_image

UPLOAD_FOLDER ='E:/AllProject/dronetrackingapi/src/uploadfolder'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def  allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route('/')
def home():
    return render_template("index.html")

@app.route('/detect/upload', methods =['POST', 'GET'])
def upload_image():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return "No file part"
        file = request.files['file']
        if file.name == '':
            flash('No file selected')
            return 'No file selected'
        if file and allowed_file(file.filename):
            filename = secure_filename("image.png")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            predict, image, nbr = detect_drone_in_image(image_path=filepath)
            cv2.imwrite(filepath, image)
            result = {
                'coordinates': predict,
                'image': filepath,
                'num_objects': nbr
            }
            return jsonify(result)
    return 'Method not allowed', 405


if __name__ == '__main__':
    app.run()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

import os
import cv2
import numpy as np
from flask import Flask, flash, request, redirect, url_for, jsonify, send_file, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
from flask import send_from_directory
from moviepy.editor import VideoFileClip

from src.config import base_dir
from src.predictions.detect_drone_in_image import detect_drone_in_image
from src.predictions.tracking_drone_in_video import tracking_drone_in_video

UPLOAD_FOLDER = os.path.join(base_dir, "uploadfolder")
SAVE_OUTPUTS_FILES = os.path.join(base_dir, "uploadfolder/outputs")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'mp4', 'avi', 'mov'}


app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["SAVE_OUTPUTS_FILES"] = SAVE_OUTPUTS_FILES
app.config['SECRET_KEY'] = 'oseesoke'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

def convert_to_mp4(filepath):
    video = VideoFileClip(filepath)
    mp4_filepath = os.path.splitext(filepath)[0] + '.mp4'
    video.write_videofile(mp4_filepath, codec='libx264')
    return mp4_filepath

def allowed_file(filename):

    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/upload')
def index():
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method="post" enctype="multipart/form-data" action="/detect/upload">
      <input type="file" name="file">
      <input type="submit" value="Upload">
    </form>
    '''
@app.route('/api')
def init():
    return "Welcome to my API. Add /upload to test the api"

@app.route('/api/download/<filename>')
def download_file(filename):
    ip_address = request.remote_addr
    print(ip_address)
    return send_from_directory(app.config["SAVE_OUTPUTS_FILES"], filename, as_attachment=True)

@app.route('/detect/upload', methods = ['POST', 'GET'])
def upload_image():
    print(request.method)
    print("Début denregistrement")
    try:
        if request.method == 'POST':
            if 'file' not in request.files:
                print("Received a POST request.")
                #flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            if file.name == '':
                flash('No file selected')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                print(file)
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                filepath2 = os.path.join(app.config['UPLOAD_FOLDER'], "outputs", filename)
                file.save(filepath)

                try:
                    if filename.lower().endswith(('.mp4', '.avi', '.mov')):
                        mp4_filepath = convert_to_mp4(filepath)
                        is_running, video_path, csv_file_path = tracking_drone_in_video(mp4_filepath)
                        csv_filename = os.path.basename(csv_file_path)
                        result = {
                            'video': url_for('download_file', filename=os.path.splitext(filename)[0] + '.mp4', _external=True),
                            'coordonnate': url_for('download_file', filename=os.path.splitext(filename)[0] + '.csv', _external=True),
                            'run': is_running
                        }
                        return jsonify(result)
                    else:
                        predict, image_detect, nbr = detect_drone_in_image(image_path=filepath)
                        cv2.imwrite(filepath2, image_detect)
                        result = {
                            'coordinates': predict,
                            'image': url_for('download_file', filename=filename, _external=True),
                            'num_objects': nbr
                        }
                        return jsonify(result)
                except Exception as e:
                    print(e)
                    return None
        print("Received a not POST request.")
    except Exception as e:
        print(e)
    return "No execution "


######################################## Upload video #############################

"""
def allowed_video_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS
def convert_to_mp4(filepath):
    video = VideoFileClip(filepath)
    mp4_filepath = os.path.splitext(filepath)[0] + '.mp4'
    video.write_videofile(mp4_filepath, codec='libx264')
    return mp4_filepath

@app.route('/upload_video', methods=['POST','GET'])
def upload_video():
    if 'video' not in request.files:
        flash('No video part')
        return "No file path "
    file = request.files['video']
    if file.filename == '':
        flash('No video selected')
        return redirect(request.url)
    if file and allowed_video_file(file.filename):
        filename = secure_filename("video.mp4")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        mp4_filepath = convert_to_mp4(filepath)
        return mp4_filepath
    else:
        flash('Invalid file type')
        return "error"
@app.route('/display_video/<filename>')
def display_video(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return f"The video file '{filename}' has been uploaded and saved at: {filepath}"
"""
@app.route('/process_image', methods=['POST'])
def process_image():
    try:
        image_data = request.get_json()["image_data"]
        image_np = np.array(image_data)
        # Vérifier que l'objet envoyé est bien un tableau numpy 2D (image en niveaux de gris)
        if len(image_np.shape) == 2:

            image_np_color = np.stack((image_np,) * 3, axis=-1)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], "image.png")
            filepath2 = os.path.join(app.config['UPLOAD_FOLDER'], "outputs", "image.png")

            cv2.imwrite(filepath, image_np_color)
            print("Debut de ladetection")
            predict, image_detect, nbr = detect_drone_in_image(image_path=filepath)
            print("Détection effectuée")
            cv2.imwrite(filepath2, image_detect)
            result = {
                'coordinates': predict,
                'image': url_for('download_file', filename="image.png", _external=True),
                'num_objects': nbr
            }
            print(result)
            return jsonify(result)

        else:
            return None

    except Exception as e:
        print(e)
        return None

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

import os
import cv2
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
CORS(app)
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

@app.route('/upload')
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
@app.route('/')
def init():
    return "Welcome to my API. Add /upload to test the api"

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config["SAVE_OUTPUTS_FILES"], filename, as_attachment=True)

@app.route('/detect/upload', methods = ['POST', 'GET'])
def upload_image():
    if request.method == 'POST':
        print("Received a POST request.")
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.name == '':
            flash('No file selected')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            filepath2 = os.path.join(app.config['UPLOAD_FOLDER'], "outputs", filename)
            file.save(filepath)

            if filename.lower().endswith(('.mp4', '.avi', '.mov')):
                mp4_filepath = convert_to_mp4(filepath)
                is_running, video_path, csv_file_path = tracking_drone_in_video(mp4_filepath)
                csv_filename = os.path.basename(csv_file_path)
                result = {
                    'video': url_for('download_file', filename=os.path.splitext(filename)[0] + '.mp4', _external=True),
                    'coordonnate': url_for('download_file', filename=os.path.splitext(filename)[0] + '.csv', _external=True),
                    'run': is_running
                }
            else:
                predict, image_detect, nbr = detect_drone_in_image(image_path=filepath)
                cv2.imwrite(filepath2, image_detect)
                result = {
                    'coordinates': predict,
                    'image': url_for('download_file', filename=filename, _external=True),
                    'num_objects': nbr
                }

            return jsonify(result)
    print("Received a not POST request.")
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

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

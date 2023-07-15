from PIL import Image
import os
from ultralytics import YOLO

current_file = os.path.abspath(__file__)
global base_dir

base_dir = os.path.dirname(current_file)
model_path = os.path.join(base_dir, "model/weights/best.pt")
model = YOLO(model_path)
video_path = os.path.join(base_dir, "runsvideos/video.mp4")
video_input_path = os.path.join(base_dir, "inputvideos/inputvideo.mp4")
image_path = os.path.join(base_dir, "runs/image.png")

outputs = {
    "predictions": []
}

"""
image_input = Image.new("RGB", (500, 500))  # Get image detect


def initialize_outputs_content():
    global outputs, image_input

    outputs = {
    "predictions": []
}

image_input = Image.new("RGB", (500, 500))  


"""
if __name__ == "__main__":
    print(model_path)

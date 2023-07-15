from PIL import Image
from ultralytics import YOLO

model_path = "E:/AllProject/AllProject/dronetrack/src/model/weights/best.pt"
model = YOLO(model_path)
video_path = "E:/AllProject/AllProject/dronetrack/src/runsvideos/video.mp4"
video_input_path = "E:/AllProject/AllProject/dronetrack/src/inputvideos/inputvideo.mp4"
image_path = "E:/AllProject/AllProject/dronetrack/src/runs/image.png"

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


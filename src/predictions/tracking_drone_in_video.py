import csv
import os.path

import cv2
import numpy as np

from src.config import model, video_path, tracker, video_input_path
from src.utils.draw_bounding import draw_boxes

is_running = True

def xyxy_to_xywh2(x1, y1, x2, y2):
    x = x1
    y = y1
    w = x2 - x1
    h = y2 - y1
    return x, y, w, h


def tracking_drone_in_video(filepath):
    filename = os.path.basename(filepath)
    global is_running
    cap = cv2.VideoCapture(filepath)
    ret, frame = cap.read()
    cap_output = cv2.VideoWriter(os.path.join(video_path, os.path.splitext(filename)[0] + '.mp4'), cv2.VideoWriter_fourcc(*'mp4v'), cap.get(cv2.CAP_PROP_FPS), (frame.shape[1], frame.shape[0]))
    # Create csv file
    csv_filename = os.path.splitext(filename)[0] + '.csv'
    csv_filepath = os.path.join(video_path, csv_filename)
    csv_file = open(csv_filepath, 'w', newline='')
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['Frame', 'Object ID', 'X1', 'Y1', 'X2', 'Y2', 'Score'])

    frame_counter = 0
    scores = []
    while ret:
        results = model(frame)
        for result in results:
            detections = []  # List for drone coordonate
            # Get x1, y1, x2, y2, score, class_id from each drone detect
            for r in result.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = r
                x1 = int(x1)
                x2 = int(x2)
                y1 = int(y1)
                y2 = int(y2)
                class_id = int(class_id)
                score = round(score, 2)
                scores.append(score)

                detections.append([x1, y1, x2, y2, score])

            detections = np.array(detections)
            # Remodelage du tableau en dimension 2 si nécessaire
            if detections.ndim == 1:
                detections = detections.reshape((1, -1))
            # Vérification si detections n'est pas vide
            if detections.size > 0:
                # Remodelage du tableau en dimension 2 si nécessaire
                if detections.ndim == 1:
                    detections = detections.reshape((1, -1))

                # Appel de la fonction 'tracker.update' avec les detections
                print(detections)
                tracker.update(frame, detections)
            else:
                pass

            for track in tracker.tracks:
                #x, y, w, h = xyxy_to_xywh2(track.bbox[0], track.bbox[1], track.bbox[2], track.bbox[3],)
                bbox = track.bbox
                track_id = track.track_id

                csv_writer.writerow([frame_counter, track_id, int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3]), scores[frame_counter]])

                identities = [int(i + 1) for i in range(len(tracker.tracks))]
                draw_boxes(frame, bbox=[bbox], identities=identities, offset=(0, 0))

        cap_output.write(frame)
        ret, frame = cap.read()
        frame_counter += 1

    cap.release()
    cap_output.release()
    cv2.destroyAllWindows()
    is_running = False
    return is_running, video_path ,csv_filepath


"""
         if len(results) > 0:
            print((results))
            #cv2.imshow('frame', frame)
            #cv2.waitKey(25)
        #Browser the results
        for result in results:
            detections = [] #List for drone coordonate
            #Get x1, y1, x2, y2, score, class_id from each drone detect
            for r in result.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = r
                x1 = int(x1)
                x2 = int(x2)
                y1 = int(y1)
                y2 = int(y2)
                class_id = int(class_id)
                score = round(score, 2)
                detections.append([x1, y1, x2, y2, score])
            print(detections)
"""


if __name__ == "__main__":
    tracking_drone_in_video()
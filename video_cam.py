# https://www.geeksforgeeks.org/python-opencv-capture-video-from-camera/
import asyncio
import numpy as np
import cv2
import datetime

class VideoCam:

    def __init__(self):
        pass
    
    def start(self):
        # Open the default camera
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        # Get the default fps, frame width and height
        frame_fps = int(cap.get(cv2.CAP_PROP_FPS))
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        print(fourcc)
        out = cv2.VideoWriter('output.mp4', fourcc, frame_fps, (frame_width, frame_height))

        if not cap.isOpened():
            print("Fehler: Die Videoquelle konnte nicht geöffnet werden.")
            return
        
        print("Quelle offen")

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Videoquelle beendet oder Fehler beim Lesen.")
                break

            # Write the frame to the output file
            out.write(frame)

            # Display the captured frame
            cv2.imshow('Camera', frame)

            # Press 'q' to exit the loop
            if cv2.waitKey(1) == ord('q'):
                break
        
        # Release the capture and writer objects
        cap.release()
        out.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    cam = VideoCam()
    cam.start()
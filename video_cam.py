# https://www.geeksforgeeks.org/python-opencv-capture-video-from-camera/
import asyncio
import time
import numpy as np
import cv2
import datetime

class VideoCam:

    def __init__(self):
        # Open the default camera
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
    async def start(self):

        # Get the default fps, frame width and height
        frame_fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter('output.mp4', fourcc, frame_fps, (frame_width, frame_height))

        if not self.cap.isOpened():
            print("Error: Unable to open the video source.")
            return

        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                print("Video source ended or error while reading.")
                break

            # Write the frame to the output file
            out.write(frame)

            # Display the captured frame
            cv2.imshow('Camera', frame)

            # Press 'q' to exit the loop
            if cv2.waitKey(1) == ord('q'):
                break
        
        # Release the capture and writer objects
        self.cap.release()
        out.release()
        cv2.destroyAllWindows()
    
    def get_frame(self):
        return self.cap.read()

# This is an async test function to check video cam is working proper
def get_frame_as_stream():
    cam = VideoCam()
    asyncio.run(cam.start())

# A Function to calculate frame per seconds
def get_fps(array: np.array):
    dt = datetime.datetime.now()
    array = np.append(array, dt)
    match = (dt - datetime.timedelta(seconds=1))
    array = array[array >= match]
    return array, len(array)

# This is a test function to get frame by frame
def get_frame_with_delay(fps: int):
    time_stamp_list = np.array([],dtype=np.int64)
    delay: float = 1 / fps
    cam = VideoCam()
    last_time = time.time()
    while cam.cap.isOpened():
        current_time = time.time()
        delta_time = current_time - last_time
        if delta_time >= delay:
            last_time = current_time
            ret, frame = cam.get_frame()
            if not ret:
                print("Videoquelle beendet oder Fehler beim Lesen.")
            else:
                # Display the captured frame
                cv2.imshow('Camera', frame)

                # Press 'q' to exit the loop
                if cv2.waitKey(1) == ord('q'):
                    cv2.destroyAllWindows()
            # time.sleep(delay)
            time_stamp_list, fps = get_fps(time_stamp_list)
            print(f"FPS {fps}")

if __name__ == "__main__":
    # get_frame_as_stream()
    get_frame_with_delay(20)
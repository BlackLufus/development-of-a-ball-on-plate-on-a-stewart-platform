# https://www.geeksforgeeks.org/python-opencv-capture-video-from-camera/
import asyncio
from collections import deque
import logging
import time
import av
import numpy as np
import cv2
import datetime
import threading

class CameraThreadWithAV:
    def __init__(
            self,
            logger = None,
            # Windows
            device_name = f"video=Logitech BRIO", 
            options = {
                "video_size": "1920x1080",
                "framerate": "30"
            },
            format = "dshow"

            # Linux 
            # Check which camera is connected
            # > v4l2-ctl --list-device
            # Check for available options
            # > 4l2-ctl --device=/dev/video1 --list-formats-ext
            # device_name = "/dev/video1", 
            # options = {
            #     "video_size": "1280x720",
            #     "framerate": "20",
            #     "input_format": "mjpeg"
            # },
            # format = "v4l2"
        ):
        self.frame_num = 0
        self.container = av.open(file=device_name, options=options, format=format)
        self.img = None
        
        self.running = True
        self.thread = threading.Thread(target=self.update, daemon=True)
        self.thread.start()
        self.logger = logger or logging.getLogger("StewartPlatform.VideoCapture")

    def update(self):
        # fps times (sliding window technique)
        fps_times = deque()
        try:
            for frame in self.container.decode(video=0):
                if not self.running:
                    break
                self.img = frame.to_ndarray(format="bgr24")
                self.frame_num += 1

                # Calculate fps
                now = time.monotonic()
                fps_times.append(now)
                while fps_times and (now - fps_times[0] > 1.0):
                    fps_times.popleft()

                self.fps = len(fps_times)
        except:
            self.logger.error("Videoquelle beendet oder Fehler beim Lesen.")
            self.running = False
    
    def read(self):
        if self.img is None:
            return None, 0, 0
        return self.img.copy(), self.fps, self.frame_num
    
    def stop(self):
        self.running = False
        self.thread.join()
        self.container.close()
    
class CameraThread:
    def __init__(self, cam_index=0):
        self.frame_num = 0

        # Windows
        self.cap = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)

        # Linux
        self.cap = cv2.VideoCapture(cam_index, cv2.CAP_V4L2)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))

        # Set resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        # Set frames per second
        self.cap.set(cv2.CAP_PROP_FPS, 60)

        # Read first image
        self.ret, self.frame = self.cap.read()

        # Current fps
        self.fps = 1

        # Is thread running
        self.running = True

        # Setup and start thread
        self.thread = threading.Thread(target=self.update, daemon=True)
        self.thread.start()

    def update(self):
        fps_times = deque()
        while self.running:
            self.ret, self.frame = self.cap.read()
            self.frame_num += 1

            # Calculate fps
            now = time.monotonic()
            fps_times.append(now)
            
            while fps_times and (now - fps_times[0] > 1):
                fps_times.popleft()

            self.fps = len(fps_times)

    def read(self):
        return self.ret, self.frame, self.fps, self.frame_num

    def stop(self):
        self.running = False
        self.thread.join()
        self.cap.release()

class VideoCam:
    def __init__(self, video_source=0):
        # Open the default camera
        self.cap = cv2.VideoCapture(video_source, cv2.CAP_DSHOW)
    
    def update(self):
        while self.cap.isOpened():
            self.ret, self.frame = self.cap.read()

    def read(self):
        return self.ret, self.frame
    
    def stop(self):
        self.cap.release()

# A Function to calculate frame per seconds
def get_fps(array: np.array):
    dt = datetime.datetime.now()
    array = np.append(array, dt)
    match = (dt - datetime.timedelta(seconds=1))
    array = array[array >= match]
    return array, len(array), round(float(array[-1].timestamp() - array[-2].timestamp()), 5) if len(array) >= 2 else 0

# This is a test function to get frame by frame
def get_frame_with_delay(debug = True):
    time_stamp_list = np.array([],dtype=np.float32)
    fps = 20
    delay: float = 1 / fps
    cam = VideoCam(video_source=2)
    cam.cap.set(cv2.CAP_PROP_FPS, fps)
    while cam.cap.isOpened():
        ret, frame = cam.read()
        if not ret:
            print("Videoquelle beendet oder Fehler beim Lesen.")
        else:
            # Display the captured frame
            cv2.imshow('Camera', frame)

            # Press 'q' to exit the loop
            if cv2.waitKey(1) == ord('q'):
                cv2.destroyAllWindows()
        time.sleep(delay)
        if debug:
            time_stamp_list, fps, length = get_fps(time_stamp_list)
            print(f"FPS {fps} ({length})")

# Get available sources
def returnCameraIndexes():
    arr = []
    for index in range(5):
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        if cap.read()[0]:
            arr.append(index)
            cap.release()
        index += 1
    return arr

def get_frame_with_thread():
    cam = CameraThread(cam_index=1)
    
    last_frame_num = cam.frame_num
    try:
        while True:
            
            if last_frame_num != cam.frame_num:
                last_frame_num = cam.frame_num
            
                ret, frame, fps, frame_num = cam.read()
                if not ret:
                    print("Fehler beim Lesen des Frames")
                    break

                print(f"FPS: {fps} (num: {frame_num})")

                # Anzeige des Bildes
                cv2.imshow("Threaded Camera", frame)

                # Mit 'q' beenden
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    finally:
        cam.stop()
        cv2.destroyAllWindows()

def get_frame_with_av_thread():
    # cam = CameraThreadWithAV("Microsoft® LifeCam HD-3000")
    cam = CameraThreadWithAV()

    last_frame_num = cam.frame_num
    try:
        while cam.running:
            if last_frame_num != cam.frame_num:
                last_frame_num = cam.frame_num

                frame, fps, frame_num = cam.read()
                if frame is not None:
                    print(f"FPS: {fps} (num: {frame_num})")

                    # Anzeige des Bildes
                    cv2.imshow("Threaded Camera", frame)

                    # Mit 'q' beenden
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

    finally:
        cam.stop()

if __name__ == "__main__":
    get_frame_with_av_thread()
    # get_frame_with_thread()
    # get_frame_as_stream(video_source=0)
    # print(returnCameraIndexes())
    # get_frame_with_delay()
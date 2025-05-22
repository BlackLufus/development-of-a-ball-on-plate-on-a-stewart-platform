import cv2
import time
import numpy as np

class BallTracker:
    def __init__(self, camera_index=1, frame_width=800, frame_height=600):
        self.cap = cv2.VideoCapture(camera_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

        # Parameter für Ballverfolgung
        self.crop = 50
        self.bbox = 120
        self.ball = None
        self.last_detection_time = 0
        self.last_roi = None  
        self.roi_reset_time = 0.5 

    def get_ball_position(self):
        # Frame lesen und rotieren
        success, img = self.cap.read()
        if not success:
            return None
        img = cv2.rotate(img, cv2.ROTATE_180)

        # Bereiche im Bild ausblenden
        height, width = img.shape[:2]
        img[:90, :180] = [128, 128, 128]
        img[height-95:, :170] = [128, 128, 128]
        img[:100, width-150:] = [128, 128, 128]
        img[height-95:, width-165:] = [128, 128, 128]
        
        # Region of Interest (ROI) definieren
        crop_top, crop_left = 0, 86
        crop_bottom, crop_right = 0, 70
        img = img[crop_top:img.shape[0] - crop_bottom, crop_left:img.shape[1] - crop_right]
        time_since_detection = time.time() - self.last_detection_time

        # ROI anhand der letzten Ball-Position
        if self.ball is not None:
            roi = [(max([self.ball[0] - self.bbox, 0]), max([self.ball[1] - self.bbox, 0])),
                   (self.ball[0] + self.bbox, self.ball[1] + self.bbox)]
        else:
            roi = ((self.crop, self.crop), (img.shape[1] - self.crop, img.shape[0] - self.crop)) if time_since_detection > self.roi_reset_time else self.last_roi

        # Bild in Graustufen umwandeln und Kanten erkennen
        roi_img = img[roi[0][1]:roi[1][1], roi[0][0]:roi[1][0]]
        gray = cv2.cvtColor(roi_img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (9, 9), 2)
        edges = cv2.Canny(gray, 100, 200)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

        # Kanten erweitern
        edges = cv2.dilate(edges, kernel, iterations=1)
        cv2.imshow("Original Edges", edges)

        # Konturen finden und Ball erkennen
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        detected_ball = None
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)
            if len(largest_contour) >= 5 and area > 150:
                ellipse = cv2.fitEllipse(largest_contour)
                cv2.ellipse(roi_img, ellipse, (0, 255, 0), 2)
                center_x, center_y = ellipse[0]
                detected_ball = (int(center_x + roi[0][0]), int(center_y + roi[0][1])) 
                self.last_roi = roi
                self.last_detection_time = time.time()

        # Ball Position zurückgeben
        if detected_ball is not None:
            self.ball = detected_ball
            cv2.rectangle(img, roi[0], roi[1], (0, 255, 0), 2)
            cv2.imshow("Detected Circle", img)
            return detected_ball
        else:
            cv2.rectangle(img, roi[0], roi[1], (0, 0, 255), 2)
            cv2.imshow("Detected Circle", img)
            self.ball = None
            return None

    def release_camera(self):
        # Kamera freigeben
        self.cap.release()

# Beispielverwendung
if __name__ == "__main__":
    tracker = BallTracker(camera_index=1)

    while True:
        ball_position = tracker.get_ball_position()
        print("Ball position: ", ball_position)

        # Bei 'q' beenden
        if cv2.waitKey(40) & 0xFF == ord('q'):
            break

    tracker.release_camera()
    cv2.destroyAllWindows()


 


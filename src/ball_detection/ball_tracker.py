import cv2
import time
import numpy as np

class BallTracker:
    def __init__(self, camera_index=0, frame_width=800, frame_height=600):
        self.cap = cv2.VideoCapture(camera_index, cv2.CAP_V4L2)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

    def get_ball_position(self):
        # Frame lesen und rotieren
        success, img_bgr = self.cap.read()
        if not success:
            return None
        
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        
        # Region of Interest (ROI) definieren
        crop_top, crop_left = 0, 86
        crop_bottom, crop_right = 0, 70
        img_rgb = img_rgb[crop_top:img_rgb.shape[0] - crop_bottom, crop_left:img_rgb.shape[1] - crop_right]

        # Bild in Graustufen kovertieren
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
        _, tresh = cv2.threshold(img_gray, 150, 255, cv2.THRESH_BINARY)

        contours, _ = cv2.findContours(tresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Konturen finden und Ball erkennen
        img_rgb_copy = img_rgb.copy()
        if contours:
            # Bekomme die größte contour
            largest_contour = max(contours, key=cv2.contourArea)

            # Erhalten den bereich der Contour
            area = cv2.contourArea(largest_contour)

            # Bekomme die x, y koordinate und den radius
            (x,y), radius = cv2.minEnclosingCircle(largest_contour)

            # Da float, in int umwandeln
            center = (int(x), int(y))
            radius = int(radius)

            # Zeichne Kreis
            cv2.circle(img_rgb_copy, center, radius, (255, 0, 0), 4)

            ellipse = cv2.fitEllipse(largest_contour)

            # Zeichne Ellipse
            cv2.ellipse(img_rgb_copy, ellipse, (0, 255, 0), 4)


            cv2.imshow("Detected Circle", img_rgb_copy)
            return center
        else:
            return None

    def release_camera(self):
        # Kamera freigeben
        self.cap.release()

# Beispielverwendung
if __name__ == "__main__":
    tracker = BallTracker(camera_index=0)

    while True:
        ball_position = tracker.get_ball_position()
        print("Ball position: ", ball_position)

        # Bei 'q' beenden
        if cv2.waitKey(40) & 0xFF == ord('q'):
            break

    tracker.release_camera()
    cv2.destroyAllWindows()


 


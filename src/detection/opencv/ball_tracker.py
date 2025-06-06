import cv2
import time
import numpy as np

class BallTracker:
    def __init__(self, camera_index=0, frame_width=800, frame_height=600, debug=False):
        self.debug = debug
        self.cap = cv2.VideoCapture(camera_index, cv2.CAP_V4L2)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

    def get_ball_position(self):
        # Read frame from cam
        success, img_rgb = self.cap.read()
        if not success:
            return None

        img_rgb = cv2.rotate(img_rgb, cv2.ROTATE_180)
        
        # Crop image to the preferd size
        crop_top, crop_left = 0, 86
        crop_bottom, crop_right = 0, 70
        img_rgb = img_rgb[crop_top:img_rgb.shape[0] - crop_bottom, crop_left:img_rgb.shape[1] - crop_right]

        # Convert image from rgb to gray
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
        if self.debug:
            cv2.imshow('img_gray', img_gray)

        # Get binarty image
        _, tresh = cv2.threshold(img_gray, 210, 255, cv2.THRESH_BINARY)
        if self.debug:
            cv2.imshow('tresh', tresh)

        # Get all contours
        contours, _ = cv2.findContours(tresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # To prevent manipulating the original image we create a copy of it
        img_rgb_copy = img_rgb.copy()

        # contours = [cnt for cnt in contours if self.check_circle(cv2.minEnclosingCircle(cnt)[1], cv2.contourArea(cnt))]

        # Check if any contour exist
        if contours:
            # Detect longest contour
            largest_contour = max(contours, key=cv2.contourArea)

            # Get x, y, koordinates and the radius
            (x,y), radius = cv2.minEnclosingCircle(largest_contour)

            # Becouse if the type of the object we have to convert it to int
            center = (int(x), int(y))
            radius = int(radius)

            # Draw circle
            cv2.circle(img_rgb_copy, center, radius, (255, 0, 0), 4)

            # Get ellipse from largest contour
            ellipse = cv2.fitEllipse(largest_contour)

            # Draw ellipse
            cv2.ellipse(img_rgb_copy, ellipse, (0, 255, 0), 4)


            if self.debug:
                cv2.imshow("Detected Circle", img_rgb_copy)
            # Return features
            return center
        else:
            return None
    
    def check_circle(self, radius, area):
        circle_area = np.pi * (radius ** 2)

        ratio = area / circle_area
        if 0.6 < ratio < 1.2:
            return True
        return False

    def release_camera(self):
        # Kamera freigeben
        self.cap.release()

# Beispielverwendung
if __name__ == "__main__":
    tracker = BallTracker(debug=True)

    while True:
        ball_position = tracker.get_ball_position()
        print("Ball position: ", ball_position)

        # Bei 'q' beenden
        if cv2.waitKey(40) & 0xFF == ord('q'):
            break

    tracker.release_camera()
    cv2.destroyAllWindows()


 


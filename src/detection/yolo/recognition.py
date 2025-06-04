
from datetime import datetime
# importing os module  
import os

from src.video_capture.video_capture import CameraThreadWithAV

import cv2

class FrameRecognition:

    def crop(self, frame):
        # 640x640 aus Bildmitte zuschneiden
        height, width, _ = frame.shape
        start_x = max((width - 648) // 2, 0)
        start_y = max((height - 648) // 2, 0)
        end_x = start_x + 648
        end_y = start_y + 648
        return frame[start_y:end_y, start_x:end_x]


    def __init__(self, fps:int, amount:int) -> None:
        print(f"fps: {fps}", f"amount: {amount}")
        if not os.path.exists('./record_images'):
            os.makedirs('./record_images')

        cam = CameraThreadWithAV(
            device_name='/dev/video0',
            options={
                "video_size": '1152x648',
                "framerate": str(fps),
                "input_format": "mjpeg"
            },
            format="v4l2",
            logger=None
        )

        last_frame_num = cam.frame_num
        try:
            print("Enter loop")
            while amount > 0 and cam.running:
                if last_frame_num != cam.frame_num:
                    last_frame_num = cam.frame_num

                    frame, fps, frame_num = cam.read()
                    if frame is not None:
                        amount -= 1
                        print("save Image:")
                        file_path = f'./record_images/{datetime.now().strftime("%Y%m%d-%H%M%S%f")}.jpg'

                        cropped_frame = self.crop(frame)
                        # Anzeige des Bildes
                        cv2.imwrite(file_path, cropped_frame)

                        # Mit 'q' beenden
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break

        finally:
            print("Leave loop")
            cam.stop()

if __name__ == "__main__":
    print("Start Recognition")
    FrameRecognition(15, 400)


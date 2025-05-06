import av
import numpy as np
import cv2
import time

# Logitech Brio – Name muss evtl. angepasst werden
device_name = "video=Logitech BRIO"

# Öffne Kamera mit FFmpeg über DirectShow
container = av.open(device_name, format="dshow")

fps_times = []
for frame in container.decode(video=0):
    img = frame.to_ndarray(format="bgr24")
    cv2.imshow("Brio", img)

    now = time.time()
    fps_times.append(now)
    fps_times = [t for t in fps_times if now - t < 1]
    print(f"FPS: {len(fps_times)}")

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cv2.destroyAllWindows()

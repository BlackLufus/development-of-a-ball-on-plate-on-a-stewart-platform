from ultralytics import YOLO  # YOLOv8-Modell
import cv2

from src.video_capture.video_capture import CameraThreadWithAV

def crop_and_resize(frame):
    # 720x720 aus der Bildmitte zuschneiden
    height, width = 720, 1280
    start_x = max((width - 720) // 2, 0)
    start_y = max((height - 720) // 2, 0)
    end_x = start_x + 720
    end_y = start_y + 720
    cropped = frame[start_y:end_y, start_x:end_x]

    # Skalieren auf 640x640 (passend zur Trainingsgröße)
    resized = cv2.resize(cropped, (640, 640), interpolation=cv2.INTER_LINEAR)
    return resized

def detect_and_speak(video_source=0, language="de"):
    # Load yolo mode
    # model = YOLO("./models/best.pt", )

    # model.export(format="ncnn")

    # Load the exported NCNN model
    ncnn_model = YOLO("./models/best_ncnn_model")

    # Videoquelle öffnen (z. B. Webcam oder Video)
    cam = CameraThreadWithAV(
        device_name='/dev/video1',
        options={
            "video_size": '1280x720',
            "framerate": str(20),
            "input_format": "mjpeg"
        },
        format="v4l2",
        logger=None
    )

    last_frame_num = cam.frame_num
    while cam.running:
        if last_frame_num != cam.frame_num:
            last_frame_num = cam.frame_num

            frame, fps, frame_num = cam.read()
            print(frame_num)
            if frame is not None:
            
                # input_frame = crop_and_resize(frame)

                # Objekterkennung auf dem aktuellen Frame
                # results = ncnn_model(input_frame)  # Ergebnisse vom Modell
                results = ncnn_model(frame)


                # Replace the detected_classes list with a dictionary to count occurrences
                detected_classes_count = {}
                for result in results:
                    boxes = result.boxes  # Boxen und Klassen aus den Ergebnissen
                    for box in boxes:
                        class_id = int(box.cls[0])  # Klassen-ID
                        class_name = ncnn_model.names[class_id]  # Klassenname
                        confidence = box.conf[0]  # Add this line to get confidence score
                        if confidence >= 0.5:
                            detected_classes_count[class_name] = (
                                detected_classes_count.get(class_name, 0) + 1
                            )

                            # Koordinaten der Bounding Box erhalten
                            x1, y1, x2, y2 = map(int, box.xyxy[0])

                            # Bounding Box zeichnen
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                            # Text (Klassennamen und Confidence-Score) über der Box anzeigen
                            label = f"{class_name} ({confidence:.2f})"
                            cv2.putText(
                                frame,
                                label,
                                (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.5,
                                (0, 255, 0),
                                2,
                            )

                # Frame mit Bounding Boxes anzeigen
                cv2.imshow("YOLO11 Objekterkennung", frame)

        # Beenden mit der Taste 'q'
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Video ist zu Ende, aber warte auf Audio
    cam.stop()

    # Cleanup erst nach Audio-Ende
    cv2.destroyAllWindows()


# Funktion starten (verwende die Webcam als Videoquelle)
detect_and_speak(video_source=0)
# detect_and_speak(
#     video_source="C:\\Users\\BlackLufus\\Workspace\\object-detection-mci\\video\\output_video_16-11.mp4"
# )
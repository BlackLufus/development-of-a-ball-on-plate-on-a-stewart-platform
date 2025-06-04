from ultralytics import YOLO  # YOLOv8-Modell
import cv2


def detect_and_speak(video_source=0, language="de"):
    # YOLOv8-Modell laden (z. B. vortrainiertes COCO-Modell)
    # model = YOLO("yolov8x.pt")  # YOLOv8-Modell
    # model = YOLO("yolov8n.pt")  # YOLOv8-Modell
    # model = YOLO("yolov9e.pt")  # YOLOv9-Modell
    # model = YOLO("yolov9s.pt")  # YOLOv9-Modell
    # model = YOLO("yolo11n.pt")  # YOLOv9-Modell
    # model = YOLO('yolov5s.pt') # YOLOv5-Modell
    # model = YOLO("./models/best.pt")
    # model = YOLO("lego_bricks_v1.pt")

    # model.export(format="ncnn")

    # # Load the exported NCNN model
    ncnn_model = YOLO("./models/best_ncnn_model")

    # Videoquelle öffnen (z. B. Webcam oder Video)
    cap = cv2.VideoCapture(video_source)
    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)

    if not cap.isOpened():
        print("Fehler: Die Videoquelle konnte nicht geöffnet werden.")
        return

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Videoquelle beendet oder Fehler beim Lesen.")
            break

        # Objekterkennung auf dem aktuellen Frame
        results = ncnn_model(frame)  # Ergebnisse vom Modell
        # results = ncnn_model(frame)


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
    cap.release()

    # Cleanup erst nach Audio-Ende
    cv2.destroyAllWindows()


# Funktion starten (verwende die Webcam als Videoquelle)
detect_and_speak(video_source=0)
# detect_and_speak(
#     video_source="C:\\Users\\BlackLufus\\Workspace\\object-detection-mci\\video\\output_video_16-11.mp4"
# )
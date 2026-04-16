from ultralytics import YOLO
import cv2

model = YOLO("yolov8n.pt")  # o tu modelo

cap = cv2.VideoCapture("normal.mp4")

# Línea de conteo (y = 300 por ejemplo)
line_y = 550

conteo = {
    "carro": 0,
    "moto": 0,
    "bus": 0,
    "camion": 0
}

# IDs ya contados
ids_contados = set()

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    results = model.track(frame, persist=True)

    if results[0].boxes.id is not None:
        boxes = results[0].boxes

        for box, track_id in zip(boxes.xyxy, boxes.id):

            x1, y1, x2, y2 = map(int, box)
            track_id = int(track_id)

            # Centro del objeto
            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)

            clase = int(boxes.cls[0])

            # Mapear clases (ajústalo)
            if clase == 2:
                label = "carro"
            elif clase == 3:
                label = "moto"
            elif clase == 5:
                label = "bus"
            elif clase == 7:
                label = "camion"
            else:
                continue

            # Dibujar
            cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)
            cv2.circle(frame, (cx, cy), 4, (0,0,255), -1)
            cv2.putText(frame, f"{label}-{track_id}", (x1, y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)

            # 🔥 CONTEO POR LÍNEA
            if cy > line_y and track_id not in ids_contados:
                conteo[label] += 1
                ids_contados.add(track_id)

    # Dibujar línea
    cv2.line(frame, (0, line_y), (frame.shape[1], line_y), (255,0,0), 3)

    # Mostrar conteo
    y_offset = 30
    for tipo, cantidad in conteo.items():
        cv2.putText(frame, f"{tipo}: {cantidad}", (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
        y_offset += 30

    cv2.imshow("Conteo por linea", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()

print("\n=== CONTEO FINAL ===")
for tipo, cantidad in conteo.items():
    print(f"{tipo}: {cantidad}")
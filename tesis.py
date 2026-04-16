import cv2
import os

video = "entrada.mp4"
output = "dataset/images"

os.makedirs(output, exist_ok=True)

cap = cv2.VideoCapture(video)

count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    cv2.imwrite(f"{output}/frame_{count}.jpg", frame)
    count += 1

cap.release()
print("Frames extraídos:", count)
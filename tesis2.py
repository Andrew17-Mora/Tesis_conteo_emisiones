import cv2
import os

image_folder = "dataset/images"
label_folder = "dataset/labels"


classes = {
    2: "carro",
    3: "moto",
    5: "bus",
    7: "camion"
}

for image_name in os.listdir(image_folder):

    img_path = os.path.join(image_folder, image_name)
    label_path = os.path.join(label_folder, image_name.replace(".jpg", ".txt"))

    img = cv2.imread(img_path)
    h, w, _ = img.shape

    if os.path.exists(label_path):

        with open(label_path) as f:
            for line in f.readlines():

                clase, x, y, bw, bh = map(float, line.split())
                clase = int(clase)

                x1 = int((x - bw/2) * w)
                y1 = int((y - bh/2) * h)
                x2 = int((x + bw/2) * w)
                y2 = int((y + bh/2) * h)

                label = classes.get(clase, "obj")

                cv2.rectangle(img, (x1,y1), (x2,y2), (0,255,0), 2)
                cv2.putText(img, label, (x1, y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6, (0,255,0), 2)

    cv2.imshow("", img)

    if cv2.waitKey(0) == 27:
        break

cv2.destroyAllWindows()
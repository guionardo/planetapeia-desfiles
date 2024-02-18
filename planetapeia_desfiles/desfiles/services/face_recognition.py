import os

import cv2

CASCADE = os.path.join(os.path.dirname(__file__), "Face_cascade.xml")
FACE_CASCADE = cv2.CascadeClassifier(CASCADE)


def get_face_image(filename: str, width=250) -> str:
    f, e = os.path.splitext(filename)
    face_file = f"{f}.face{e}"
    if os.path.isfile(face_file):
        return face_file
    image = cv2.imread(filename)
    image_grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    faces = FACE_CASCADE.detectMultiScale(
        image_grey, scaleFactor=1.16, minNeighbors=5, minSize=(25, 25), flags=0
    )
    for x, y, w, h in faces:
        pad = int(h * 0.2)  # 10
        sub_img = image[max(0, y - pad) : y + h + pad, x - pad : x + w + pad]

        break
    else:
        sub_img = image

    r = float(width) / sub_img.shape[1]
    dim = (width, int(sub_img.shape[0] * r))
    resized = cv2.resize(sub_img, dim, interpolation=cv2.INTER_AREA)

    cv2.imwrite(face_file, resized)

    return face_file

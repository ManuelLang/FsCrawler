import cv2
import numpy as np
from pdf2image.pdf2image import convert_from_path
from pytesseract import image_to_string

pages = convert_from_path('/Users/langm27/Downloads/Contrat de bail - Romain Godelier et Lisenn Doré.pdf', 200)
for i in range(len(pages)):
    pages[i].save(f"/Users/langm27/Downloads/tmp/page{i}.jpg", 'JPEG')
    # https://stackoverflow.com/questions/65802129/pytesseract-output-is-extremely-inaccurate-mac
    img = cv2.imread(f"/Users/langm27/Downloads/tmp/page{i}.jpg")
    kernel = np.ones((4, 4), np.uint8)
    opn = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
    txt = image_to_string(img)
    txt = txt.split("\n")
    for i in txt:
        i = i.strip()
        if i != '' and len(i) > 3:
            print(i)

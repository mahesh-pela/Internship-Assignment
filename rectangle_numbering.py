import cv2
import numpy as np
import math


def getContours(img, contourType):
    mode = cv2.RETR_TREE if contourType == "line" else cv2.RETR_EXTERNAL
    contours, _ = cv2.findContours(img, mode, cv2.CHAIN_APPROX_SIMPLE)
    rectangleContours = []
    lineContours = []

    for contour in contours:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        area = cv2.contourArea(contour)
        rect = cv2.minAreaRect(contour)
        box = np.intp(cv2.boxPoints(rect))  # Use np.intp instead of np.int0
        center, size, angle = rect

        if contourType == "line" and area >= 5 and min(size) < 20:
            lineContours.append({'center': center, 'size': size, 'angle': angle, 'area': area, 'box': box})
        elif contourType != "line":
            x_start, y_start = box[3]
            x_end, y_end = box[1]
            rectangleContours.append({'center': center, 'size': size, 'angle': angle, 'area': area, 'box': box,
                                       'BBpoints': [x_start, y_start, x_end, y_end]})

    if contourType == "line":
        similarLineList = []
        while len(lineContours) != 0:
            similarLine = []
            line = lineContours[0]
            similarLine.append(line)
            for j in range(1, len(lineContours)):
                if j < len(lineContours):
                    if abs(line['center'][0] - lineContours[j]['center'][0] < 10 and line['center'][1] -
                           lineContours[j]['center'][1] < 10.0):
                        if abs(line['angle'] - lineContours[j]['angle']) < 1.0:
                            if abs(line['area'] - lineContours[j]['area']) < 175:
                                similarLine.append(lineContours[j])
                                del lineContours[j]
            del lineContours[0]
            similarLineList.extend([similarLine])

        for similarLines in similarLineList:
            if len(similarLines) > 1:
                if similarLines[0]['area'] < similarLines[1]['area']:
                    lineContours.append(similarLines[0])
                else:
                    lineContours.append(similarLines[1])
            else:
                lineContours.append(similarLines[0])

        return lineContours
    else:
        return rectangleContours


img = cv2.imread('image.png')
imgContour = img.copy()

imgGray = cv2.cvtColor(cv2.GaussianBlur(img, (7, 7), 1), cv2.COLOR_BGR2GRAY)
imgCanny = cv2.Canny(imgGray, 20, 23)

lineContours = getContours(imgCanny, "line")
rectangleContours = getContours(imgCanny, "rectangle")

numberedImgContour = img.copy()

sorted_index = []
i = 0
for lineContour in lineContours:
    if lineContour['size'][0] > lineContour['size'][1]:
        lineContour['length'] = lineContour['size'][0]
        lineContour['width'] = lineContour['size'][1]
    else:
        lineContour['length'] = lineContour['size'][1]
        lineContour['width'] = lineContour['size'][0]
    dict = {'index': i,
            'length': lineContour['length'],
            'width': lineContour['width']}
    sorted_index.append(dict)
    i = i + 1

temp = sorted_index.copy()
sorted_index = sorted(sorted_index, key=lambda d: d['length'])

for i in range(0, len(sorted_index)):
    index = sorted_index[i]['index']
    length = sorted_index[i]['length']
    x = int(rectangleContours[index]['center'][0])
    y = int(rectangleContours[index]['center'][1])
    cv2.putText(numberedImgContour, f"R-{i + 1}", (x - 100, y + 100), cv2.FONT_HERSHEY_COMPLEX, 1.2, (0, 255, 0), 2)
    cv2.putText(numberedImgContour, f"Length: {round(length, 2)}", (x - 100, y + 135),
                cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)

cv2.putText(numberedImgContour, "Rectangle Numbering Image", (120, 28), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)

cv2.imwrite("numbered_image.jpg", numberedImgContour)

print("Success!!!")

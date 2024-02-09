import cv2
import numpy as np
import math

def getContours(img, contourType):
    mode = cv2.RETR_TREE if contourType == "line" else cv2.RETR_EXTERNAL
    contours, _ = cv2.findContours(img, mode, cv2.CHAIN_APPROX_SIMPLE)
    rectangleContours = []
    lineContours = []
    for i, contour in enumerate(contours):
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        area = cv2.contourArea(contour)
        rect = cv2.minAreaRect(contour)
        box = np.intp(cv2.boxPoints(rect))  # Updated np.int0 to np.intp
        center, size, angle = rect
        if contourType == "line" and area >= 5 and min(size) < 20:
            lineContours.append({'contour': i, 'center': center, 'size': size, 'angle': angle, 'area': area, 'box': box})
        elif contourType != "line":
            x_start, y_start = box[3]
            x_end, y_end = box[1]
            rectangleContours.append({'contour': i, 'center': center, 'size': size, 'angle': angle, 'area': area, 'box': box, 'BBpoints': [x_start, y_start, x_end, y_end]})
    return lineContours if contourType == "line" else rectangleContours

def findPerpendicularDist(x1, y1, x2, y2, x, y):
    A = y1 - y2
    B = x2 - x1
    if A == 0 or B == 0:
        return float('inf')
    C = x1 * y2 - x2 * y1
    pd = abs((A * x + B * y + C)) / (math.sqrt(A * A + B * B))
    return pd

img = cv2.imread('image.png')
blankImg = cv2.imread('image.png')

imgGray = cv2.cvtColor(cv2.GaussianBlur(img, (7, 7), 1), cv2.COLOR_BGR2GRAY)
imgCanny = cv2.Canny(imgGray, 20, 23)

lineContours = getContours(imgCanny, "line")
rectangleContours = getContours(imgCanny, "rectangle")

# Calculate the average angle of all rectangle contours
total_angle = 0
for rectContour in rectangleContours:
    total_angle += rectContour['angle']
average_angle = total_angle / len(rectangleContours)

# Rotate each rectangle contour by the negative of the average angle
for rectContour in rectangleContours:
    rectContour['angle'] -= average_angle
    # Rotate the box points
    rotated_box = cv2.boxPoints(((rectContour['center']), (rectContour['size']), rectContour['angle']))
    rectContour['box'] = np.intp(rotated_box)

# Now all rectangle contours should be aligned horizontally

for rectContour in rectangleContours:
    cv2.rectangle(img, tuple(rectContour['box'][1]), tuple(rectContour['box'][3]), (219, 67, 119), 3)
    cv2.rectangle(blankImg, tuple(rectContour['box'][1]), tuple(rectContour['box'][3]), (0, 0, 0), 2)

for lineContour in lineContours:
    length, width = max(lineContour['size']), min(lineContour['size'])
    # Check if the rectangleContours list is not empty before accessing its elements
    if rectangleContours:
        if len(rectangleContours) > lineContour['contour']:
            pd1 = findPerpendicularDist(*lineContour['box'][1], *rectangleContours[lineContour['contour']]['box'][1], *lineContour['center'])
            pd2 = findPerpendicularDist(*lineContour['box'][1], *rectangleContours[lineContour['contour']]['box'][0], *lineContour['center'])
            if np.isfinite(pd1) and np.isfinite(pd2):
                pd1, pd2 = round(pd1, 0), round(pd2, 0)
                x_start, y_start = rectangleContours[lineContour['contour']]['box'][1]
                length = round(length, 0)
                if (d1 := math.sqrt((x_start - rectContour['box'][0][0]) ** 2 + (y_start - rectContour['box'][0][1]) ** 2)) >= (d2 := math.sqrt((x_start - rectContour['box'][2][0]) ** 2 + (y_start - rectContour['box'][2][1]) ** 2)):
                    x_start -= pd2
                    x_end = x_start - length
                    y_start -= pd1
                    y_end = y_start
                else:
                    x_start += pd1
                    x_end = x_start + length
                    y_start -= pd2
                    y_end = y_start
                cv2.rectangle(img, (int(x_start), int(y_start)), (int(x_end), int(y_end)), (219, 67, 119), 2)
                cv2.rectangle(blankImg, (int(x_start), int(y_start)), (int(x_end), int(y_end)), (0, 0, 0), 2)
        else:
            print("Index out of range in rectangleContours list.")
    else:
        print("No rectangle contours found.")

cv2.imwrite('result_image2.png', img)

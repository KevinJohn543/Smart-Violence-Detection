from __future__ import absolute_import
from __future__  import division
from __future__ import print_function
import tensorflow as tf
import numpy as np
from skimage.io import imread
from skimage.transform import resize
import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import pyplot
from mtcnn.mtcnn import MTCNN
from matplotlib.patches import Rectangle
from PIL import Image
from PIL import ImageEnhance
from matplotlib.patches import Circle
from tkinter import filedialog as fd
import tkinter
import argparse
import imutils
import math
import time
import os
from localfiletesting import *
import trafficLightColor
import threading

hastrafficlight = False
trafficlight_detected = False

model = Det_Model(tf,wight='D:/Smart violence Detection/fightw.hdfs')
root = tkinter.Tk()
root.withdraw()
V_test = fd.askopenfilenames(title="Select Input Video File", filetypes=[("Video Files", "*.mp4")])

displayCounter = 0
j = 0
output_path = "output/a_output.avi"

# Set YOLO directory path
yolo_path = "yolo-coco"

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input",nargs="+",
	help="path to input video")
ap.add_argument("-o", "--output", required=True,
	help="path to output video")
ap.add_argument("-y", "--yolo", required=True,
	help="base path to YOLO directory")
ap.add_argument("-c", "--confidence", type=float, default=0.5,
	help="minimum probability to filter weak detections")
ap.add_argument("-t", "--threshold", type=float, default=0.3,
	help="threshold when applyong non-maxima suppression")
if not V_test:
    print("No input video selected.")
else:
    # pass the input files to argparse
    args = vars(ap.parse_args(["--input"] + list(V_test) + ["--output", output_path, "--yolo", yolo_path]))
    # load the COCO class labels our YOLO model was trained on
    labelsPath = os.path.sep.join([args["yolo"], "coco.names"])
    LABELS = open(labelsPath).read().strip().split("\n")

    # initialize a list of colors to represent each possible class label
    np.random.seed(42)
    COLORS = np.random.randint(0, 255, size=(len(LABELS), 3),
	    dtype="uint8")

    # derive the paths to the YOLO weights and model configuration
    weightsPath = os.path.sep.join([args["yolo"], "yolov3.weights"])
    configPath = os.path.sep.join([args["yolo"], "yolov3.cfg"])

    # load our YOLO object detector trained on COCO dataset (80 classes)
    # and determine only the *output* layer names that we need from YOLO
    print("[INFO] loading YOLO from disk...")
    net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)
    ln = net.getLayerNames()
    ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]

    for input_path in args['input']:
        # Open the input video
        cap = cv2.VideoCapture(input_path)

        # Get the video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        writer = None
        (W, H) = (None, None)

        try:
	        prop = cv2.cv.CV_CAP_PROP_FRAME_COUNT if imutils.is_cv2() \
		        else cv2.CAP_PROP_FRAME_COUNT
	        total = int(cap.get(prop))
	        print("[INFO] {} total frames in video".format(total))

        # an error occurred while trying to determine the total
        # number of frames in the video file
        except:
	        print("[INFO] could not determine # of frames in video")
	        print("[INFO] no approx. completion time can be provided")
	        total = -1

        OPENCV_OBJECT_TRACKERS = {
	        "csrt": cv2.TrackerCSRT_create,
	        "kcf": cv2.TrackerKCF_create,
	        "boosting": cv2.TrackerBoosting_create,
	        "mil": cv2.TrackerMIL_create,
	        "tld": cv2.TrackerTLD_create,
	        "mosse": cv2.TrackerMOSSE_create
        }
        startTime = time.time()
        def detectviolence():
            i = 0
            frames = np.zeros((30, 160, 160, 3), dtype=float)
            old = []
            k = 0
            truecount = 0
            imagesaved=0
            filename = './output/Violence-{}.jpg'
            my_image = 'finalImage.jpg'
            face_image = 'faces.png'
            ysdatav2 = np.zeros((1, 30, 160, 160, 3), dtype=float)
            ysdatav2[0][:][:] = frames
            prediction = pred_fight(model,ysdatav2,acuracy=0.96)
            exit_flag = False
            while(True):
                ret, frame = cap.read()

                if not ret:
                    break
                # describe the type of font to be used 
                font = cv2.FONT_HERSHEY_SIMPLEX
                #display the text on every frame
                text_color = (0, 255, 0) #Green
                label = prediction[0]
                if label: # Violence
                    text_color = (0, 0, 255) # red
                    truecount = truecount + 1
                else:# No Violence
                    text_color = (0, 255, 0)
                text = "Violence: {}".format(label)
                cv2.putText(frame, text, (35, 50), font,1.25, text_color, 3)
                if i > 29:
                    ysdatav2 = np.zeros((1,30,160,160, 3), dtype=float)
                    ysdatav2[0][:][:] = frames
                    prediction = pred_fight(model,ysdatav2,acuracy=0.96)
                    if label == True:
                        cv2.imshow('out',frame)
                        print('Violence detected here ...')
                        fourcc = cv2.VideoWriter_fourcc(*'XVID')
                        vio = cv2.VideoWriter("./videos/output-"+str(k)+".avi", fourcc, 10.0, (fwidth,fheight))
                        #vio = cv2.VideoWrite"./videos/output-"+str(j)+".mp4", cv2.VideoWriter_fourcc(*'mp4v'), 10, (300, 400))
                        for frameinss in old:
                            vio.write(frameinss)
                        vio.release()
                    i = 0
                    k += 1
                    frames = np.zeros((30, 160, 160, 3), dtype=float)
                    old = []
                else:
                    try:
                        frm = resize(frame,(160,160,3))
                        old.append(frame)
                        fshape = frame.shape
                        fheight = fshape[0]
                        fwidth = fshape[1]
                        frm = np.expand_dims(frm,axis=0)
                        if(np.max(frm)>1):
                            frm = frm/255
                        frames[i][:] = frm
                        i+=1
                    except:
                        pass
                if(truecount == 40):
                    if(imagesaved == 0):
                        if(label):
                            frame_umat = cv2.UMat(frame,None) # convert numpy array to cv2.UMat
                            cv2.imwrite(filename.format(k),frame_umat)
                            imagesaved = 1
        def distance_to_line(line_point_1, line_point_2, point): #EUCLEDIAN DISTANCE
            x1, y1 = line_point_1
            x2, y2 = line_point_2
            x, y = point
            A = y2 - y1
            B = x1 - x2
            C = (y1 - y2) * x1 + (x2 - x1) * y1
            distance = abs(A * x + B * y + C) / math.sqrt(A ** 2 + B ** 2)
            return distance
        def up(): #to delete the boxes when the object is out of the frame
            deleted = []
            for n, pair in enumerate(trackersList):
                tracker, box = pair
                (x, y, w, h) = box
                for n2,pair2 in enumerate(trackersList):
                    if(n == n2):
                        continue
                    tracker2, box2 = pair2
                    (x2, y2, w2, h2) = box2
                    val = bb_intersection_over_union([x, y, x + w, y + h], [x2, y2, x2 + w2, y2 + h2])
                    if(val > 0.4):
                        deleted.append(n)
                        break
            print(deleted)
            for i in deleted:
                del trackersList[i]
        def bb_intersection_over_union(boxA, boxB):
            # determine the (x, y)-coordinates of the intersection rectangle
            xA = max(boxA[0], boxB[0])
            yA = max(boxA[1], boxB[1])
            xB = min(boxA[2], boxB[2])
            yB = min(boxA[3], boxB[3])

            # compute the area of intersection rectangle
            interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)

            # compute the area of both the prediction and ground-truth
            # rectangles
            boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
            boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)

            # compute the intersection over union by taking the intersection
            # area and dividing it by the sum of prediction + ground-truth
            # areas - the interesection area
            iou = interArea / float(boxAArea + boxBArea - interArea)

            # return the intersection over union value
            return iou
        def setLightCoordinates(): # used for detecting the traffic lights in a video    
            global hastrafficlight   
            vss = cv2.VideoCapture(input_path)
            while True:
                W = None
                H = None
                # read the next frame from the file
                (grabbed, frame) = vss.read()
                if not grabbed:
                    break
                else:
                    frame = cv2.resize(frame, (1000, 750))
                # if the frame dimensions are empty, grab them
                if W is None or H is None:
                    (H, W) = frame.shape[:2]

                # construct a blob from the input frame and then perform a forward
                # pass of the YOLO object detector, giving us our bounding boxes
                # and associated probabilities
                blob = cv2.dnn.blobFromImage(
                    frame, 1 / 255.0, (416, 416), swapRB=True, crop=False
                )
                net.setInput(blob)
                start = time.time()
                layerOutputs = net.forward(ln)
                end = time.time()

                # initialize our lists of detected bounding boxes, confidences,
                # and class IDs, respectively
                boxes = []
                confidences = []
                classIDs = []

                # loop over each of the layer outputs
                for output in layerOutputs:
                    # loop over each of the detections
                    for detection in output:
                        # extract the class ID and confidence (i.e., probability)
                        # of the current object detection
                        scores = detection[5:]
                        classID = np.argmax(scores)
                        confidence = scores[classID]

                        # filter out weak predictions by ensuring the detected
                        # probability is greater than the minimum probability
                        if confidence > 0.1:
                            # scale the bounding box coordinates back relative to
                            # the size of the image, keeping in mind that YOLO
                            # actually returns the center (x, y)-coordinates of
                            # the bounding box followed by the boxes' width and
                            # height
                            box = detection[0:4] * np.array([W, H, W, H])
                            (centerX, centerY, width, height) = box.astype("int")

                            # use the center (x, y)-coordinates to derive the top
                            # and and left corner of the bounding box
                            x = int(centerX - (width / 2))
                            y = int(centerY - (height / 2))

                            # update our list of bounding box coordinates,
                            # confidences, and class IDs
                            boxes.append([x, y, int(width), int(height)])
                            confidences.append(float(confidence))
                            classIDs.append(classID)

                # apply non-maxima suppression to suppress weak, overlapping
                # bounding boxes
                idxs = cv2.dnn.NMSBoxes(boxes, confidences, 0.1, args['threshold'])
                # loop over the indexes we are keeping
                for i in idxs.flatten():
                    (x, y) = (boxes[i][0], boxes[i][1])
                    (w, h) = (boxes[i][2], boxes[i][3])
                    color = [int(c) for c in COLORS[classIDs[i]]]
                    if classIDs[i] == 9:
                        hastrafficlight = True
                        print("Traffic Light Detected")
                        vss.release()
                        cv2.waitKey()
                        return (True,x, y, w, h)
                        break
                return (False, None, None, None, None)
    listAll = []
    trafficlight_detected,xlight,ylight,wlight,hlight = setLightCoordinates()
    def Trafficlight:
        def getLightThresh():
            while True:
                vss = cv2.VideoCapture(input_path)
                (grabbed, frame) = vss.read()

                frame = cv2.resize(frame, (1000, 750))
                temp =frame.copy()
                temp2=frame.copy()
                grayscaled = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                th = cv2.adaptiveThreshold(grayscaled, 250, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 115, 1)
                kernel = np.ones((3, 3), np.uint8)
                th = cv2.erode(th, kernel, iterations=1)
                th = cv2.dilate(th, kernel, iterations=2)
                contours, hierarchy = cv2.findContours(th, cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_KCOS)
                cv2.destroyAllWindows()
                contIndex = 0
                allContours = []
                for contour in contours:
                    M = cv2.moments(contour)
                    if(cv2.contourArea(contour)>800):
                        if(len(contour)<100):
                            peri = cv2.arcLength(contour, True)
                            approx = cv2.approxPolyDP(contour, 0.04 * peri, True)
                            if(len(approx)==4):
                                x, y, w, h = cv2.boundingRect(contour)
                                cv2.drawContours(frame, contours, contIndex, (0, 255, 0), 3)
                                cv2.rectangle(temp,(x,y),(x+w,y+h),(255,0,0),2)
                                allContours.append((x,y,w,h))
                    contIndex = contIndex + 1

                cv2.drawContours(temp2, contours, -1, (0, 255, 0), 3)
                frame=temp
                minIndex = 0
                count=0
                minDistance = 10000000
                for rect in allContours:
                    x,y,w,h = rect
                    if(ylight+wlight<y):
                        cv2.line(temp, (xlight,ylight), (x, y), (0, 0, 255), 2)
                        if (((x-xlight)**2 + (y-ylight)**2)**0.5) < minDistance:
                            minDistance = (((x-xlight)**2 + (y-ylight)**2)**0.5)
                            minIndex=count
                    count=count+1
                (x,y,w,h) = allContours[minIndex]
                vss.release()
                return y

        ctr = 0

        penaltyList = []
        redLightViolatedCounter = 0

        thresholdRedLight = getLightThresh()
        trackersList = []
        redTrackers = []
        recentlyViolated = []
        redTrackingCounters = []
        iDsWithIoUList = []
        idCounter = 0

        def updateTrackers(image):
            print('update')
            global displayCounter
            global redTrackers
            global redLightViolatedCounter
            global recentlyViolated
            global redTrackingCounters
            boxes = []

            for n, pair in enumerate(trackersList):
                tracker, box = pair

                success, bbox = tracker.update(image)

                if not success:
                    del trackersList[n]
                    continue

                boxes.append(bbox)  # Return updated box list

                xmin = int(bbox[0])
                ymin = int(bbox[1])
                xmax = int(bbox[0] + bbox[2])
                ymax = int(bbox[1] + bbox[3])
                xmid = int(round((xmin + xmax) / 2))
                ymid = int(round((ymin + ymax) / 2))
                light = frame[ylight:ylight + hlight, xlight:xlight + wlight]
                b, g, r = cv2.split(light)
                light = cv2.merge([r, g, b])
                if(ymid < thresholdRedLight and trafficLightColor.estimate_label(light)=="red"):
                    displayCounter = 10
                    print(displayCounter)
                    clone = image.copy()
                    cv2.line(clone, (0, thresholdRedLight), (1300, thresholdRedLight), (0, 0, 0), 4, cv2.LINE_AA)
                    print(trafficLightColor.estimate_label(light))
                    cv2.rectangle(clone, (xmax, ymax), (xmin, ymin), (0, 255, 0), 2)
                    print(redLightViolatedCounter)
                    redLightViolatedCounter = redLightViolatedCounter + 1
                    print(trackersList[n])
                    recentlyViolated.append((trackersList[n][1],10))
                    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    print(redLightViolatedCounter)
                    print(box)
                    print("__")
                    print(bbox)
                    print("___")
                    tracker, box = trackersList[n]

                    (xt, yt, wt, ht) = box
                    print(iDsWithIoUList)
                    for nn, item in enumerate(iDsWithIoUList):
                        print(item)
                        ___, id, listWithFrame,violationList = item
                        print(listWithFrame)
                        box2, __ = listWithFrame[len(listWithFrame) - 1]
                        print(item)
                        print(list)
                        (x1, y1, w1, h1) = box2

                        val = bb_intersection_over_union([xt, yt, xt + wt, yt + ht], [x1, y1, x1 + w1, y1 + h1])
                        print("IoU -------")
                        print(val)
                        print("IoU_______")

                        if (val > 0.20):
                            ___ = True
                            iDsWithIoUList[n] = (___, id, listWithFrame,[(box,ctr)])
                            break

                    tracker, box = trackersList[n]
                    print(box)
                    print("____")
                    redTrackers.append(trackersList[n])
                    redTrackingCounters.append(10)
                    del trackersList[n]
                    distance = distance_to_line((0, thresholdRedLight), (1300, thresholdRedLight), (xmid, ymid))
                    print("EUCLEDIAN DISTANCE")
                    print(distance)
                # here will check if it passes the red light
            return boxes
        def updateRedTrackers(image):
            clonedImage = image.copy()
            for n, pair in enumerate(redTrackers):
                tracker, box = pair

                success, bbox = tracker.update(image)

                if not success:
                    del redTrackers[n]
                    continue

                redTrackingCounters[n] = redTrackingCounters[n] - 1

                if(redTrackingCounters[n] > 0):
                    (xt, yt, wt, ht) = bbox
                    for n, item in enumerate(iDsWithIoUList):
                        print(item)
                        ___, id, listWithFrame, violationList = item

                        if(___ == False):
                            continue
                        print(listWithFrame)
                        box2, __ = listWithFrame[len(listWithFrame) - 1]
                        print(item)
                        print(list)
                        (x1, y1, w1, h1) = box2

                        val = bb_intersection_over_union([xt, yt, xt + wt, yt + ht], [x1, y1, x1 + w1, y1 + h1])
                        print("IoU -------")
                        print(val)
                        print("IoU_______")

                        if (val > 0.20):
                            violationList.append(([bbox],ctr))
                            iDsWithIoUList[n] = (___, id, listWithFrame,violationList)
                            break

                    boxes.append(bbox)  # Return updated box list

                    xmin = int(bbox[0])
                    ymin = int(bbox[1])
                    xmax = int(bbox[0] + bbox[2])
                    ymax = int(bbox[1] + bbox[3])
                    xmid = int(round((xmin + xmax) / 2))
                    ymid = int(round((ymin + ymax) / 2))
                    cv2.rectangle(clonedImage, (xmax, ymax), (xmin, ymin), (0, 0, 255), 2)
                    cropped_image = clonedImage[ymin:ymax, xmin:xmax]
                    cv2.imwrite("object_image.jpg", cropped_image)
            return clonedImage

        def add_object(image, box):
            tracker = cv2.TrackerMedianFlow_create()
            (x, y, w, h) = [int(v) for v in box]

            success = tracker.init(image, (x, y, w, h))

            if success:
                trackersList.append((tracker, (x, y, w, h)))
        # loop over frames from the video file stream
        prevCurrentList = []
        #-----------------------------------

        while True:
            print(thresholdRedLight)
            (grabbed, frame) = cap.read()
            if(not grabbed):
                break
            else:
                frame = cv2.resize(frame, (1000, 750))
            frameTemp2 = frame.copy()
            frameTemp3 = frame.copy()
            boxesTemp = updateTrackers(frame)
            if(ctr % 5== 0):

                frameTemp = frame.copy()

                cv2.line(frameTemp, (0, thresholdRedLight), (1300, thresholdRedLight), (0, 0, 0), 4, cv2.LINE_AA)
                # Draw the running total of cars in the image in the upper-left corner

                print('tracker boxes : ')
                print(boxesTemp)
                print("___ tracked boxes done")
                for idx, box in enumerate(boxesTemp):
                    (x, y, w, h) = [int(v) for v in box]
                    cv2.rectangle(frameTemp, (x, y), (x + w, y + h), (0, 255, 0), 2)
                # read the next frame from the file
                # if the frame was not grabbed, then we have reached the end
                # of the stream
                if not grabbed:
                    break
                # if the frame dimensions are empty, grab them
                if W is None or H is None:
                    (H, W) = frame.shape[:2]
                # construct a blob from the input frame and then perform a forward
                # pass of the YOLO object detector, giving us our bounding boxes
                # and associated probabilities
                blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416),
                    swapRB=True, crop=False)
                net.setInput(blob)
                start = time.time()
                layerOutputs = net.forward(ln)
                end = time.time()

                # initialize our lists of detected bounding boxes, confidences,
                # and class IDs, respectively
                boxes = []
                confidences = []
                classIDs = []

                # loop over each of the layer outputs
                for output in layerOutputs:
                    # loop over each of the detections
                    for detection in output:
                        # extract the class ID and confidence (i.e., probability)
                        # of the current object detection
                        scores = detection[5:]
                        classID = np.argmax(scores)
                        confidence = scores[classID]

                        # filter out weak predictions by ensuring the detected
                        # probability is greater than the minimum probability
                        if confidence > args["confidence"]:
                            # scale the bounding box coordinates back relative to
                            # the size of the image, keeping in mind that YOLO
                            # actually returns the center (x, y)-coordinates of
                            # the bounding box followed by the boxes' width and
                            # height
                            box = detection[0:4] * np.array([W, H, W, H])
                            (centerX, centerY, width, height) = box.astype("int")

                            # use the center (x, y)-coordinates to derive the top
                            # and and left corner of the bounding box
                            x = int(centerX - (width / 2))
                            y = int(centerY - (height / 2))

                            # update our list of bounding box coordinates,
                            # confidences, and class IDs
                            if(classID ==2 or classID==7 or classID ==3 or classID == 9):
                                boxes.append([x, y, int(width), int(height)])
                                confidences.append(float(confidence))
                                classIDs.append(classID)

                # apply non-maxima suppression to suppress weak, overlapping
                # bounding boxes
                idxs = cv2.dnn.NMSBoxes(boxes, confidences, args["confidence"],
                    args["threshold"])
                currentBoxes = []
                # ensure at least one detection exists
                if len(idxs) > 0:
                    # loop over the indexes we are keeping
                    for i in idxs.flatten():
                        # extract the bounding box coordinates
                        (x, y) = (boxes[i][0], boxes[i][1])
                        (w, h) = (boxes[i][2], boxes[i][3])
                        currentBoxes.append((x,y,w,h))
                        # draw a bounding box rectangle and label on the frame
                        cv2.rectangle(frameTemp2, (x, y), (x + w, y + h), (255, 0, 0), 2)
                prevCurrentList = currentBoxes.copy()
                addedBoxes = []
                #---------------------
                index = 0
                for idx, box in enumerate(boxesTemp):
                    if (len(trackersList) == 0):
                        break
                    i = 0
                    (x, y, w, h) = [int(v) for v in box]
                    print('iteration')
                    print((x, y, w, h))
                    flagg = False
                    yt,ht = 0,0
                    for idx2, box2 in enumerate(currentBoxes):
                        (x2, y2, w2, h2) = [int(v2) for v2 in box2]
                        val = bb_intersection_over_union([x,y,x+w,y+h],[x2,y2,x2+w2,y2+h2])

                        print(val)

                        if(val > .25):
                            flagg = True
                            i = idx2
                            yt, ht = y2,h2

                    if(flagg == False):
                        del trackersList[index]
                        del boxesTemp[index]
                        index = index - 1
                    else:
                        print('INDEX DELETED',index)
                        print('Length',len(trackersList))
                        del trackersList[index]


                        index = index - 1
                        addedBoxes.append(currentBoxes[i])

                        (xt,yt, wt, ht) = currentBoxes[i]
                        print(iDsWithIoUList)
                        for n,item in enumerate(iDsWithIoUList):
                            print(item)
                            ___,id,listWithFrame,violationList = item
                            print(listWithFrame)
                            box2, __ = listWithFrame[len(listWithFrame) - 1]
                            print(item)
                            print(list)
                            (x1, y1, w1, h1) = box2


                            val = bb_intersection_over_union([xt, yt, xt + wt, yt + ht], [x1, y1, x1 + w1, y1 + h1])
                            print("IoU -------")
                            print(val)
                            print("IoU_______")
                            if(val > 0.20):
                                listWithFrame.append((currentBoxes[i],ctr))
                                iDsWithIoUList[n] = (___, id, listWithFrame,violationList)
                                break

                    index = index + 1
                #----------------------
                for idx, box in enumerate(currentBoxes):
                    (x, y, w, h) = [int(v) for v in box]
                    flagg = False
                    for box2 in boxesTemp:
                        (x2, y2, w2, h2) = [int(v2) for v2 in box2]
                        val = bb_intersection_over_union([x, y, x + w, y + h], [x2, y2, x2 + w2, y2 + h2])
                        print(val)

                        if (val > .25):
                            flagg = True
                    fl = False
                    if(flagg == False):
                        if ((y + y + h) / 2 > thresholdRedLight):
                            addedBoxes.append(box)
                            print(box)
                            iDsWithIoUList.append((False, idCounter, [(box,ctr)],[]))
                            idCounter = idCounter + 1
                print("______________")
                print("iDs with IoU")
                for i in iDsWithIoUList:
                    print(i)
                print("_______________")

                print(addedBoxes)
                print(len(boxesTemp))
                print('TRACKER LIST LENGTH: ',len(trackersList))
                print(len(penaltyList))
                for box in addedBoxes:
                    add_object(frameTemp2,box)
                    penaltyList.append(0)
                print("_____________")
                print(len(trackersList))
                print(len(penaltyList))

                # check if the video writer is None
            frameTemp3 = updateRedTrackers(frameTemp3)
            if(ylight!=None):
                light = frame[ylight:ylight + hlight, xlight:xlight + wlight]
                b, g, r = cv2.split(light)
                light=cv2.merge([r,g,b])
                greenCount = 0
                if(trafficLightColor.estimate_label(light)=="green"):
                    print('GREEEENNNN')
                cv2.putText(frameTemp3, trafficLightColor.estimate_label(light), (xlight, ylight),cv2.FONT_HERSHEY_DUPLEX, 1.5, (255, 255, 255), 2, cv2.LINE_AA)

            cv2.line(frameTemp3, (0, thresholdRedLight), (1300, thresholdRedLight), (0, 0, 0), 4, cv2.LINE_AA)
            cv2.putText(frameTemp3, 'Violation Counter: ' + str(redLightViolatedCounter), (30, 60),cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 4, cv2.LINE_AA)

            if (displayCounter != 0):
                cv2.putText(frameTemp3, 'Violation', (30, 120),cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 4, cv2.LINE_AA)
                truecount+=1
                displayCounter = displayCounter - 1
                if(truecount == 1):
                    j+=1
                    cv2.imwrite("./output/violation-"+str(j)+".jpg",frameTemp3)
                    if frameTemp3[y:y+h, x:x+w, 2].sum() > frameTemp3[y:y+h, x:x+w, :2].sum():
                            # Crop the image using the bounding box coordinates
                            j+=1
                            cropped_img = frameTemp3[y:y+h, x:x+w]
                            cv2.imwrite('./output/noplate-'+str(j)+'.jpg', cropped_img)
            else:
                truecount = 0
            for idx, box in enumerate(boxesTemp):
                (x, y, w, h) = [int(v) for v in box]
                cv2.rectangle(frameTemp3, (x, y), (x + w, y + h), (0, 255, 0), 2)

            if writer is None:
                # initialize our video writer

                fourcc = cv2.VideoWriter_fourcc(*"MJPG")
                writer = cv2.VideoWriter(args["output"], fourcc, fps,(frameTemp3.shape[1], frameTemp3.shape[0]), True)

                # some information on processing single frame
                if total > 0:
                    elap = (end - start)
                    print("[INFO] single frame took {:.4f} seconds".format(elap))
                    print("[INFO] estimated total time to finish: {:.4f}".format(
                        elap * total))

            # write the output frame to disk
            writer.write(frameTemp3)
            cv2.imshow('frame',frameTemp3)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            ctr = ctr + 1
    if trafficlight_detected:
        Trafficlight()
    else:
        detectviolence()
        
        
cap.release()
cv2.waitKey(1)
cv2.destroyAllWindows()
print("[INFO] cleaning up...")
endTime = time.time()
print('Total Time: ', endTime - startTime)
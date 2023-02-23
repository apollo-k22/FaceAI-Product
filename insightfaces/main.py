import os
import os.path as osp
import argparse
import cv2
import numpy as np
import scipy.spatial.distance as distance
import onnxruntime
from insightfaces.scrfd import SCRFD
from insightfaces.arcface_onnx import ArcFaceONNX
import math, time, json
from pathlib import Path
from cryptophic.main import generate_token

DETECT_ONNX_MODEL = "scrfd_10g_bnkps.onnx"
RECOG_ONNX_MODEL = "glintr100.onnx"
THRESHOLDS = [0.7, 0.8, 0.9]

onnxruntime.set_default_logger_severity(3)
assets_dir = osp.expanduser(r'./models')
detector = SCRFD(os.path.join(assets_dir, DETECT_ONNX_MODEL))
detector.prepare(0)
model_path = os.path.join(assets_dir, RECOG_ONNX_MODEL)
rec = ArcFaceONNX(model_path)
rec.prepare(0)

# Line slope given two points:
def slope(x1, y1, x2, y2): # Line slope given two points:
    return (y2-y1)/(x2-x1)

def angle(s1, s2): 
    return math.degrees(math.atan((s2-s1)/(1+(s2*s1))))

def init_json_data(data):
    data['time_used'] = {}
    data['thresholds'] = {}
    data['faces'] = []
    data['results'] = []
    data['image_id'] = "image id"
    data['request_id'] = "reques id"

    return data

def get_similarity_str(data, similarity, path):
    conclu = ""

    if similarity < THRESHOLDS[0]:
        conclu = 'NOT SIMILAR PERSON'
    elif similarity >= THRESHOLDS[0] and similarity < THRESHOLDS[1]:
        conclu = 'Low match'
    elif similarity >= THRESHOLDS[1] and similarity < THRESHOLDS[2]:
        conclu = 'High match'
    else:
        conclu = 'Highest match'

    return conclu

def append_json_data(data, x1, y1, x2, y2, angle, sim, path):
    _, token = generate_token()
    facedata = {
        'image_path': path,
        'face_token': str(token),
        'face_rectangle': {
            'left': int(x1),
            'top': int(y1),
            'width': int(x2-x1),
            'height': int(y2-y1),
        },
        'face_angle': int(angle)
    }
    result = {
        'image_path': path,        
        'face_token': str(token),
        'confidence': "%4f" % sim,
        'user_id': "",
    }
    
    data['faces'].append(facedata)
    data['results'].append(result)

    return data

def build_json_data(data, time):
    data['time_used'] = int(time)
    data['thresholds'] = {
        'Low match': int(THRESHOLDS[0] * 100),
        'High match': int(THRESHOLDS[1] * 100),
        'Highest match': int(THRESHOLDS[2] * 100),
    }
    data['request_id'] = "request"
    # data = json.dumps(data, indent=4)

    return data

def draw_results(bboxes, kpss, image, angles):
    bboxes=bboxes
    kpsses = kpss
    img=image
    color = (0, 255, 0)
    height, width, channels = img.shape
    print(width)
    print(height)
    print(channels)
    for i in range(bboxes.shape[0]):
        bbox = bboxes[i]
        kpss = kpsses[i]
        x1, y1, x2, y2, x3= bbox
        cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), color, 1)
        # img = cv2.putText(img, 'sim: %f'%sim[i, 0], (int(x1), int(y1)), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 1, cv2.LINE_AA)
        img = cv2.putText(img, 'angle: %f'%angles[i], (int(x1), int(y1)), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 1, cv2.LINE_AA)
        for kps in kpss:
            x, y = kps
            cv2.circle(img, (int(x), int(y)) , 1, color , 2)
    cv2.imshow('Test', img)
    cv2.waitKey(0)

def get_face(image, bbox):
    ystart=int(np.round(bbox[1]))
    ystop=int(np.round(bbox[3]))
    xstart=int(np.round(bbox[0]))
    xstop=int(np.round(bbox[2]))
    return image[ystart:ystop, xstart:xstop]

def findCosineDistance(representation1, representation2):
    # a = np.matmul(np.transpose(representation1), representation2)
    # b = np.sum(np.multiply(representation1, representation1))
    # c = np.sum(np.multiply(representation2, representation2))
    # return 1 - (a / (np.sqrt(b) * np.sqrt(c)))
    return 1 - distance.cosine(representation1, representation2)

# Takes as input subject and target image paths and return json formated data
# pair (path1, path2). "path1" is subject image path. "path2" is target image paths.
def recognition(path1, paths2):
    jsondata = {}
    angles1 = {}
    angles2 = {}  
    image2 = {}  
    sim = {}
    feat2 = []

    jsondata = init_json_data(jsondata)

    start_time = time.time()
    
    image1 = cv2.imread(path1.__str__())
    bboxes1, kpss1 = detector.autodetect(image1, max_num=1)   
    if bboxes1.shape[0]==0:
        return -1.0, "Face not found in Image-1"

    for idx, bbox1 in enumerate(bboxes1):
        x1, y1, x2, y2, z2 = bboxes1[idx]
        pt1, pt2, pt3, pt4, pt5 = kpss1[idx]
        angles1[idx] = angle(slope(x1, y1, x2, y1), slope(pt1[0], pt1[1], pt2[0], pt2[1]))

    feat1 = rec.get(image1, kpss1[0])
    # feat1 = rec.get_feat(get_face(image1, bboxes1[0]))
    # cv2.imshow('Test', get_face(image1, bboxes1[0]))
    # cv2.waitKey(0)

    for index, path2 in enumerate(paths2):
        image2[index] = cv2.imread(path2.__str__())
        bboxes2, kpss2 = detector.autodetect(image2[index], max_num=1)
        if bboxes2.shape[0]==0:
            return -1.0, "Face not found in Image-2"

        x1, y1, x2, y2, z2 = bboxes2[0]
        pt1, pt2, pt3, pt4, pt5 = kpss2[0]
        angles2[index] = angle(slope(x1, y1, x2, y1), slope(pt1[0], pt1[1], pt2[0], pt2[1]))
        
        feat2 = rec.get(image2[index], kpss2[0])
        # feat2 = rec.get_feat(get_face(image2[index], bboxes2[0]))
        # cv2.imshow('Test', get_face(image2[index], bboxes2[0]))
        # cv2.waitKey(0)
        sim[index] = rec.compute_sim(feat1, feat2) * 2
        # sim[index] = findCosineDistance(feat1, feat2) * 2
        if sim[index] > 1: sim[index] = 1
        print("sim: ", sim[index])    

        res = get_similarity_str(jsondata, sim[index], path2)
        jsondata = append_json_data(jsondata, x1, y1, x2, y2, angles2[index], sim[index], path2.__str__())

    end_time = time.time()
    time_used = end_time - start_time

    jsondata = build_json_data(jsondata, time_used)
    print(jsondata)

    # draw_results(bboxes1, kpss1, image1, angles1)

    return jsondata



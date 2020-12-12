import cv2
import numpy as np
import imutils
import base64
import socket
import sys
import pickle
import struct
import time

HOST = '10.0.0.235'
PORT = 8080

# CHANGING RESOLUTION
# width, height = 160, 140
# width, height = 320, 240
width, height = 640, 480


resize_width = 0
# below is accurate when width = 640 and height = 480
# cuts payload size from ~90,000 to (resize_width=240) 11000 (Reaches 36000 payload which drops fps at resize_width = 440)
resize_width = 220

cap=cv2.VideoCapture(0, cv2.CAP_DSHOW)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

clientsocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
clientsocket.connect((HOST,PORT))

def rescale_frame(frame, percent=75):
    width = int(frame.shape[1] * percent / 100)
    height = int(frame.shape[0] * percent / 100)
    dim = (width, height)
    return cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)

true_start = time.time()
count = 0

while True:
    start = time.time()
    ret,frame=cap.read()

    # Maniplating Frame to decrease size
    if resize_width:
        frame = imutils.resize(frame, width=resize_width) 

    # Serialize frame
    # data = pickle.dumps(frame)
    encoded, buffer = cv2.imencode('.jpg', frame)
    frame64 = base64.b64encode(buffer)

    # frame = rescale_frame(frame, percent=50)
    # Send message length first
    message_size = struct.pack("L", len(frame64)) ### CHANGED
    # Then data
    clientsocket.sendall(message_size + frame64)
    
    if count % 30 == 0:
        print('[INFO] Time taken to send data: {}, payload size: {}'.format(time.time() - start, len(frame64)))
    
    count += 1

print('[DISCONNECTED] Connected to server for {} second(s)'.format(time.time() - true_start))
cv2.destroyAllWindows()
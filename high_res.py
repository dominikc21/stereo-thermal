import ctypes
import numpy as np
import os
import cv2
import sys
sys.path.append('/home/ece495-group3/stereo-thermal/lib/python3.11/site-packages')
import torch
#from ultralytics import YOLO
from PIL import Image
from pathlib import Path

model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
	
def new_frame():
	# to compile: gcc -fPIC -shared -o high_res.so high_res.c -lwiringPi
	path = os.path.abspath('high_res.so')
	lib = ctypes.CDLL(path)
	
	array_type = ctypes.c_uint * 4800 * 4
	lib.lepton3.restype = ctypes.POINTER(array_type)
	array_ptr = lib.lepton3()
	arr = np.array(array_ptr.contents)
	
	# reshape and normalize
	reshaped_arr = arr.reshape((120, 160))
	min_val = np.amin(reshaped_arr)
	max_val = np.amax(reshaped_arr)
	normalized_arr = 255.0 * (reshaped_arr - min_val) / (max_val - min_val)
	normalized_arr = np.clip(normalized_arr, 0, 255).astype(np.uint8)
	big_image = cv2.resize(normalized_arr, (320, 240))
	
	return big_image
	
def infer_and_draw(image):
    pil_image = Image.fromarray(image)
    results = model(pil_image)
    annotated_image = results.render()[0]
    return annotated_image

def main():
    while True:
        frame = new_frame()
        #annotated_frame = infer_and_draw(frame)
        cv2.imshow('annotated', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
    cv2.destroyAllWindows()
    
    
if __name__ == '__main__':
    main()

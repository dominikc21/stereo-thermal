import ctypes
import numpy as np
import os
import cv2
import threading

import sys
sys.path.append('/home/ece495-group3/stereo-thermal/lib/python3.11/site-packages')
#import torch
#from ultralytics import YOLO
import time


def new_frame_lep2():
	# to compile: gcc -fPIC -shared -o get_frame.so get_frame.c
	path = os.path.abspath('read_frame.so')
	lib = ctypes.CDLL(path)
	
	array_type = ctypes.c_uint * 4800
	lib.lepton2.restype = ctypes.POINTER(array_type)
	array_ptr = lib.lepton2()
	arr = np.array(array_ptr.contents)
	
	# reshape and normalize
	reshaped_arr = arr.reshape((60, 80))
	min_val = np.amin(reshaped_arr)
	max_val = np.amax(reshaped_arr)
	print(min_val)
	print(max_val)
	normalized_arr = 255.0 * (reshaped_arr - min_val) / (max_val - min_val)
	normalized_arr = np.clip(normalized_arr, 0, 255).astype(np.uint8)
	big_image = cv2.resize(normalized_arr, (320, 240))
	
	return big_image
	
def new_frame_lep3():
	# to compile: gcc -fPIC -shared -o get_frame.so get_frame.c
	path = os.path.abspath('read_frame.so')
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

def main():


	while True:
		"""
		thread1 = threading.Thread(target=new_frame_lep2)
		thread2 = threading.Thread(target=new_frame_lep3)

		thread1.start()
		thread2.start()

		image1 = thread1.join()
		image2 = thread2.join()

		#image1 = thread1.result()
		#image2 = thread2.result()
		"""
		image1 = new_frame_lep2()
		image2 = new_frame_lep3()
		cv2.imshow('Low-res', image1)
		cv2.imshow('High-res', image2)
		if cv2.waitKey(1) & 0xFF == ord('q'):
		    break

	cv2.destroyAllWindows()
    
    
    # test inference
	"""
	image2 = new_frame_lep3()
	model = YOLO('yolov5su.pt')
	cv2.imwrite('im.jpg', image2)
	img = cv2.imread('im.jpg')
	model.predict(source=img, save=True, save_txt=False, conf=0.2, verbose=False)
	"""
    
if __name__ == '__main__':
    main()

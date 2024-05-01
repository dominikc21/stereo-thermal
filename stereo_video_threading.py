import ctypes
import numpy as np
import os
import cv2
import threading
import sys
import time
import math
from queue import Queue
shared_queue = Queue()

display_lock = threading.Lock()

def new_frame_lep2():
    det_type = 1 # 0 for specific temperature value, 1 for elevated temperature compared to average
    temp = 30
    buff = 1
    
    path = os.path.abspath('low_res.so')
    lib = ctypes.CDLL(path)
    array_type = ctypes.c_uint * 4800
    lib.lepton2.restype = ctypes.POINTER(array_type)
    array_ptr = lib.lepton2()
    arr = np.array(array_ptr.contents)
    
    # reshape and normalize
    reshaped_arr = arr.reshape((60, 80))
    min_val = np.amin(reshaped_arr)
    max_val = np.amax(reshaped_arr)
    #print(min_val)
    #print(max_val)
    int_arr = np.uint16(reshaped_arr)
    rot_arr = cv2.rotate(int_arr, cv2.ROTATE_90_CLOCKWISE)
    proc_lep2 = temp_recognition(rot_arr, temp, buff, 120, 160, det_type)
    shared_queue.put(proc_lep2)
    normalized_arr = 255.0 * (proc_lep2['original_image'] - min_val) / (max_val - min_val)
    normalized_arr = np.clip(normalized_arr, 0, 255).astype(np.uint8)
    big_image = cv2.resize(normalized_arr, (320, 240))
    
    return big_image
	
def new_frame_lep3():
    det_type = 1 # 0 for specific temperature value, 1 for elevated temperature compared to average
    temp = 30
    buff = 1
    lep3_data = {
    'focal_length': 0.00177,
	'pixel_size': 0.000012,
	'camera_dist': 1}
    lep2_data = {
    'focal_length': 0.00146,
	'pixel_size': 0.000017}
    
    # get data
    path = os.path.abspath('high_res.so')
    lib = ctypes.CDLL(path)
    array_type = ctypes.c_uint * 4800 * 4
    lib.lepton3.restype = ctypes.POINTER(array_type)
    array_ptr = lib.lepton3()
    arr = np.array(array_ptr.contents)
    
    # reshape and normalize
    reshaped_arr = arr.reshape((120, 160))
    reshaped_arr[63] = (reshaped_arr[62] + reshaped_arr[64])/2
    min_val = np.amin(reshaped_arr)
    max_val = np.amax(reshaped_arr)
    int_arr = np.uint16(reshaped_arr)
    rot_arr = cv2.rotate(int_arr, cv2.ROTATE_90_COUNTERCLOCKWISE)
    proc_lep3 = temp_recognition(rot_arr, temp, buff, 120, 160, det_type)
    proc_lep2 = shared_queue.get()
    final_return = dist_meas(proc_lep3, proc_lep2, lep3_data, lep2_data)
    normalized_arr = 255.0 * (final_return['big_image'] - min_val) / (max_val - min_val)
    normalized_arr = np.clip(normalized_arr, 0, 255).astype(np.uint8)
    big_image = cv2.resize(normalized_arr, (320, 240))
    
    return big_image

def process_frame(frame_func, title):  
    i = 1 
    j = 1
    while True:
        start = time.time()
        if frame_func == new_frame_lep2:
            image1 = frame_func()
            if i == 0:
                cv2.imwrite('low.jpg', image1)
                i += 1
            with display_lock:
                cv2.imshow(title, image1)
        else:
            image2 = frame_func()
            if j == 0:
                cv2.imwrite('high.jpg', image2)
                j += 1
            with display_lock:
                cv2.imshow(title, image2)
        end = time.time()
        #print(end - start)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
def main():
    # separate processes and execute in parallel
    thread2 = threading.Thread(target=process_frame, args=(new_frame_lep2, '1',))
    thread1 = threading.Thread(target=process_frame, args=(new_frame_lep3, '2',))
    thread2.start()
    thread1.start()
    thread2.join()
    thread1.join()
    cv2.destroyAllWindows()

'''This function takes an image array along with a temperature, a temperature
buffer and a detection type. It outputs the location of pixels at the given
temperature along with processed images.'''
def temp_recognition(input_image, temp, buff, height, width, det_type):
    height, width = input_image.shape[:2]
    # Converts the input image array to unsigned, 16-bit integers (needed for cv2 processing)
    gray16_image = np.uint16(input_image)
    # Initialize the location of pixels in the x and y direction
    x_location = []
    y_location = []
    
    
    # For det_type 0, checks the value of each pixel and determined whether or not it is within the temperature buffer and records the location of each pixel within this range
    # Note: this used the formula P = T*25, where P is the pixel value and T is the temperature in Kelvin
    if det_type == 0:
        for i in range(height):
            for j in range(width):
                if (gray16_image[i,j]<((temp + 273.15)*25 + buff*100) and gray16_image[i,j]>((temp + 273.15)*25 - buff*100)):
                    x_location.append(j)
                    y_location.append(i)
                j+=1
            i+=1
    # For det_type 1, all pixels within the top 30% of the value range are recorded
    else:
        crit_val = np.min(gray16_image)+(np.max(gray16_image)-np.min(gray16_image))*0.7
        for i in range(height):
            for j in range(width):
                if (gray16_image[i,j]>crit_val):
                    x_location.append(j)
                    y_location.append(i)
                j+=1
            i+=1
    
    
    # If pixels are recorded, these if statements calculate the rounded average location and range in the x and y directions
    # If there are no recorded pixels, the averages and ranges are set to -1 (the 'no object found' code)
    if x_location:
        x_average = int(np.average(x_location))
        x_range = x_location[len(x_location)-1] - x_location[0]
    else:
        x_average = -1
        x_range = -1
    if y_location:
        y_average = int(np.average(y_location))
        y_range = y_location[len(y_location)-1] - y_location[0]
    else:
        y_average = -1
        y_range = -1
    
    
    # If pixels are recorded, this draws a rectangle around them (with a 5 pixel spacing around them) and writes the temperature value for det_type 0
    if x_average != -1 and y_average != -1:
        if det_type == 0:
            # write temperature value
            cv2.putText(gray16_image,"{0:.1f} C".format(temp),(x_average - math.ceil(x_range/2), y_average), cv2.FONT_HERSHEY_PLAIN, 0.8,(255,0,0),2)

        # write temperature square
        cv2.rectangle(gray16_image, pt1=(x_average - math.ceil(x_range/2) - 5, y_average - math.ceil(y_range/2) - 5), pt2=(x_average + math.ceil(x_range/2) + 5, y_average + math.ceil(y_range/2) + 5), color = (0, 0, 255), thickness = 1)
    else:
        cv2.putText(gray16_image,"No Object Detected",(int(10), int(height/2)), cv2.FONT_HERSHEY_PLAIN, 0.8,(255,0,0),2)
    

    # Returns all useful values as a dictionary so that errors don't occur if they are blank
    temp_recognition_return = {
        'original_image': gray16_image,
        'x_average': x_average,
        'y_average': y_average,
        'y_range': y_range,
        'x_range': x_range}   
    
    
    return(temp_recognition_return)
    
    
def dist_meas(lep3_return, lep2_return, lep3_data, lep2_data):
    
    errors = []
    #Check to ensure that the data has been correctly imported
    try:
        float(lep3_data['pixel_size'])
    except:
        errors.append('905')
    try:
        float(lep3_data['focal_length'])
    except:
        errors.append('905')
    try:
        float(lep3_data['camera_dist'])
    except:
        errors.append('905')
    try:
        float(lep2_data['pixel_size'])
    except:
        errors.append('906')
    try:
        float(lep2_data['focal_length'])
    except:
        errors.append('906')
    try:
        float(lep3_return['x_average'])
    except:
        errors.append('907')
    try:
        float(lep3_return['y_average'])
    except:
        errors.append('907')
    
    

    # If no import errors occur, this calculates the distance to the recognized object
    if not ('905' in errors or '906' in errors or '907' in errors):
        Z = 0
        if lep3_return['x_average']!=-1 and lep3_return['y_average']!=-1:
            lep3_term = lep3_data['pixel_size']*lep3_return['x_average']/\
                (lep3_data['focal_length']*lep3_data['camera_dist'])
            lep2_term = lep2_data['pixel_size']*lep2_return['x_average']/\
                (lep2_data['focal_length']*lep3_data['camera_dist'])
                
            # Double checking that we won't get divide by zero errors (occurs for very far away objects
            if lep2_term != lep3_term:
                Z = 1/abs(lep3_term - lep2_term)
            else:
                Z = 999
            cv2.putText(lep3_return['original_image'],"{0:.1f} m".format(Z),(lep3_return['x_average'] - math.ceil(lep3_return['x_range']/2), lep3_return['y_average'] + 10), cv2.FONT_HERSHEY_PLAIN, 0.8, (255,0,0),2)

        # Returns all useful information (x_average, y_average and distance won't be used in our program, but could be used by a drone if necessary)
        dist_return = {
            'big_image': lep3_return['original_image'],
            'x_average': lep3_return['x_average'],
            'y_average': lep3_return['y_average'],
            'distance': Z,
            'errors': errors}
    else:
        print(errors)
        dist_return = {
            'errors': errors}
        
        
    return dist_return
    
if __name__ == '__main__':
    main()

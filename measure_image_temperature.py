# import the necessary packages
import numpy as np
import cv2
import math

'''This function takes an image array along with a temperature, a temperature
buffer and a detection type. It outputs the location of pixels at the given
temperature along with processed images.'''
def temp_recognition(input_image, temp, buff, height, width, det_type):

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
            cv2.putText(gray16_image,"{0:.1f} C".format(temp),(x_average - 10, y_average), cv2.FONT_HERSHEY_PLAIN, 0.8,(255,0,0),2)

        # write temperature square
        cv2.rectangle(gray16_image, pt1=(x_average - math.ceil(x_range/2) - 5, y_average - math.ceil(y_range/2) - 5), pt2=(x_average + math.ceil(x_range/2) + 5, y_average + math.ceil(y_range/2) + 5), color = (0, 0, 255), thickness = 1)
    else:
        cv2.putText(gray16_image,"No Object Detected",(int(10), int(height/2)), cv2.FONT_HERSHEY_PLAIN, 0.8,(255,0,0),2)
    

    # Returns all useful values as a dictionary so that errors don't occur if they are blank
    temp_recognition_return = {
        'original_image': gray16_image,
        'x_average': x_average,
        'y_average': y_average,
        'y_range': y_range}   
    
    
    return(temp_recognition_return)


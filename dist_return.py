# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 09:57:49 2024

@author: Owner
"""
import cv2



def dist_meas(highq_return, lowq_return, highq_data, lowq_data, errors):
    
    
    #Check to ensure that the data has been correclty imported
    try:
        float(highq_data['pixel_size'])
    except:
        errors.append('905')
    try:
        float(highq_data['focal_length'])
    except:
        errors.append('905')
    try:
        float(highq_data['camera_dist'])
    except:
        errors.append('905')
    try:
        float(lowq_data['pixel_size'])
    except:
        errors.append('906')
    try:
        float(lowq_data['focal_length'])
    except:
        errors.append('906')
    try:
        float(highq_return['x_average'])
    except:
        errors.append('907')
    try:
        float(lowq_return['y_average'])
    except:
        errors.append('907')
    
    

    
    if not ('905' in errors or '906' in errors or '907' in errors):
        highq_term = highq_data['pixel_size']*highq_return['y_average']/\
            (highq_data['focal_length']*highq_data['camera_dist'])
        lowq_term = lowq_data['pixel_size']*lowq_return['y_average']/\
            (lowq_data['focal_length']*highq_data['camera_dist'])
        Z = 1/(lowq_term - highq_term)
        
        cv2.putText(highq_return['scaled_image'],"{0:.1f} m".format(Z),(highq_return['x_average'] - 25, highq_return['y_average'] + 45), cv2.FONT_HERSHEY_PLAIN, 1,(255,0,0),2)

        
        dist_return = {
            'scaled_image': highq_return['scaled_image'],
            'original_image': highq_return['original_image'],
            'output_image': highq_return['output_image'],
            'x_average': highq_return['x_average'],
            'y_average': highq_return['y_average'],
            'distance': Z,
            'errors': errors}
    else:
        dist_return = {
            'errors': errors}
        
        
    return dist_return
        
        
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 09:57:49 2024

@author: Owner
"""
import cv2



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
            lep3_term = lep3_data['pixel_size']*lep3_return['y_average']/\
                (lep3_data['focal_length']*lep3_data['camera_dist'])
            lep2_term = lep2_data['pixel_size']*lep2_return['y_average']/\
                (lep2_data['focal_length']*lep3_data['camera_dist'])
                
            # Double checking that we won't get divide by zero errors (occurs for very far away objects
            if lep2_term != lep3_term:
                Z = 1/abs(lep2_term - lep3_term)
            else:
                Z = 999
            cv2.putText(lep3_return['big_image'],"{0:.1f} m".format(Z),(lep3_return['x_average']*2 - 20, lep3_return['y_average']*2 + 20), cv2.FONT_HERSHEY_PLAIN, 1.6, (255,0,0),2)

        # Returns all useful information (x_average, y_average and distance won't be used in our program, but could be used by a drone if necessary)
        dist_return = {
            'big_image': lep3_return['big_image'],
            'x_average': lep3_return['x_average'],
            'y_average': lep3_return['y_average'],
            'distance': Z,
            'errors': errors}
    else:
        print(errors)
        dist_return = {
            'errors': errors}
        
        
    return dist_return

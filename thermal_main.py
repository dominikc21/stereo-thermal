# -*- coding: utf-8 -*-
"""
Created on Sat Jan 20 14:59:25 2024

@author: Owner
"""
import cv2
from measure_image_temperature import temp_recognition
from thermal_output_processing import get_errors
from dist_return import dist_meas


def thermal_main():
    errors = []
    temp = 58.0
    buffer = 2
    highq_data = {
        'focal_length': 0.00177, #default 0.00177
        'pixel_size': 0.000012, #default 0.000012
        'camera_dist': 1} #default 1.4
    lowq_data = {
        'focal_length': 0.00146, #default 0.00146
        'pixel_size': 0.000017} #default 0.000017
    
    
    # open the gray16 image
    try: 
        highq_img = cv2.imread("lighter_gray16_image.tiff", cv2.IMREAD_ANYDEPTH)
    except:
        errors.append('903')
    try:
        lowq_img = cv2.imread("lighter_gray16_image.tiff", cv2.IMREAD_ANYDEPTH)
    except:
        errors.append('903')
    
    
    highq_return = temp_recognition(highq_img, temp, buffer, errors)
    errors.append(highq_return['errors'])
    
    
    lowq_return = temp_recognition(lowq_img, temp, buffer, errors)
    errors.append(lowq_return['errors'])
    
    
    distance_return = dist_meas(highq_return, lowq_return, highq_data, lowq_data, errors)
    errors.append(distance_return['errors'])
    
    
    if ('901' in errors or '902' in errors or '903' in errors or '904' in errors\
        or '905' in errors or '906' in errors or '907' in errors):
        err_msg = get_errors(highq_return['errors'])
        main_return = {
            'errors': errors,
            'err_msg': err_msg}
    else:
        main_return = {
            'scaled_image': distance_return['scaled_image'],
            'original_image': distance_return['original_image'],
            'output_image': distance_return['output_image'],
            'x_average': distance_return['x_average'],
            'y_average': distance_return['y_average'],
            'distance': distance_return['distance'],
            'errors': errors}
    
    
    return main_return


if __name__ == "__main__":
    main_return = thermal_main()



    if not ('901' in main_return['errors'] or '902' in main_return['errors'] or '903' in main_return['errors'] or \
            '904' in main_return['errors'] or '905' in main_return['errors'] or '906' in main_return['errors'] or \
            '907' in main_return['errors']):
        cv2.imshow("gray8-celsius", main_return['scaled_image'])
        cv2.imshow("gray16-celsius", main_return['original_image'])
        cv2.imshow("output_image", main_return['output_image'])
        cv2.waitKey(0)

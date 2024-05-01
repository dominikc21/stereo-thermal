# -*- coding: utf-8 -*-
"""
Created on Sat Jan 20 15:11:40 2024

@author: Owner
"""

def get_errors(errors):
    err_msg = []
    if '901' in errors:
        err_msg.append('Error 901: Invalid input for detection temperature.')
    if '902' in errors:
        err_msg.append('Error 902: Detection temperature is outside of camera range.')
    if '903' in errors:
        err_msg.append('Error 903: Image import failed.')
    if '904' in errors:
        err_msg.append('Error 904: Location of object could not be identified.')
    if '905' in errors:
        err_msg.append('Error 905: Invalid high quality camera data entered.')
    if '906' in errors:
        err_msg.append('Error 906: Invalid low quality camera data entered.')
    if '907' in errors:
        err_msg.append('Error 907: Location of object not present in triangulation code.')
    
    get_errors_return = {
        'err_msg': err_msg}
    
    
    return get_errors_return

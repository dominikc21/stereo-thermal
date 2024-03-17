import spidev
import numpy as np
import cv2
import matplotlib.pyplot as plt
    
def main():
    spi = spidev.SpiDev()
    spi.open(0, 0)
    spi.max_speed_hz = 20 * 1000 * 1000

    bytes_per_frame = 60*80*2
    header_size = 4 # bytes
    payload_size = 160 # bytes
    raw_data = np.array([])
    pixel_data_14bit = np.array([])
    i = 0
    while i < 60:
        payload = np.array(spi.readbytes(164))
        if payload[1] != 255: # if not full of zeros
            pixels = payload[4:] # discarding header
            raw_data = np.append(raw_data, pixels) 
            i += 1
    print(len(raw_data))
    for e in range(int(len(raw_data)/2)):
        first_6bit = int(raw_data[2*e])
        last_8bit = int(raw_data[2*e + 1])
        pix_value = (first_6bit << 8) | last_8bit
        pixel_data_14bit = np.append(pixel_data_14bit, pix_value)
        
    image = pixel_data_14bit.reshape((60, 80))
    normalized_image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    big = cv2.resize(normalized_image, (320, 240))
    cv2.imshow('aaa', big)
    cv2.imwrite('/home/ece495-group3/test_image.png', big)
    cv2.waitKey(0)
    spi.close()
    cv2.destroyAllWindows()
    
if __name__ == '__main__':
    main()

import spidev
import numpy as np
import cv2
import RPi.GPIO as GPIO
import time

def sync():
    GPIO.setmode(GPIO.BOARD)
    cs_pin = 8
    GPIO.setup(cs_pin, GPIO.OUT)
    
    # deassert chip select
    GPIO.output(cs_pin, GPIO.HIGH)
    
    # wait for at least 5 frame periods (>185ms)
    time.sleep(0.185)
    
    GPIO.output(cs_pin, GPIO.LOW)
    
    GPIO.cleanup()

def raw14_to_8bit(data):
    
    pixel_data_14bit = np.array([])
    
    # take every two consecutive bytes, convert to one 14 bit value
    for e in range(int(len(data)/2)):
        first_6bit = int(data[2*e])
        last_8bit = int(data[2*e + 1])
        pix_value = (first_6bit << 8) | last_8bit
        pixel_data_14bit = np.append(pixel_data_14bit, pix_value)
        
    # resize from array
    if len(pixel_data_14bit) == 4800:
        image = pixel_data_14bit.reshape((60, 80))
    elif len(pixel_data_14bit) == 19200:
        image = pixel_data_14bit.reshape((120, 160))
        
    # normalize to 8 bit pixel values
    normalized_image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    
    return normalized_image
    

def read_spi_data_high_res(spi): # reads one frame
    raw_data = np.array([])
    seg_data = np.array([])
    
    segment_index = 1
    discard = 0
    wrong_seg = 0
    while segment_index < 5:
        packet_index = 0
        while packet_index < 60:
            payload = np.array(spi.readbytes(164))
            header_ID = payload[0]
            TTT = (payload[0] & 0b01110000) >> 4
            

            
            packet_number = ((payload[0] << 8) | payload[1]) & 0b0000111111111111

            if header_ID & 0b00001111 == 15:
                discard += 1
            else:
                if packet_number == packet_index:
                    seg_data = np.append(seg_data, payload[4:])
                    packet_index += 1
                elif packet_number > 59:
                    sync()
                else:
                    continue
                    
                if packet_number == 20 and TTT != segment_index: # restart reading segment
                    seg_data = np.array([])
                    packet_index = 0

        raw_data = np.append(raw_data, seg_data)
        seg_data = np.array([])
        segment_index += 1
            
            
    # takes array of length 38400 for full image
    image = raw14_to_8bit(raw_data)
    
    big_image = cv2.resize(image, (320, 240))
    return big_image
    
def read_spi_data_low_res(spi): # reads one frame
    bytes_per_frame = 60*80*2
    header_size = 4 # bytes
    payload_size = 160 # bytes
    raw_data = np.array([])
    pixel_data_14bit = np.array([])
    
    # take 60 payloads for each frame
    i = 0
    while i < 60:
        payload = np.array(spi.readbytes(164))
        if payload[1] != 255: # if not full of zeros
            pixels = payload[4:] # discarding header
            raw_data = np.append(raw_data, pixels) 
            i += 1
            
    image = raw14_to_8bit(raw_data)
    
    big_image = cv2.resize(image, (320, 240))
    return big_image
    
    
    
def main():
    # initialize
    spi1 = spidev.SpiDev()
    spi2 = spidev.SpiDev()
    
    # open
    spi1.open(0, 0) # high res
    spi2.open(1, 0) # low res
    
    # set max bus speed
    spi1.max_speed_hz = 24 * 1000 * 1000
    spi2.max_speed_hz = 24 * 1000 * 1000

    sync()
    
    while True:
        image_high_res = read_spi_data_high_res(spi1)
        image_low_res = read_spi_data_low_res(spi2)
        cv2.imshow('high res', image_high_res)
        cv2.imshow('lew res', image_low_res)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
    # close bus
    spi1.close()
    spi2.close()
    cv2.destroyAllWindows()
    
if __name__ == '__main__':
    main()

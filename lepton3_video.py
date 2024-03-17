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
    image = pixel_data_14bit.reshape((120, 160))
        
    # normalize to 8 bit pixel values
    normalized_image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    
    return normalized_image
    

def read_spi_data(spi): # reads one frame
    raw_data = np.array([])
    seg_data = np.array([])
    
    segment_index = 1
    discard = 0
    wrong_seg = 0
    wrong_packet = 0
    while segment_index < 5:
        packet_index = 0
        while packet_index < 60:
            payload = np.array(spi.readbytes(164))
            header_ID = payload[0]
            TTT = (payload[0] & 0b01110000) >> 4
            #print(payload)

            
            packet_number = ((payload[0] << 8) | payload[1]) & 0b0000111111111111

            if header_ID & 0b00001111 == 15:
                discard += 1
            else:
                
                if packet_number == packet_index:
                    seg_data = np.append(seg_data, payload[4:])
                    packet_index += 1
                elif packet_number > 59:
                    wrong_packet += 1
                    sync()
                    #print("packet fail")
                    
                if packet_number == 20 and TTT != segment_index: # restart reading segment
                    seg_data = np.array([])
                    packet_index = 0
                    wrong_seg += 1
                    #print("segment fail")
                else:
                    continue

        raw_data = np.append(raw_data, seg_data)
        seg_data = np.array([])
        segment_index += 1
            
            
    # takes array of length 38400 for full image
    image = raw14_to_8bit(raw_data)
    
    big_image = cv2.resize(image, (320, 240))
    return big_image
    
def main():
    # open bus
    spi = spidev.SpiDev()
    spi.open(0, 0)
    
    # set max bus speed
    spi.max_speed_hz = 24 * 1000 * 1000
    
    sync()
    
    while True:
        image = read_spi_data(spi)
        cv2.imshow('Camera Image', image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
    # close bus
    spi.close()
    cv2.destroyAllWindows()
    
if __name__ == '__main__':
    main()

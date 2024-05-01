# Stereo Imaging with Flir Leptons
This project uses a Lepton 2.5 and a Lepton 3.5 (to save costs) separated by a fixed distance to determine the distance to a recognized object. We used a Raspberry Pi 4B to take the data from the cameras and process it to output.


![alt text](https://github.com/dominikc21/stereo-thermal/images/stereo-thermal_device.heic?raw=true)


## Hardware
The cameras we used in this project are the FLIR [Lepton 2.5](https://www.digikey.ca/en/products/detail/flir-lepton/500-0763-01/6250105) (60 x 80 resolution) and the [Lepton 3.5](https://www.digikey.ca/en/products/detail/flir-lepton/500-0771-01/7606616) (120 x 160). The choice not to go with both Lepton 3.5s was due to costs (~$70 CAD difference). The high-resolution camera gives a better viewing experience. Each camera was mounted on a [Lepton breakout board](https://www.digikey.ca/en/products/detail/flir-lepton/250-0577-00/10385179). We went with the Raspberry Pi 4B 8GB RAM for the computer.

## Software
The VoSPI (Video over SPI) protocol is used to gather frames in the RAW14 format (this protocol is detailed in the engineering datasheets). This portion of the software is written in C using 'lWiringpi'. We originally tested it in Python but it resulted in a poor frame rate. The C functions for gathering frames are called from a Python program using the 'ctypes' package. To further increase the speed at which frames can be processed and displayed, we implemented separate threads to process the two input streams separately. 

## Guide


![alt text](https://github.com/dominikc21/stereo-thermal/images/detailed_wiring_diagram.png?raw=true)


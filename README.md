# Stereo Imaging with Flir Leptons
This project uses a Lepton 2.5 and a Lepton 3.5 (to save costs) separated by a fixed distance to determine the distance to a recognized object. We used a Raspberry Pi 4B to take the data from the cameras and process it to output.

## Guide
Connect the Lepton 3.5 to spidev0.0 and the Lepton 2.5 to spidev1.0 (after enabling it in config.txt). Connect the RESET_L pin of the cameras to GPIO 23 (WiringPi 4) and GPIO 24 (WiringPi 5), for the 3.5 and 2.5, respectively. The cameras should be fixed relative to each other. We used an aluminum pole (~1m) with 3D-printed housings for the cameras on both ends, so the cameras are sideways.

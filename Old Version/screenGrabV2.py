from random import randint
import time
import cv2
import mss
import numpy
from PIL import Image, ImageGrab

import dxcam

with mss.mss() as sct:
    # Part of the screen to capture
    monitor = sct.monitors[1]

    pixels = [ {"top": randint(10, monitor['height']) - 10, "left": randint(10, monitor['width']) - 10, "width": 9, "height": 9} for i in range(1) ]
    
    camera = dxcam.create()

    last_time = time.time()

    for i in range(0, 100):
    #while "Screen capturing":

        # Get raw pixels from the screen, save it to a Numpy array
        #img = sct.grab(monitor)

        # DXCAM
        frame = camera.grab()

        # Display the picture
        #cv2.imshow("OpenCV/Numpy normal", img)#cv2.resize(img, dsize, interpolation=cv2.INTER_NEAREST))

        #img_scaled = img[0:monitor["width"]:5]

        # Display the picture in grayscale
        # cv2.imshow('OpenCV/Numpy grayscale',
        #            cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY))

        #x = randint(0, monitor['width']) - 1
        #y = randint(0, monitor['height']) - 1

        #print(str(img[y][x]) + ", " + str(img[y]) + 25 * ' ', end='\r')
        
        #frametimes.append(time.time() - last_time)

        print(f'Testing... {i}/500' + 25*' ', end='\r')

    average_frametime = (time.time() - last_time) / 100
    print("\nAverage FPS: {}".format(1 / average_frametime))
    #Image.fromarray(frame).show()

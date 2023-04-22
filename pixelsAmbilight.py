import sys
import threading
from time import sleep, time
from config import Config
import numpy as np
from numpy import array, mean, median, bincount
import dxcam
from multiprocessing import Pool, Process
from cuesdk.structs import CorsairLedColor

from multiprocessing.pool import ThreadPool

class PixelsAmbilight: 
    
    def __init__(self, sdk, canvas):
        self.sdk = sdk
        self.canvas = canvas

        self.frametime = 1
        self.errors = 0

        self.running = True
        color = threading.Thread(target=self.color_thread)
        color.start()
        #flush = threading.Thread(target=self.flush_thread)
        #flush.start()

        #self.color_thread()

        self.log_thread()

    def color_thread(self):

        camera = dxcam.create()

        while self.running:
            start = time()

            img = camera.grab()

            if img is None:
                continue

            print

            process_args = [(img, device_index, self.canvas['leds'][device_index]) for device_index in self.canvas['leds'].keys()]

            for device_index in self.canvas['leds'].keys():
                #print(f"Started process for Device {device_index}")
                thread = threading.Thread(target=self.device_thread, args=(img, device_index, self.canvas['leds'][device_index]))
                thread.start()

            self.sdk.set_led_colors_flush_buffer()
            self.frametime = (time() - start)
            #break

            #with Pool(4) as p:
            #    p.map(self.device_thread, img_list)

    def device_thread(self, img, device_index, device_leds):
        #device_index = 0
        #device_leds = self.canvas['leds'][device_index]

        colors = []
        for led in device_leds:
            #print(led)
            #for x in range(0, 10):
            #    for y in range(0, 10):
            #        color = img[max(led[1][1] -x, 0) * 30][max(led[1][0] - y, 0) * 30]
            x = max(led[1][1], 0)
            y = max(led[1][0], 0)
            steps = 1
            points = 3
            
            r = []
            g = []
            b = []

            for _x in range(points):
                x_coord = int(max(0, x - (_x * steps)))
                for _y in range(points):
                    y_coord = int(max(0, y - (_y * steps)))

                    r.append(img[x_coord][y_coord][0])
                    g.append(img[x_coord][y_coord][1])
                    b.append(img[x_coord][y_coord][2])
            #print(color)
            colors.append(CorsairLedColor(led[0], int(np.average(r)), int(np.average(g) * 0.75), int(np.average(b) * 0.65)))
            
        self.sdk.set_led_colors_buffer_by_device_index(device_index, colors)
        #self.sdk.set_led_colors_flush_buffer()

    def flush_thread(self):
        while self.running:
            self.sdk.set_led_colors_flush_buffer()

    def log_thread(self):
        print("\nLoaded Average Ambilight module")
        while True:
            print(f" > Average FPS: {int(1 / self.frametime)} | Errors: {self.errors}" + 20 * "", end='\r')
            sleep(1)
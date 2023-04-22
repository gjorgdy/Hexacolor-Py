import sys
import threading
from time import sleep, time
from config import Config
import numpy as np
from numpy import array, mean, median, bincount
import dxcam
from multiprocessing import Pool, Process
from cuesdk.structs import CorsairLedColor
from grid_canvas import Canvas as gCanvas
import colorsys

import statistics

from multiprocessing.pool import ThreadPool

class PixelsAmbilight: 
    
    def __init__(self, sdk, canvas : gCanvas):
        self.sdk = sdk
        self.canvas = canvas

        self.frametime = 1
        self.errors = 0

        self.running = True
        color = threading.Thread(target=self.color_thread)
        color.start()

        self.size = 0
        self.vertical_bars = 0
        self.horizontal_bars = 0

        #self.color_thread()

        self.log_thread()

    def color_thread(self):

        camera = dxcam.create()

        size_printed = False

        img = camera.grab()
        y_steps = int(len(img) / self.canvas.height)
        middle_y = int(len(img) / 2)
        x_steps = int(len(img[0]) / self.canvas.width)
        middle_x = int(len(img[0]) / 2)

        while self.running:
            start = time()

            img = camera.grab()

            if img is None:
                continue

            vertical_bars = 1
            for i in range(0, int(self.canvas.width/2)):
                x = i * (x_steps - 1)
                r, g, b = img[middle_y][x]
                if (r, g, b) == (0, 0, 0):
                    vertical_bars =  x + x_steps
                else:
                    break

            horizontal_bars = 1
            #for i in range(0, int(self.canvas.height/2)):
            #    y = i * (y_steps - 1)
            #    r, g, b = img[y][middle_x]
            #    if (r, g, b) != (0, 0, 0):
            #        horizontal_bars =  y
            #        break

            # remove vertical bars
            if 0 < horizontal_bars < len(img)/2:
                img = img[horizontal_bars:]
                img = img[:-horizontal_bars]
            self.horizontal_bars = horizontal_bars
            if (vertical_bars != 0) and (vertical_bars < len(img[0])):
                img = [xs[vertical_bars:] for xs in img]
                img = [xs[:-vertical_bars] for xs in img]
            self.vertical_bars = vertical_bars
            
            self.size = (len(img), len(img[0]))

            if len(img) < self.canvas.height:
                continue
            if len(img[0]) < self.canvas.width:
                continue

            y_steps = int(len(img) / self.canvas.height)
            x_steps = int(len(img[0]) / self.canvas.width)

            img = img[::y_steps]
            img = [xs[::x_steps] for xs in img]

            #process_args = [(img, device_index, self.canvas['leds'][device_index]) for device_index in self.canvas['leds'].keys()]
            try:
                for index, leds in self.canvas.devices.items():
                    #print(f"Started process for Device {device_index}")
                    #thread = threading.Thread(target=self.device_thread, args=(img, index, leds))
                    #thread.start()
                    self.device_thread(img, index, leds)
            except:
                break

            #break

            self.sdk.set_led_colors_flush_buffer()
            self.frametime = (time() - start)


            #with Pool(4) as p:
            #    p.map(self.device_thread, img_list)

    def device_thread(self, img, index, leds):

        filter_color = self.sdk.get_device_info(index).model in ("ASUS Motherboard")

        colors = []
        for led in leds:
            led_id, pos0, pos1 = led

            dx = pos1[0] - pos0[0]
            dy = pos1[1] - pos0[1]
            
            r = []
            g = []
            b = []

            for x_step in range(dx):
                _x = (pos0[0] + x_step)
                for y_step in range(dy):
                    _y = (pos0[1] + y_step)

                    r.append(img[_y][_x][0])
                    g.append(img[_y][_x][1])
                    b.append(img[_y][_x][2])

            if (len(r) > 0) and (len(g) > 0) and (len(b) > 0):
                #color = (r[0], g[0], b[0])
                #print(color, end='\r')
                avg_r = int(np.mean(r))
                avg_g = int(np.mean(g))
                avg_b = int(np.mean(b))

                hsv = colorsys.rgb_to_hsv(avg_r/255, avg_g/255, avg_b/255)

                if filter_color:
                    r, g, b = colorsys.hsv_to_rgb(hsv[0], hsv[1], hsv[2])
                else:
                    r, g, b = colorsys.hsv_to_rgb(hsv[0], (hsv[1] ** 2) * 0.8 + 0.2, max(hsv[2] ** 4 - 0.1, 0))

                colors.append(CorsairLedColor(led_id, int(r*255), int(g*255), int(b*255)))
                #print(r, g, b, end='\r')
            
        self.sdk.set_led_colors_buffer_by_device_index(index, colors)

    def flush_thread(self):
        while self.running:
            self.sdk.set_led_colors_flush_buffer()

    def log_thread(self):
        print("\nModule Loaded: Pixel Grid Canvas")
        while True:
            print(f" > Average FPS: {int(1 / self.frametime)} | Errors: {self.errors} | Size: {self.size} | Borders: ({self.horizontal_bars}, {self.vertical_bars})" + 20 * "", end='\r')
            sleep(1)
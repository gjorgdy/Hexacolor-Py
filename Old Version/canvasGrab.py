import imp
from cuesdk import CueSdk, CorsairEventId
from PIL import Image, ImageDraw, ImageGrab, ImageFilter
import colorsys
import threading
from mss import mss
from time import sleep, time
from utils import Utils as ut
from config import Config
import d3dshot
import numpy as np
from scipy import ndimage

class canvasGrab():
    
    def __init__(self, sdk, devices):
        self.running = True

        c = Config()
        self.split = c.getSplit()
        self.max_fps = c.getMaxFPS()
        self.sdk = sdk
        self.devices = devices
        self.frametime = 1/self.max_fps
        self.raw_frametime = 0
        self.monitor = {}
    
    def canvasInit(self):
        # Create Device canvas
        self.monitor = mss().monitors[1]
        for di in self.devices:
            device = self.devices[di]
            print(len(device['leds']))
            min_x = min([led[0] for led in device['leds'].values()])
            min_y = min([led[1] for led in device['leds'].values()])
            max_x = max([led[0] for led in device['leds'].values()])
            max_y = max([led[1] for led in device['leds'].values()])
            left = int((device['x'] + min_x * device['w']) * self.monitor['width'])
            top = int((device['y'] + min_y * device['h']) * self.monitor['height'])
            right = int(left + ((max_x - min_x) * device['w']) * self.monitor['width'] + 1)
            bottom = int(top + ((max_y - min_y) * device['h']) * self.monitor['height'] + 1)
            #canvas = {
            #    'left'  : int((device['x'] + min_x * device['w']) * self.monitor['width']),
            #    'top'   : int((device['y'] + min_y * device['h']) * self.monitor['height']),
            #    'width' : int(((max_x - min_x) * device['w']) * self.monitor['width'] + 1),
            #    'height': int(((max_y - min_y) * device['h']) * self.monitor['height'] + 1)
            #}
            canvas = (
                left, top, right, bottom
            )
            print(f"{di} : {canvas} ")
            for i in range(0, 2):
                thread = threading.Thread(target=self.canvasThread, args=(canvas, di, device['leds']))
                thread.start()
                sleep(self.frametime)
        
        thread = threading.Thread(target=self.backgroundThread, args=())
        thread.start()
    
    def canvasThread(self, canvas, di, leds):
        frametime = self.frametime
        max_frametime = 0
        d = d3dshot.create(capture_output="numpy")
        while True:
            start = time()

            #img = self.screenshot(canvas)
            #w, h = img.size
            #img = img.filter(ImageFilter.GaussianBlur(radius=5))
            
            img = d.screenshot(region=canvas)
            h, w = img.shape[0], img.shape[1] # canvas[2] - canvas[0], canvas[3] - canvas[1]#img.size
            #print(f"{di}, {img.shape} ")
            
            color_leds = {}
            for led in leds:
                x = min(leds[led][0], 1)
                y = min(leds[led][1], 1)
                px_x = max(0, x * w-1)
                px_y = max(0, y * h-1)
                color_leds[led] = ut.incrSat(img[int(px_y), int(px_x)])

            self.sdk.set_led_colors_buffer_by_device_index(di, color_leds)
            self.sdk.set_led_colors_flush_buffer()
            
            end = time()
            frametime = end-start#ut.constrain(end-start, 0, 1)
            self.raw_frametime = frametime
            
            sleep(frametime)
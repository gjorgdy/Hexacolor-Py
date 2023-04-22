import imp
from cuesdk import CueSdk, CorsairEventId
from PIL import Image, ImageDraw, ImageGrab, ImageFilter
import colorsys
import threading
from matplotlib.pyplot import sca
from mss import mss
from time import sleep, time
from utils import Utils as ut
from config import Config
import numpy as np
from numpy import array, mean, median, bincount

from cuesdk.structs import CorsairLedColor
import dxcam

class ScreenGrabAverage():
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
        self.frames = 0

    def thread(self, monitor):
        # Auto loop
        u = ut()
        u.setRunning(True)

        self.monitor = (monitor['left'], monitor['top'], monitor['left'] + monitor['width'], monitor['top'] + monitor['height'])#monitor
        print(self.monitor)
        camera = dxcam.create()

        test_length = 60
        start = time()
        for i in range(0, test_length):
            self.screenGrab(camera)
        end = time()
        print('\n')
        print(test_length/(end-start))

    def screenGrab(self, camera):
        while self.running:
            img = camera.grab()

            if img is None:
                continue

            h, w, px = img.shape
            
            step = 50

            xc, yc = 0, 0
            
            while xc < w/3:
                px = tuple(img[int(h/2), int(xc)])
                if px == (0, 0, 0): #img.getpixel((xc, h*0.6)) == (0, 0, 0):
                    xc += step
                else:
                    w = w - xc * 2
                    break
            while yc < h/3:
                px = tuple(img[int(yc), int(w/2)])
                if px == (0, 0, 0): #img.getpixel((xc, h*0.6)) == (0, 0, 0):
                    yc += step
                else:
                    h = h - yc * 2
                    break
            
            points_y = int(h/step)
            points_x = int(w/step)

            all_rgb = np.array([img[int(step * y), int(step * x)] for y in range(0, points_y) for x in range(0, points_x)])
            all_dta = np.array([(max(rgb)-min(rgb)) for rgb in all_rgb])
            std = all_dta.argsort()
            std_rgb = all_rgb[std]
            rgb = [int(mean(v)) for v in zip(*std_rgb[-int(len(std_rgb)/5):])]

            #try:
            #    rgb[0] = int(ut.constrain(rgb[0], last_rgb[0]-24, last_rgb[0]+24)) 
            #    rgb[1] = int(ut.constrain(rgb[1], last_rgb[1]-16, last_rgb[1]+16)) 
            #    rgb[2] = int(ut.constrain(rgb[2], last_rgb[2]-16, last_rgb[2]+16)) 
            #    last_rgb = rgb
            #except:
            #    last_rgb = rgb

            #scale = ut.constrain(254/(max(rgb)+1), 1, 2)
            #rgb = [int(v*scale) for v in rgb]
            
            rgb = ut.balanceRGB(rgb)

            #all_hsv = [ut.RGBtoHSV(rgb) for rgb in all_rgb]
            #hsv = tuple(zip(*all_hsv))
            #h = mean(hsv[0])#median(hsv[0])
            #s = mean(hsv[1])
            #v = mean(hsv[2])
            ##if 'av_s' in locals():
            #    #if abs(av_s - s) < 0.5:
            #    #    s = av_s
            #    #else: av_s = mean((av_s, s))
            #    #if abs(av_v - v) < 0.5:
            #    #    v = av_v
            #    #else: av_v = mean((av_v, v))
            #try:
            #    s = ut.constrain(s, av_s-0.01, av_s+0.01)
            #    av_s = mean((av_s, s))
            #    v = ut.constrain(v, av_v-0.01, av_v+0.01)
            #    av_v = mean((av_v, v))
            #except:
            #    av_s = s
            #    av_v = v
            #hsv = (h, s, v)
            #rgb = ut.HSVtoRGB(hsv)
            
            #rgb = [int(sum(v)/len(v)) for v in zip(*all_rgb)]

            for di in self.devices:
                device = self.devices[di]

                if di == 7:
                    rgb = tuple(int(v*0.75) for v in rgb)

                color_leds =  [CorsairLedColor(led, rgb[0], rgb[1], rgb[2]) for led in device['leds']] #{ led : rgb for led in device['leds'] }

                #print(list(device['leds'].keys()))

                    
                self.sdk.set_led_colors_buffer_by_device_index(di, color_leds)
            self.sdk.set_led_colors_flush_buffer()
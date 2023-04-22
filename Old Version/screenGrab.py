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

class ScreenGrab():
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

    def backgroundThread(self):
        self.frametime = ut.constrain((self.raw_frametime), (1/self.max_fps), (1))
        #print(f'Effect; Canvas Grab | {1/self.frametime}fps | {(self.raw_frametime*1000)}ms' + 25*' ', end='\r')
        sleep(1)

    def thread(self, monitor, canvas):
        # Auto loop
        u = ut()
        u.setRunning(True)

        self.monitor = (monitor['left'], monitor['top'], monitor['left'] + monitor['width'], monitor['top'] + monitor['height'])#monitor
        print(self.monitor)
        d = d3dshot.create(capture_output="numpy")
        
        #thread = threading.Thread(target=self.backgroundThread, args=())
        #thread.start()

        while self.running:
            if u.isRunning():
                self.screenGrab(d)
            else:
                sleep(1)

    def screenshot(self, monitor):
        # Capture entire screen
        with mss() as sct:
            sct_img = sct.grab(monitor)
            # Convert to PIL/Pillow Image
            return Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX')

    def screenGrab(self, d):
        #print('sg thread')
        start = time()

        img = d.screenshot()#region=self.monitor)

        h, w, px = img.shape 
        
        xc, yc = 0, 0
        
        while xc < w/3:
            px = tuple(img[int(h/2), int(xc)])
            if px == (0, 0, 0): #img.getpixel((xc, h*0.6)) == (0, 0, 0):
                xc += 1
            else:
                w = w - xc * 2
                break
        #while yc < h/2:
        #    px = tuple(img[int(yc), int(w/2)])
        #    if px == (0, 0, 0): #img.getpixel((xc, h*0.6)) == (0, 0, 0):
        #        yc += 1
        #    else:
        #        h = h - yc * 2
        #        break

        for di in self.devices:
            device = self.devices[di]

            #color_leds = {led: ut.incrSat( list(img[int(min(yc + min(device['y'] + device['leds'][led][1] * device['h'], 1) * h, h-1)), int(min(xc + min(device['x'] + device['leds'][led][0] * device['w'], 1) * w, w-1)) ])) for led in device['leds']}

            color_leds = {}
            for led in device['leds']:
                rad = 20
                ran = 5

                if di == 7:
                    rad = int(w/2.5)
                    ran = int(w/50)

                x = device['leds'][led][0]
                y = device['leds'][led][1]
                pc_x = min(device['x'] + x * device['w'], 1)
                pc_y = min(device['y'] + y * device['h'], 1)
                px_x = int(ut.constrain(xc + pc_x * w, rad, w-rad-1))
                px_y = int(ut.constrain(yc + pc_y * h, rad, h-rad-1))
                #px = img[px_y, px_x]
                
                step = ((ran-1)/2)
                all_rgb = (img[int(px_y-rad+y*(rad/step)), int(px_x-rad+x*(rad/step))] for y in range(0, ran) for x in range(0, ran))
                rgb = [int(sum(v)/len(v)) for v in zip(*all_rgb)]
                rgb = ut.balanceRGB(rgb)
                #r = [img[px_y, px_x-ran+i][0] for i in range(0, ran)]
                #g = [img[px_y, px_x-ran+i][1] for i in range(0, ran)]
                #b = [img[px_y, px_x-ran+i][2] for i in range(0, ran)]
                #rgb = (int(sum(r)/ran), int(sum(g)/ran), int(sum(b)/ran))

                color_leds[led] = rgb#ut.incrSat(rgb)
                
            self.sdk.set_led_colors_buffer_by_device_index(di, color_leds)
        self.sdk.set_led_colors_flush_buffer()
            #thread = threading.Thread(target=self.screenThread, args=(di, self.devices[di], img))
            #thread.start()

        end = time()

        print(1/(end-start), end='\r')
        #self.frametime = ut.constrain((end - start), (1/self.max_fps), (1))
        #self.raw_frametime = end-start
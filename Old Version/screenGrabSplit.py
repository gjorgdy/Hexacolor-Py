import imp
from cuesdk import CueSdk, CorsairEventId
from PIL import Image, ImageDraw, ImageGrab, ImageFilter
import colorsys
import threading
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
        self.crop_x = 0
        self.setMonitor()

    def thread(self, canvas):
        start = time()
        # Auto loop
        print("> Created threads")
        while self.running:
            if time() - start > 1:
                start = time()
                self.crop()
            self.screenGrab(0, canvas)
            #for i in range(0, self.split):
            #    t = threading.Thread(target=self.screenGrab, args=(i, canvas))
            #    t.start()

            sleep(self.frametime)

            self.sdk.set_led_colors_flush_buffer()
            print(f'Effect; Screen Grab | {1/self.frametime}fps' + 25*' ', end='\r')
            #break

    def crop(self):
        mon = {
                'left'  : 0, 
                'top'   : int(self.monitor['top'] / 2), 
                'width' : self.monitor['width'], 
                'height': 1
                }
        img = self.screenshot(mon, 0)
        var_x = 0
        while var_x < self.monitor['width']:
            if img.getpixel((var_x, 0)) == (0, 0, 0):
                var_x += 1
            else:
                if self.crop_x != var_x:
                    self.crop_x = var_x
                return

    def setMonitor(self):
        mon = mss().monitors[1]
        self.monitor = {
                'left'  : int(((mon['width']-(2*self.crop_x)) / self.split)), 
                'top'   : 0, 
                'width' : int(((mon['width']-(2*self.crop_x)) / self.split)), 
                'height': mon['height']
                }

    def screenshot(self, monitor, i):
        # Capture entire screen
        with mss() as sct:
            mon = {
                'left'  : monitor['left'] * i, 
                'top'   : monitor['top'], 
                'width' : monitor['width'], 
                'height': monitor['height']
                }
            sct_img = sct.grab(mon)
            # Convert to PIL/Pillow Image
            return Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX')

    def screenGrab(self, i, canvas):
        #print('sg thread')
        start = time()
        #{'left': 0, 'top': 144*9, 'width': 3440, 'height': 144}

        # take screenshot of single split of monitor 
        img = self.screenshot(self.monitor, i)

        #print(f'{monitor["width"]}, {mon}, {split}, {i}')

        # resize to single split
        img = img.resize((int(canvas[0] / self.split), int(canvas[1])))
        img = img.filter(ImageFilter.GaussianBlur(radius=5))
        #img.show()
        w, h = img.size
        min_w = (w *  i   ) # left X-coord of slice
        max_w = (w * (i+1)) # right X-coord of slice

        for di in self.devices:
            device = self.devices[di]
            color_leds = {}
            for x in device['leds']:
                if min_w <= x <= max_w:
                    for y in device['leds'][x]:
                        px_x = int(ut.constrain(device['corner_x'] - min_w + x, 0, w - 10))
                        px_y = int(ut.constrain(device['corner_y'] + y, 0, h - 10))
                        px = img.getpixel((px_x, px_y))
                        #print(px)
                        color_leds[device['leds'][x][y]] = px
                        #print(f'{w}, {h}')
                        #print(f'{x}, {y}')
            self.sdk.set_led_colors_buffer_by_device_index(di, color_leds)
            #thread = threading.Thread(target=self.screenThread, args=(i, di, self.devices[di], img))
            #thread.start()
        end = time()

        #print(1/(end-start))
        self.frametime = end-start#ut.constrain((end - start), (1/self.max_fps), (1))

    def screenThread(self, i, di, device, img):
        w, h = img.size
        min_w = (w *  i   ) # left X-coord of slice
        max_w = (w * (i+1)) # right X-coord of slice
        color_leds = {}
        for x in device['leds']:
            if min_w <= x <= max_w:
                for y in device['leds'][x]:
                    px_x = int(ut.constrain(device['corner_x'] - min_w + x, 0, w - 10))
                    px_y = int(ut.constrain(device['corner_y'] + y, 0, h - 10))
                    px = img.getpixel((px_x, px_y))
                    #print(px)
                    color_leds[device['leds'][x][y]] = px
                    #print(f'{w}, {h}')
                    #print(f'{x}, {y}')
        self.sdk.set_led_colors_buffer_by_device_index(di, color_leds)

    #def screenThreadOld(self, x_mul, y_mul, i, device_index , device, img):
    #    color_leds = {}
    #    for x in device['leds']:
    #        if x < int(max_x / split):
    #            for y in device['leds'][x]:
    #                px_x = int(constrain(device['corner_x'] + x, 0, max_x - 10))# - int((max_x / split) * i) + 1)
    #                px_y = constrain(device['corner_y'] + y, 0, max_y - 10)
    #                px = img.getpixel((x_mul * px_x, y_mul * px_y))
    #                print(px)
    #                color_leds[device['leds'][x][y]] = px
    #    sdk.set_led_colors_buffer_by_device_index(device_index, color_leds)

import imghdr
import threading
from cuesdk import CueSdk, CorsairEventId
from matplotlib.pyplot import sca
from mss import mss
from time import sleep, time
from config import Config
import numpy
from numpy import array, mean, median, bincount
import dxcam

from cuesdk.structs import CorsairLedColor
from numba import jit, njit, vectorize

class averageAmbilight():

    def __init__(self, sdk:CueSdk, canvas):
        self.sdk = sdk
        self.canvas = canvas

        self.frametime = 1
        self.errors = 0
        self.colors = []

        self.running = True

        #self.color_thread()
        #return
        self.color()
        #flush = threading.Thread(target=self.flush_thread)
        #flush.start()
        take_control = threading.Thread(target=self.control_thread)
        take_control.start()

        self.log_thread()

    def color(self):

        color = (0, 0, 0)


        monitor = mss().monitors[0]
        width = 3420
        height = 1420
        half_width = 1710
        half_height = 710

        quadrants = [
            (0, 0, half_width, half_height),
            (half_width, 0, width, half_height),
            (0, half_height, half_width, height),
            (half_width, half_height, width, height)
        ]
        halves = [
            (0, 0, half_width, height),
            (half_width, 0, width, height)
        ]
        print(quadrants)
        
        camera = dxcam.create()

        #for region in halves:
        threading.Thread(target=self.color_thread, args=(camera, )).start()

    def color_thread(self, camera):

        while self.running:
            start = time()

            img = camera.grab()

            if img is None:
                continue

            color = calculate_color(img)
            
            if color == None:
                self.errors += 1
                continue
            
            self.combine(color)
        
            self.frametime = (time() - start)

    def combine(self, color):

        if len(self.colors) < 2:
            self.colors.append(color)
        else:
            r = [pixel[0] for pixel in self.colors]
            g = [pixel[1] for pixel in self.colors]
            b = [pixel[2] for pixel in self.colors]

            r = int(numpy.average(r))
            g = int(numpy.average(g))
            b = int(numpy.average(b))

            self.colors = []

            for device in self.canvas['leds']:
                self.sdk.set_led_colors_buffer_by_device_index(device, [CorsairLedColor(led[0], r, g, b) for led in self.canvas['leds'][device]])
            
            self.sdk.set_led_colors_flush_buffer()


    def control_thread(self):
        while self.running:
            self.sdk.request_control()
            sleep(10)

    def flush_thread(self):
        while self.running:
            self.sdk.set_led_colors_flush_buffer()

    def log_thread(self):
        print("\nLoaded Average Ambilight module")
        while True:
            print(f" > Average FPS: {int(1 / self.frametime)} | Errors: {self.errors}" + 20 * "", end='\r')
            sleep(1)

#@jit()
def img_to_array(img):
    lines_y = img[0 : img.shape[0] : 100]
    lines_x = array([line[0 : img.shape[1] : 100] for line in lines_y])
    
    return numpy.concatenate(lines_x)


def calculate_color(img) -> tuple:
    
    pixels = img_to_array(img)

    black = (0, 0, 0)
    nb_pixels = numpy.delete(pixels, numpy.where(black == pixels), axis=0)

    pixels_weights = [(numpy.max(pixel) - numpy.min(pixel)) for pixel in nb_pixels]
    order = numpy.argsort(pixels_weights)
    pixels_sorted = pixels[numpy.flip(order)]
    
    r = [pixel[0] for pixel in pixels_sorted[0:100]]
    g = [pixel[1] for pixel in pixels_sorted[0:100]]
    b = [pixel[2] for pixel in pixels_sorted[0:100]]

    return average_pixels(r, g, b)

#@njit()
def average_pixels(r, g, b):
    try:

        if len(r) > 0:
            r = int(numpy.average(r))
            g = int(numpy.average(g))
            b = int(numpy.average(b))
        else:
            r = 0
            g = 0
            b = 0

        #dif_vib = 255 / (numpy.max((r, g, b)) - numpy.min((r, g, b)))
        #stand_vib = 255 / numpy.max((r, g, b))
        vib = 1 #numpy.min((dif_vib, stand_vib))
        
        return (int(vib * r), int(vib * g), int(vib * b))

    except:
        #print('error getting mean values\n')
        return (0, 0, 0)
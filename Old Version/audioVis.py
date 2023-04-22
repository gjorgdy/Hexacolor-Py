from cuesdk import CueSdk, CorsairEventId
from matplotlib.pyplot import sca
from mss import mss
from time import sleep, time
from utils import Utils as ut
from config import Config
import numpy as np
from numpy import array, mean, median, bincount
import audioop

CHUNK = 4048

class audioVis():

    def __init__(self, sdk, devices):
        pa = pyaudio.PyAudio()
        self.stream = pa.open(
            format=pyaudio.paInt16, 
            channels=1, 
            rate=44100, 
            input=True,
            frames_per_buffer=CHUNK
            )
        self.stream.start_stream()
        self.sdk = sdk
        self.devices = devices

    def listener(self):
        max_v = 0
        while True:
            data = self.stream.read(CHUNK)
            rms = audioop.rms(data, 2)
            val = min(rms/8000, 1)
            #data = np.fromstring(self.stream.read(CHUNK),dtype=np.int16)
            #av = (data.mean() + 1) / 2

            rgb = [0, int(val*192), int(val*192)]
            print(rms, end='\r')

            for di in self.devices:
                device = self.devices[di]

                color_leds = { led : rgb for led in device['leds'] }
                    
                self.sdk.set_led_colors_buffer_by_device_index(di, color_leds)
            self.sdk.set_led_colors_flush_buffer()
        
        self.stream.stop_stream()
        self.stream.close()

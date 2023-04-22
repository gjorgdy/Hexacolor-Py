from random import random, randint
from time import sleep
from utils import Utils

class Load():

    def LoadAnimation(sdk, devices, length):
        ut = Utils()
        ut.setRunning(False)

        amount_of_leds = 0        
        for device in devices.values():
            amount_of_leds += len(device['leds'])
        print(amount_of_leds)

        fully_colored_leds = []
        color_leds = {}
        while amount_of_leds > len(fully_colored_leds):
        #for i in range(0, length):
            #print(len(colored_leds))
            for di in devices:
                device = devices[di]

                for led in device['leds']:

                    if led not in color_leds.keys():
                        color_leds[led] = ( 0, 0, 0 )

                    if color_leds[led] == (255, 255, 255):
                        fully_colored_leds.append(led)
                    elif randint(0, 10) == 0:
                        r, g, b = color_leds[led]
                        color_leds[led] = ( min(r+randint(0,5), 255), min(g+randint(0,5), 255), min(b+randint(0,5), 255) )
                    
                sdk.set_led_colors_buffer_by_device_index(di, color_leds)
            sleep(0.05)
            sdk.set_led_colors_flush_buffer()

        for i in range(0, length):
            for di in devices:
                device = devices[di]

                color_leds = {}
                for led in device['leds']:
                    color_leds[led] = (255, 255, 255)
                    
                sdk.set_led_colors_buffer_by_device_index(di, color_leds)
            sleep(1)
            sdk.set_led_colors_flush_buffer()
        
        ut.setRunning(True)
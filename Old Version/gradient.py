from utils import Utils as u
from main import Main

class Gradient():
    def gradient(min_h, max_h):
        for device_index in devices:
            device = devices[device_index]
            color_leds = {}
            for x in device['leds']:
                for y in device['leds'][x]:
                    xc = (device['corner_x'] + x)/max_x
                    yc = (device['corner_y'] + y)/max_y

                    varS = (min_h + (max_h - min_h) * xc)
                    
                    color_leds[device['leds'][x][y]] = u.HSVtoRGB(u.constrain(varS, 0, 1), 1.0, 1.0)

            sdk.set_led_colors_buffer_by_device_index(device_index, color_leds)
        
        sdk.set_led_colors_flush_buffer()
        print('Effect; Gradient', end='\r')
import json
import math

from mss import mss
from PIL import Image, ImageDraw, ImageGrab

import statistics


class Canvas():

    def __init__(self, config, width, height):
        self.width = width
        self.height = height
        self.devices = {}

    def add_device(self, device_index, device_config, device_leds):
        if device_leds == 0:
            return

    # Device canvas
        left = int((device_config['left'] / 100) * self.width)
        top = int((device_config['top'] / 100) * self.height)
        width = int((device_config['width'] / 100) * self.width)
        height = int((device_config['height'] / 100) * self.height)

    # Construct leds dict
        leds = []
        for led_id in device_leds:
            _x = int(device_leds[led_id][0])
            _y = int(device_leds[led_id][1])
        # Enter into dict
            leds.append( (led_id, ( _x, _y )) )
            
    # Sort leds by x coordinate
        leds = sorted( leds, key= lambda x:(x[1][0], x[1][1]) )

    # List of all coordinate tuples
                # index, pos, x
        all_x = [led[1][0] for led in leds]
        all_x = list(dict.fromkeys(all_x))
        all_x.sort()
        min_x = min(all_x)
        max_x = max(all_x)
        if len(all_x) > 1:
            diff_x = [ all_x[i] - all_x[i-1] for i in range(1, len(all_x)) ]
            median_diff_x = statistics.median(diff_x)
            scale_x = (max_x - min_x) / width
        else:
            median_diff_x = max_x
            scale_x = max_x / width
        
                # index, pos, y
        all_y = [led[1][1] for led in leds]
        all_y = list(dict.fromkeys(all_y))
        all_y.sort()
        min_y = min(all_y)
        max_y = max(all_y)
        if len(all_y) > 1:
            diff_y = [ all_y[i] - all_y[i-1] for i in range(1, len(all_y)) ]
            median_diff_y = statistics.median(diff_y)
            scale_y = (max_y - min_y) / height
        else:
            median_diff_y = max_y
            scale_y = max_y / height

    # Modulo space all coordinates to the median difference
        #border = max(median_diff_x, median_diff_y)
        if len(all_x) == 1 and len(all_y) == 1:
            dleds = { height : {width : leds[0][0]} }
        else:
            dleds = {}
        for i in range(1, len(leds)):

            _id, (_x, _y) = leds[i]
            _ix, _iy = all_x.index(_x), all_y.index(_y)
            p_x, p_y = all_x[_ix-1], all_y[_iy-1]

            try:
                _dx = _x - p_x
                _fx = _dx % median_diff_x
                _nx = min(int((_x - min_x - _fx + median_diff_x) / scale_x + left), self.width)
            except:
                _nx = self.width;

            try:
                _dy = _y - p_y
                _fy = _dy % median_diff_y
                _ny = min(int((_y - min_y - _fy + median_diff_y) / scale_y + top), self.height)
            except:
                _ny = self.height;

            if _ny in list(dleds.keys()):
                dleds[_ny][_nx] = _id
            else:
                dleds[_ny] = { _nx : _id }
        
        dleds = dict(sorted(dleds.items(), key=lambda x:x[0]))

    # Create canvas map
        p_x = left
        p_y = top
        led_map = []
        for _y, _xs in dleds.items():
            #if len(_xs) > 2:
            #    p_x = left
            for _x, _id in _xs.items():
                led_map.append( (_id, (p_x, p_y), (_x, _y) ) )
                if len(_xs) > 2:
                    p_x = _x
            if len(_xs) > 2:
                p_y = _y
        
        self.devices[device_index] = led_map

        return

    # Create Debug image
        img_obj = Image.new("RGB", (self.width * 10 + 2, self.height * 10 + 2))
        img = ImageDraw.Draw(img_obj)
        
        g = 0
        b = 0
        if len(led_map) > 0:
            s = int(255 / len(led_map))
        else:
            s = 255

        for _id, (p_x, p_y), (_x, _y) in led_map:
            img.rectangle( ((_x * 10, _y * 10), (p_x * 10, p_y * 10)), fill=None, outline=(0, 255, b), width=2 )
            print( (p_x, p_y), (_x, _y) )
            b += s

        img_obj.show()
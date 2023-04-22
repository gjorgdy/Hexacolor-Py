import json
from mss import mss

class Canvas():

    def __init__(self, config):
        canvas_settings = config.get_canvas()
        
        monitor = mss().monitors[canvas_settings['monitor']]

        self.canvas = {
            'width' : int(monitor['width'] / 100 * 100 - 1),
            'height' : int(monitor['height'] / 100 * 100 - 1),
            'leds' : {}
        }

    def add_device(self, device_index, device_config, device_leds):
        # Device canvas
        left_offset = int((device_config['left'] / 100) * self.canvas['width'])
        top_offset = int((device_config['top'] / 100) * self.canvas['height'])
        width = int((device_config['width'] / 100) * self.canvas['width'])
        height = int((device_config['height'] / 100) * self.canvas['height'])
        #print(f"Canvas;        {self.canvas}")
        #print(f"Device canvas; {left_offset}, {top_offset}, {width}, {height}")
        # Led canvas
        all_led_x_coords = [device_leds[led_id][0] for led_id in device_leds]
        nondup_led_x_coords = list(dict.fromkeys(all_led_x_coords))
        all_led_y_coords = [device_leds[led_id][1] for led_id in device_leds]
        nondup_led_y_coords = list(dict.fromkeys(all_led_x_coords))
        top_left_corner = (min(all_led_x_coords), min(all_led_y_coords))
        bottom_right_corner = (max(all_led_x_coords), max(all_led_y_coords))
        # Coords
        sorted_coords_x = list.sort(nondup_led_x_coords)
        sorted_coords_y = list.sort(nondup_led_y_coords)
        #steps_x = [(sorted_coords_x[index + 1] - sorted_coords_x[index]) for index in range(len(sorted_coords_x) - 1)]
        #steps_y = [(sorted_coords_y[index + 1] - sorted_coords_y[index]) for index in range(len(sorted_coords_y) - 1)]
        #avg_step_X = int(sum(steps_x) / len(steps_x))
        #avg_step_y = int(sum(steps_y) / len(steps_y))
        # 
        min_x, max_x = min(all_led_x_coords), max(all_led_x_coords)
        min_y, max_y = min(all_led_y_coords), max(all_led_y_coords)
        # Led ratio
        led_width_ratio = (max_x - min_x)
        if led_width_ratio == 0:
            led_width_ratio = 1
        led_height_ratio = (max_y - min_y)
        if led_height_ratio == 0:
            led_height_ratio = 1
        # Calculate final led coordinates
        self.canvas['leds'][device_index] = []
        for led_id in device_leds:
            led_coords = device_leds[led_id]
            formatted_led_coords = (
                int(((led_coords[0] - min_x) / led_width_ratio) * width + left_offset),
                int(((led_coords[1] - min_y ) / led_height_ratio) * height + top_offset)
            )
            self.canvas['leds'][device_index].append( (led_id, formatted_led_coords) )

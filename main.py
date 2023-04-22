from ast import main
from time import sleep, time
from cuesdk import CueSdk, CorsairEventId
from PIL import Image, ImageDraw, ImageGrab
from mss import mss
import json
from canvas import Canvas
from grid_canvas import Canvas as gCanvas
from config import Config
import threading
from cuesdk.structs import CorsairLedColor
from random import randint

from averageAmbilight import averageAmbilight
from pixelsAmbilight import PixelsAmbilight
from grid_pixelsAmbilight import PixelsAmbilight as gPixelsAmbilight

class Main():

    def __init__(self, start_cli=True):
        self.start_cli = start_cli

        self.sdk = CueSdk()
        self.sdk.connect()
        self.devices = {}

        self.main()

    def sdk_event_handler(self, event_id, data):
        #print("Event: %s" % event_id)
        if (event_id == CorsairEventId.KeyEvent):
            print(" Device id: %s\n    Key id: %s\n Key state: %s" %
                (data.deviceId.decode(), data.keyId,
                "pressed" if data.isPressed else "released"))
        elif (event_id == CorsairEventId.DeviceConnectionStatusChangedEvent):
            data.deviceId.decode()
            if data.isConnected:
                print('Connection made epicly')
                #Load.LoadAnimation(self.sdk, self

    def main(self):
        # Subscribe to SDK events
        subscribed = self.sdk.subscribe_for_events(self.sdk_event_handler)
        if not subscribed:
            err = self.sdk.get_last_error()
            print("Subscribe for events error: %s" % err)
            return

        # load config
        config = Config()
        
        # load canvas
        self.canvas = gCanvas(config, 16, 16)
        
        device_count = self.sdk.get_device_count()
        for i in range(device_count):
            #if self.sdk.get_device_info(i).model in ( "K60 RGB PRO"):
            device_id = self.sdk.get_device_info(i).id
            config.register_device(self.sdk, i)
            device_config = config.get_device(device_id)
            leds = self.sdk.get_led_positions_by_device_index(i)

            config.register_device(self.sdk, i)
            self.canvas.add_device(i, device_config ,leds)

            print(f'Calculated canvas for {i} : {self.sdk.get_device_info(i).model}')


        print(self.sdk.protocol_details)

        #program_thread = threading.Thread(target=self.cli())
        #program_thread.start()

        # Initiate leds
        self.sdk.request_control()
        start = time()
        for index, leds in self.canvas.devices.items():
            self.sdk.set_led_colors_buffer_by_device_index(index, [CorsairLedColor(led[0], 0, 0, 0) for led in leds])
        self.sdk.set_led_colors_flush_buffer()

        load_time = time() - start
        print(f"Time to load: {load_time}s")
        print(f"Which would equate to {1/(load_time + 0.0001)} fps")

        print(f"Loaded {device_count} devices")
        led_count = sum([device['led_count'] for device in config.config['devices'].values()])
        print(f" with a total of {led_count} controllable LEDs")

        #self.printImage(self.canvas)


        pixel_mode = gPixelsAmbilight(self.sdk, self.canvas)
        print("Select; \n 0-Print Canvas \n 1-Pixels \n 2-Average Screen Grab \n q-quit")
        effect = input('>> ')
        
        if effect == '0':
            self.printImage(self.canvas)

        elif effect == '1':
            ################################################################
            pixel_mode = gPixelsAmbilight(self.sdk, self.canvas)
#
        #elif effect == '2':
        #    ################################################################
        #    average_mode = averageAmbilight(self.sdk, canvas.canvas)
        else:
            print("Invalid selection")

        #if self.start_cli:
        #    self.cli()
    
    def printImage(self, canvas : gCanvas):
        img_obj = Image.new("RGB", (canvas.width * 10 + 2, canvas.height * 10 + 2))
        img = ImageDraw.Draw(img_obj)
        
        for led_map in canvas.devices.values():
            b = 0
            if len(led_map) > 0:
                s = int(255 / len(led_map))
            else:
                s = 255

            for _id, (p_x, p_y), (_x, _y) in led_map:
                img.rectangle( ((_x * 10, _y * 10), (p_x * 10, p_y * 10)), fill=None, outline=(0, 255, b), width=2 )
                #print( (p_x, p_y), (_x, _y) )
                b += s

        img_obj.show()

    def cli(self):
        print("\n-= Started CLI Hexacolor =- use '?' for help") 
        while True:
            command = input('\n> ')

            if command == '?':
                print(
                    "\nCommands:",
                    "\n ? - open this help menu",
                    "\n print - print the canvas",
                    "\n modes - list available modes",
                    "\n mode {id} - set the current mode",
                    "\n r - reload the program",
                    "\n q - quit the program",
                    ""
                )
            elif command == 'print':
                self.printImage(self.canvas)
            elif command == 'r':
                Main(False)
            elif command == 'q':
                self.sdk.release_control()
                exit()
                return
            else:
                print("Invalid command")

# Start program
Main()
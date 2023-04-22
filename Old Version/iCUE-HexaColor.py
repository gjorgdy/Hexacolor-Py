from cuesdk import CueSdk, CorsairEventId
from PIL import Image, ImageDraw, ImageGrab
from mss import mss
from screenGrab import ScreenGrab
from screenGrabAverage import ScreenGrabAverage
from utils import Utils
from config import Config
#import d3dshot
from load import Load
from audioVis import audioVis

class Main():

    def __init__(self):
        self.sdk = CueSdk()
        self.sdk.connect()
        self.devices = {}

        self.main()

    def sdk_event_handler(self, event_id, data):
        print("Event: %s" % event_id)
        if (event_id == CorsairEventId.KeyEvent):
            print(" Device id: %s\n    Key id: %s\n Key state: %s" %
                (data.deviceId.decode(), data.keyId,
                "pressed" if data.isPressed else "released"))
        elif (event_id == CorsairEventId.DeviceConnectionStatusChangedEvent):
            data.deviceId.decode()
            if data.isConnected:
                print('Connection made epicly')
                #Load.LoadAnimation(self.sdk, self.devices, 5)
        #else:
        #    print("Invalid event!")

    ################################

    def printImage(self, monitor, devices):
        c = Config()
        
        mon = (monitor['width'], monitor['height'])
        img_obj = Image.new("RGB", mon)
        img = ImageDraw.Draw(img_obj)
        w, h = mon

        for di in devices:
            c1x = devices[di]['x'] * w
            c1y = devices[di]['y'] * h
            c2x = (devices[di]['x'] + devices[di]['w']) * w
            c2y = (devices[di]['y'] + devices[di]['h']) * h
            img.rectangle([(c1x, c1y), (c2x, c2y)], outline=c.getColor(di))
            if di == 0:
                print(f'{di} : {c1x}, {c2x} ')
            for led in devices[di]['leds'].values():
                c1x = (devices[di]['x'] + (led[0] * devices[di]['w']) )* w
                c1y = (devices[di]['y'] + (led[1] * devices[di]['h']) )* h
                img.ellipse((c1x, c1y, c1x+10, c1y+10), fill=c.getColor(di))

        img_obj.show()

    def getDevice(self, device_index):
        c = Config()
        if not c.isEnabled(device_index):
            return None

        leds = self.sdk.get_led_positions_by_device_index(device_index)
        if len(leds) == 0:
            return {
                'x' : 0,
                'y' : 0,
                'w' : 0,
                'h' : 0,
                'leds'   : {}
            }
        
        #print(f'| {device_index} : {self.sdk.get_device_info(device_index)}')
        #print(leds)
        leds_x = {led:int(leds[led][0]/5) for led in leds}
        leds_y = {led:int(leds[led][1]/5) for led in leds}
        led_index = list(leds.keys())

        min_x = min(leds_x.values())
        min_y = min(leds_y.values())
        max_x = max(leds_x.values())
        max_y = max(leds_y.values())
        if min_x == 0:
            min_x = -1
        if min_y == 0:
            min_y = -1
        if max_x == 0:
            max_x = 1
        if max_y == 0:
            max_y = 1
        #print(f"| {min_x}, {min_y}, {max_x}, {max_y} " )

        #led_positions = {((x-min_x/2)/max_x) : {((leds_y[led_index]-min_y/2)/max_y) : led_index for led_index in leds_y if leds_x[led_index] == x} for x in leds_x.values()}
        leds = {led:((leds_x[led]-min_x/2)/max_x, (leds_y[led]-min_y/2)/max_y ) for led in leds_x}

        if c.inDivide(device_index):
            for led in leds_x:
                x = leds[led][0]
                y = leds[led][1]
                leds[led] = (y, x)

        return {
            'index': device_index,
            'x'    : c.getPosition(device_index)[0],
            'y'    : c.getPosition(device_index)[1],
            'w'    : c.getPosition(device_index)[2],
            'h'    : c.getPosition(device_index)[3],
            'leds' : leds
        }

    def main(self):
        c = Config()
        print(self.sdk.protocol_details)

        device_count = self.sdk.get_device_count()

        leds = self.sdk.get_led_positions_by_device_index(0)
        #print('')
        #print(list(leds.keys())[11])
        #print(list(leds.values())[11])
        #print('')
        for device_index in range(device_count):
            device = self.getDevice(device_index)
            if device != None:
                self.devices[device_index] = device
                print(f'| {device_index} : {self.sdk.get_device_info(device_index)} | {c.getColor(device_index)}')
            else:
                print(f'| {device_index} : {self.sdk.get_device_info(device_index)} | Disabled')

        subscribed = self.sdk.subscribe_for_events(self.sdk_event_handler)
        if not subscribed:
            err = self.sdk.get_last_error()
            print("Subscribe for events error: %s" % err)

        print("Select; \n 0-Print Canvas \n 1-Screen Grab \n 2-Average Screen Grab \n 3-Audio Visualizer \n q-quit")
        effect = input('>> ')
        
        monitor = mss().monitors[1]
        if effect == '0':
            self.printImage(monitor, self.devices)

        elif effect == '1':
            sg = ScreenGrab(self.sdk, self.devices)
            print("> Starting ScreenGrab Thread")
            #monitor['top'] = int(monitor['height'] *0.4)
            #monitor['height'] = int(monitor['height'] * 0.2)
            sg.thread(monitor, ())

        elif effect == '2':
            sga = ScreenGrabAverage(self.sdk, self.devices)
            #monitor['top'] = int(monitor['height'] *0.4)
            #monitor['height'] = int(monitor['height'] * 0.2)
            sga.thread(monitor)

        elif effect == '3':
            vis = audioVis(self.sdk, self.devices)
            vis.listener()
            #Load.LoadAnimation(self.sdk, self.devices, 15)
        
        else:
            print("Invalid selection")


Main()
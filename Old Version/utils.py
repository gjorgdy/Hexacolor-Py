from cmath import sqrt
from numpy import mean
import colorsys

class Utils():

    def __init__(self):
        self.running = False

    def constrain(val, min_val, max_val):
        return min(max_val, max(min_val, val))

    def HSVtoRGB(hsv):
        return [int(i*255) for i in colorsys.hsv_to_rgb(hsv[0], hsv[1], hsv[2])]
    
    def RGBtoHSV(rgb):
        return [i for i in colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)]

    def incrSat(rgb):
        #print(f"in  {r}, {g}, {b}")
        r, g, b = rgb
        hsv = Utils.RGBtoHSV(r, g, b)
        if hsv[1] >= 0.15:
            s = int(hsv[1]**0.5)
        else:
            s = hsv[1]
        v = hsv[2]
        #if hsv[1] > 0.5:
        #    s = Utils.constrain(hsv[1] * 2, 0, 1)
        #else:
        #    s = hsv[1]
        #if hsv[2] > 0.75:
        #    v = 1#hsv[2] * 0.25
        #elif hsv[2] < 0.05:
        #    v = 0
        #else:
        #    v = hsv[2]
        rgb = Utils.HSVtoRGB(hsv[0], s, v)
        #print(f"hsv {hsv}")
        #print(f"dif {rgb[0] - r}, {rgb[1] - g}, {rgb[2] - b}", end='\r')
        return rgb

    def setRunning(self, bool):
        self.running = bool
        return bool

    def isRunning(self):
        return self.running

    def balanceRGB(rgb):
        rgb[1] = int(rgb[1]/1.5)
        rgb[2] = int(rgb[2]/2)
        return rgb
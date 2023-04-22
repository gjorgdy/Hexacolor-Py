
class Config():

    def __init__(self):
        self.color = {
            0 : "red",
            1 : "orange",
            2 : "yellow",
            3 : "green",
            4 : "blue",
            5 : "purple",
            6 : "pink",
            7 : "cyan"
        }
        self.positions = {
        #index   x       y      w       h
            0 : (0.13  , 0.5  , 0.5   , 0.375 ), # Fans
            1 : (0.85  , 0.1  , 0.05  , 0.8   ), # 
            2 : (0.90  , 0.1  , 0.05  , 0.8   ), # Ram 1
            3 : (0     , 0    , 0     , 0     ), # Ram 2
            4 : (0.77  , 0.75 , 0.1   , 0.1   ), # Keyboard
            5 : (0.95  , 0.1  , 0.05  , 0.8   ), # Headset /disabled
            6 : (0     , 0    , 0     , 0     ), # Mouse
            7 : (0     , 0    , 1     , 1     )  # Led Strip
        }
        self.divide = {
            5 : 8
        }
        self.enabled = {
            0 : True,
            1 : True,
            2 : True,
            3 : True,
            4 : True,
            5 : True,
            6 : True,
            7 : True
        }
        self.max_fps = 30
        self.split = 1

    def getColor(self, i):
        return self.color[i]

    def getPosition(self, i):
        return self.positions[i]
        
    def getDivide(self, i):
        return self.divide[i]

    def inDivide(self, i):
        if i in self.divide.keys():
            return True
        else:
            return False

    def isEnabled(self, i):
        return self.enabled[i]

    def getMaxFPS(self):
        return self.max_fps

    def getSplit(self):
        return self.split
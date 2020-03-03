############################################
#### Evelyn - the Ultimate Puzzle Game ##### 
####### create/draw/update Buttons #########
############################################
# cuz tkinter buttons are weird
from tkinter import *

class FakeButton(object):
    def __init__(self, cx, cy, width, height, text, function, mode, level = None, 
                 outline=None, bg=None):
        (self.cx, self.cy) = (cx, cy)
        (self.width, self.height) = (width, height)
        self.x0 = self.cx - self.width//2
        self.y0 = self.cy - self.height//2
        self.x1 = self.cx + self.width//2
        self.y1 = self.cy + self.height//2
        self.text = text
        self.level = level
        self.command = function
        self.mode = mode
        self.state = "outside"
        if outline == None and bg == None:
            self.bg = '#EAF0F1'
            self.outline = '#4a69bd'
        else:
            self.bg = bg
            self.outline = outline
        self.size = " 23"
        self.font = "Times"

    def handleClick(self, event): 
        if (self.inBounds(event.x, event.y)):
            if self.level == None:
                self.command()
            else:
                self.command(self)

    def update(self, event): 
        #change bg color if the mouse is in a button but hasn't clicked
        self.state = "outside"
        if (self.inBounds(event.x,event.y)):
            self.state = "inside"

    def inBounds(self, x, y): 
        #Check if the mouse is within the button
        if (x < self.x0 or x > self.x1 or y < self.y0 or y > self.y1):
            return False
        return True

    def draw(self, canvas, data):
        if (self.state == "inside"): 
            canvas.create_rectangle(self.x0, self.y0, self.x1, self.y1, 
                                    fill=self.outline, outline=self.outline, width = 3)
        else: 
            canvas.create_rectangle(self.x0, self.y0, self.x1, self.y1, 
                                    fill=self.bg, outline=self.outline, width = 3)
        canvas.create_text(self.cx, self.cy, text = self.text, font = self.font+self.size)
############################################
#### Evelyn - the Ultimate Puzzle Game ##### 
#########   Dots for the beats   ###########
############################################
# modified from Devansh Kukreja TP - Pulse 
# https://github.com/devanshk/Pulse

import random
import math

class Dot(object): 
    def __init__(self, x, y, data, velx = None, vely = None, velr = None, r = None, curvy=True):
        (self.x, self.y) = (x,y)
        self.r = r
        self.fill = random.choice(data.colors)
        self.timer = 0
        self.velx = velx
        self.vely = vely
        self.velr = velr
        self.curvy = curvy

        if (self.velr == None):
            self.velr = -0.5
        if (self.velx == None):
            negnum = random.random()-0.5
            self.velx = random.random()*2 * abs(negnum)/negnum
        if (self.vely == None):
            negnum = random.random()-0.5
            self.vely = random.random()*2 * abs(negnum)/negnum
        if (self.r == None):
            self.r = random.randint(10,20)

    def draw(self, canvas): #Draw the dot
        x0 = self.x-self.r
        y0 = self.y-self.r
        x1 = self.x+self.r
        y1 = self.y+self.r
        if self.curvy:
            canvas.create_oval(x0, y0, x1, y1, fill=self.fill, width=2, 
                               outline = 'goldenrod')
        else:
            canvas.create_oval(x0, y0, x1, y1, fill=self.fill, width=0)
                        
    def update(self, data): 
        #Update the dot based on all its variables and the time speed
        self.timer += 1 * data.timescale
        if (self.curvy):
            self.x += self.velx * data.timescale * math.sin(self.timer/10)
            self.y += self.vely * data.timescale * math.sin(self.timer/10)
        else:
            self.x += self.velx * data.timescale
            self.y += self.vely * data.timescale
        self.r += self.velr * data.timescale
        if (self.r < 0): 
            #If the dot disappeared, remove it
            data.dots.remove(self)
        elif ((self.x < self.r or self.x > data.width+self.r) and (self.y < self.r or self.y > data.height+self.r)): 
            #If the dot went off-screen, remove it
            data.dots.remove(self)


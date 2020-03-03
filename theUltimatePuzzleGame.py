############################################
#### Evelyn - the Ultimate Puzzle Game ##### 
########## Game Modes / Main File ##########
############################################
# video: https://www.youtube.com/watch?v=oF4RBVQNbuw&feature=youtu.be
from tkinter import *
from PIL import Image
import os
import random
import pyaudio
import spotipy
import csv
import wave
import math
import time
from pydub import AudioSegment
from matplotlib import pyplot as plt
import matplotlib as mpl
import numpy as np
from FakeButton import FakeButton
from saveProgress import Progress
from spotifyinfo import SpotifyInfo

# https://github.com/devanshk/Pulse
# modified from Devansh Kukreja Term Project - Pulse
from beatDetection import SimpleBeatDetection
# modified from Devansh Kukreja Term Project - Pulse
from Dot import Dot
# copied from Devansh Kukreja Term Project - Pulse
from grapher import Graph
# copied from http://www.cs.cmu.edu/~112/notes/cmu_112_graphics.py
from cmu_112_graphics import *

class CustomizedGameMode(Mode):
    def appStarted(mode):
        mode.won = '''                Congratulations on your completion!
                Please click 'Restart' to upload another image or 'Menu' to go to other modes of the Ultimate Puzzle Game! 
                :-)'''
        mode.game = "customizedgame"
        mode.getFile()
        mode.canvasAppStarted()
        mode.puzzleStart()
        mode.createButtons()

    def getSizes(mode):
        mode.getRow()
        mode.getCol()

    def getRow(mode):
        row = mode.getUserInput("Please enter an integer for the number of rows.")
        try:
            row = int(row)
            mode.row = row
        except:
            messagebox.showerror('Error', "Please enter an integer for the number of rows.")
            mode.getRow()

    def getCol(mode):
        col =  mode.getUserInput( "Please enter an integer for the number of columns.")
        try:
            col = int(col)
            mode.col = col
        except:
            messagebox.showerror('Error', "Please enter an integer for the number of columns")
            mode.getCol()

    def getFile(mode):
        mode.filepath = filedialog.askopenfilename()
        caseCheck = mode.filepath.lower()
        if not (caseCheck.endswith(".jpg") or caseCheck.endswith(".png")
                or caseCheck.endswith(".jpeg")):
            messagebox.showerror('Error', "Please upload a .png, .jpg, or .jpeg image to continue. If you want to go back to the Menu Screen, please upload an image first and then click the Menu button.")
            mode.getFile()
        else:
            mode.puzzleIm = mode.loadImage(mode.filepath)

    def canvasAppStarted(mode):
        mode.widthUnit = mode.app.width//10
        mode.heightUnit = mode.app.height//9
        mode.cx, mode.cy = (mode.app.width//2, mode.app.height//2)
        mode.selected = [(-100, -100)]

    def createButtons(mode):
        mode.buttons = []
        menuB = FakeButton(mode.widthUnit*0.5, mode.heightUnit*1.5, 
                           mode.widthUnit*0.8, mode.heightUnit*0.6, 
                           "Menu", mode.menuBCom, mode)
        mode.buttons.append(menuB)
        hintB = FakeButton(mode.widthUnit*0.5, mode.heightUnit*2.5, 
                           mode.widthUnit*0.8, mode.heightUnit*0.6,
                           "Hint", mode.hintBCom, mode)
        mode.buttons.append(hintB)
        solveB = FakeButton(mode.widthUnit*0.5, mode.heightUnit*3.5, 
                            mode.widthUnit*0.8, mode.heightUnit*0.6,
                           "Solve", mode.solveBCom, mode)
        mode.buttons.append(solveB)
        restB = FakeButton(mode.widthUnit*0.5, mode.heightUnit*4.5, 
                           mode.widthUnit*0.8, mode.heightUnit*0.6,
                           "Restart", mode.restartBCom, mode)
        mode.buttons.append(restB)
        mode.solve = False

    def spotBCom(mode):
        mode.stream.stop_stream()
        mode.gameState = "spotify"
        mode.spotify = "playlists"

    def puzzleStart(mode):
        mode.adjustImage()
        mode.marginX = (mode.app.width-mode.puzzleW)//2
        mode.marginY = (mode.app.height-mode.puzzleH)//2
        mode.complete = False

        mode.puzzles = []
        mode.cropPuzzles()

    def cropPuzzles(mode):
        mode.cellWidth = mode.puzzleW // mode.col
        mode.cellHeight = mode.puzzleH // mode.row
        for i in range(mode.row):
            for j in range(mode.col):
                puzzle = mode.puzzleIm.crop((mode.cellWidth*j, mode.cellHeight*i, 
                                       mode.cellWidth*(j+1), mode.cellHeight*(i+1)))
                mode.puzzles.append(puzzle)
        mode.solution = copy.deepcopy(mode.puzzles)
        random.shuffle(mode.puzzles)
        while mode.puzzles == mode.solution:
            random.shuffle(mode.puzzles)

    def menuBCom(mode):
        mode.app.setActiveMode(mode.app.gameMenuMode)

    def hintBCom(mode):
        for index in range(len(mode.solution)):
            if mode.puzzles[index] != mode.solution[index]:
                correctIm = mode.solution[index]
                wrongIm = mode.puzzles[index]
                indexSwap = mode.puzzles.index(correctIm)
                mode.puzzles[index] = correctIm
                mode.puzzles[indexSwap] = wrongIm
                if mode.game == "music":
                    #mode.solution[indexSwap]
                    wrongKey = mode.currStates[correctIm]
                    rightKey = mode.currStates[wrongIm]
                    mode.currStates[correctIm] = rightKey
                    mode.currStates[wrongIm] = wrongKey
                break
        mode.selected = [(-100, -100)]
        mode.completionCheck()
                    
    def solveBCom(mode):
        if not mode.complete:
            mode.solve = True
            mode.hintBCom()
    
    def timerFired(mode):
        if mode.solve and not mode.complete:
            mode.hintBCom()

    def restartBCom(mode):
        mode.appStarted()
        
    def adjustImage(mode):
        (mode.puzzleW, mode.puzzleH) = mode.puzzleIm.size
        widthDiff = mode.app.width - mode.puzzleW
        if widthDiff < 2*mode.widthUnit:
            ratio = (mode.app.width - 2*mode.widthUnit)/mode.puzzleW
            mode.puzzleIm = mode.scaleImage(mode.puzzleIm, ratio)

        (mode.puzzleW, mode.puzzleH) = mode.puzzleIm.size
        heightDiff = mode.app.height - mode.puzzleH
        if heightDiff < 2*mode.heightUnit:
            ratio = (mode.app.height - 2*mode.heightUnit)/mode.puzzleH
            mode.puzzleIm = mode.scaleImage(mode.puzzleIm, ratio)
        (mode.puzzleW, mode.puzzleH) = mode.puzzleIm.size

    def mouseMoved(mode, event):
        for btn in mode.buttons:
            btn.update(event)
    
    def pointInGrid(mode, x, y):
    # copied from http://www.cs.cmu.edu/~112/notes/notes-animations-part1.html#exampleGrids
    # return True if (x, y) is inside the grid defined by app.
        return ((mode.marginX <= x <= mode.app.width-mode.marginX) and
                (mode.marginY <= y <= mode.app.height-mode.marginY))

    def getCell(mode, x, y):
    # copied from http://www.cs.cmu.edu/~112/notes/notes-animations-part1.html#exampleGrids
    # return (row, col) in which (x, y) occurred or (-1, -1) if outside grid.
        if (not mode.pointInGrid(x, y)):
            return (-100,-100)
        else:
            row = int((y - mode.marginY) / mode.cellHeight)
            col = int((x - mode.marginX) / mode.cellWidth)
            return (row, col)

    def mousePressed(mode, event):
        (row, col) = mode.getCell(event.x, event.y)
        if (row, col) == (-100, -100):
            for btn in mode.buttons:
                btn.handleClick(event)
        else:
            if len(mode.selected)== 1:
                mode.selected.append((row, col))
                try: 
                    if (row, col) != (-100, -100):
                        mode.selected.remove((-100, -100))
                except:
                    pass
            if len(mode.selected) == 2:
                (row1, col1) = mode.selected[0]
                (row2, col2) = mode.selected[1]
                mode.swap(row1, col1, row2, col2)
                mode.selected = [(-100, -100)]
            
    def swap(mode, row1, col1, row2, col2):
        #swap the 2 pieces selected
        (index1, index2) = (row1*mode.col+col1, row2*mode.col+col2)
        im1 = mode.puzzles[index1]
        im2 = mode.puzzles[index2]
        mode.puzzles[index1] = im2
        mode.puzzles[index2] = im1
        mode.selected = [(-100, -100)]
        mode.completionCheck()

    def completionCheck(mode):
        if mode.solution == mode.puzzles:
            mode.complete = True
            mode.solve = False
            if mode.game == "music" or mode.game == "colorgame":
                try:
                    mode.currLevel += 1
                    col = (mode.currLevel-1) % 8
                    row = (mode.currLevel-1) // 8
                    levelB = FakeButton(mode.widthUnit*(col+1.5), mode.heightUnit*(row+1.5), mode.widthUnit*0.8, 
                            mode.heightUnit*0.6, " %d " % mode.currLevel, mode.levelBCom, mode, str(mode.currLevel))
                    mode.levelButtons.append(levelB)
                except:
                    pass
            return True
        else:
            mode.complete = False
            return False

    def redrawAll(mode, canvas):
        if mode.game == "customizedgame" or mode.game == "colorgame":
            canvas.create_rectangle(0,0,mode.app.width, mode.app.height, fill = "#99AAAB", width=0)
            for i in range(mode.row):
                for j in range(mode.col):
                    x = (mode.cellWidth*j + mode.cellWidth*(j+1))//2
                    y = (mode.cellHeight*i + mode.cellHeight*(i+1))//2
                    x += mode.marginX
                    y += mode.marginY
                    puzzle = mode.puzzles[(i*mode.col)+j]
                    canvas.create_image(x, y, image=ImageTk.PhotoImage(puzzle))
            if not mode.complete:
                mode.drawBorder(canvas)
            for btn in mode.buttons:
                btn.draw(canvas,mode)
            if mode.complete:
                canvas.create_text(mode.cx, mode.marginY//2+10, text=mode.won, font="Times 18")  

    def drawBorder(mode, canvas):
        for i in range(mode.row):
            for j in range(mode.col):
                (x0,y0,x1,y1)=mode.getBounds(i,j)
                canvas.create_rectangle(x0,y0,x1,y1,outline = "silver", width = 2)
        for (row, col) in mode.selected:
            (x0,y0,x1,y1) = mode.getBounds(row, col)
            canvas.create_rectangle(x0,y0,x1,y1,outline = "red", width = 5)

    def getBounds(mode, row, col):
        x0 = mode.marginX + mode.cellWidth*col
        y0 = mode.marginY + mode.cellHeight*row
        x1 = mode.marginX + mode.cellWidth*(col+1)
        y1 = mode.marginY + mode.cellHeight*(row+1)
        return (x0,y0,x1,y1)

    def sizeChanged(mode):
        mode.marginX = (mode.app.width-mode.puzzleW)//2
        mode.marginY = (mode.app.height-mode.puzzleH)//2

class ColorGameMode(CustomizedGameMode):
    def appStarted(mode):
        try:
            mode.bg = mode.loadImage("colorlevelbg.jpg")
        except:
            mode.bg = mode.loadImage("https://i.ibb.co/Rz598S0/colorlevelbg.jpg")
        mode.Progress = Progress()
        mode.won = '''                Congratulations on your completion! You've unlocked the next level! 
                Please click 'Levels' to proceed or 'Menu' to go to other modes of the Ultimate Puzzle Game! 
                :-)'''
        mode.newPuzzle()
        mode.canvasAppStarted()
        levelPageB = FakeButton(mode.widthUnit*0.5, mode.heightUnit*5.5, 
                           mode.widthUnit*0.8, mode.heightUnit*0.6,
                           "Levels", mode.levelPageBCom, mode)
        mode.currLevel = 0
        mode.game = 'levels'
        mode.levelButtons = []
        level1B = FakeButton(mode.widthUnit*1.5, mode.heightUnit*1.5, mode.widthUnit*0.8, 
                   mode.heightUnit*0.6, " 1 ", mode.levelBCom, mode, " 1 ")
        mode.levelButtons.append(level1B)

        mode.createButtons()
        mode.buttons.append(levelPageB)
    
    def keyPressed(mode, event):
        if event.key == 'c':
            mode.Progress.loadProgress()
            username = mode.getUserInput("Please enter your existing username for the Ultimate Puzzle Game.").lower()
            mode.currLevel = mode.Progress.progressDict[username]['color']
            for i in range(2, mode.currLevel+1):
                col = (i-1) % 8
                row = (i-1) // 8
                levelB = FakeButton(mode.widthUnit*(col+1.5), mode.heightUnit*(row+1.5), mode.widthUnit*0.8, 
                                    mode.heightUnit*0.6, " %d " % i, mode.levelBCom, mode, str(i))
                mode.levelButtons.append(levelB)

    def newPuzzle(mode):
        mode.colors = ['#FFC312','#F79F1F','#EE5A24','#EA2027',
                       '#C4E538','#A3CB38','#009432','#006266',
                       '#12CBC4','#1289A7','#0652DD','#1B1464',
                       '#FDA7DF','#D980FA','#9980FA','#5758BB',
                       '#ED4C67','#B53471','#833471','#6F1E51',
                       '#b8e994','#82ccdd','#78e08f','#fad390']
        c1 = random.choice(mode.colors)
        c2 = random.choice(mode.colors)
        while c2 == c1:
            c2 = random.choice(mode.colors)
        mode.createColorGradient(c1, c2)

    def restartBCom(mode):
        random.shuffle(mode.puzzles)
        mode.complete=False
        
    def levelPageBCom(mode):
        mode.game = 'levels'

    def levelBCom(mode, btn):
        mode.currLevel = int(btn.text.strip())
        mode.game = 'colorgame'
        if mode.currLevel == 1:
            (mode.row, mode.col) = (5, 1)
        elif 2 <= mode.currLevel <= 4:
            (mode.row, mode.col) = (3, mode.currLevel)
        elif 5 <= mode.currLevel <= 9:
            (mode.row, mode.col) = (4, mode.currLevel-2)
        elif 10 <= mode.currLevel <= 12:
            (mode.row, mode.col) = (5, mode.currLevel-4)
        elif 13 <= mode.currLevel <= 18:
            (mode.row, mode.col) = (mode.currLevel-7, 8)
        elif 19 <= mode.currLevel:
            (mode.row, mode.col) = (int(mode.currLevel//1.5), int(mode.currLevel//2))
        mode.newPuzzle()
        mode.puzzleStart()

    def mouseMoved(mode, event):
        if mode.game == 'levels':
            for btn in mode.levelButtons:
                btn.update(event)
        elif mode.game == 'colorgame':
            super().mouseMoved(event)

    def mousePressed(mode, event):
        if mode.game == 'levels':
            for btn in mode.levelButtons:
                btn.handleClick(event)
        elif mode.game == 'colorgame':
            super().mousePressed(event)

    def colorFader(mode, c1,c2,mix=0): 
    # copied from https://stackoverflow.com/questions/25668828/how-to-create-colour-gradient-in-python
    # fade (linear interpolate) from color c1 (at mix=0) to c2 (mix=1)
        c1=np.array(mpl.colors.to_rgb(c1))
        c2=np.array(mpl.colors.to_rgb(c2))
        return mpl.colors.to_hex((1-mix)*c1 + mix*c2)

    def createColorGradient(mode, c1, c2, n=80):
    # modified from https://stackoverflow.com/questions/25668828/how-to-create-colour-gradient-in-python
        fig, ax = plt.subplots(figsize=(8, 5))
        for x in range(n+1):
            ax.axvline(x, color=mode.colorFader(c1,c2,x/n), linewidth=15) 
        plt.savefig("needFilter.png")
        colorImage = Image.open("needFilter.png")
        colorImage = colorImage.crop((120,60,720,445))
        background  = colorImage.transpose(Image.ROTATE_90)
        foreground = Image.open("filter.png")
        mode.puzzleIm = Image.alpha_composite(background, foreground)
        mode.puzzleIm.save("solution.png")
    
    def redrawAll(mode, canvas):
        if mode.game == 'levels':
            canvas.create_image(mode.app.width//2, mode.app.height//2, image=ImageTk.PhotoImage(mode.bg))
            for btn in mode.levelButtons:
                btn.draw(canvas, mode)
        elif mode.game == 'colorgame':
            super().redrawAll(canvas)

class MusicGameMode(CustomizedGameMode):
    fourierInterval = 3.5
    decay = 0.9945
    beatDetect = SimpleBeatDetection()
    def appStarted(mode):
        try:
            mode.bg = mode.loadImage("muslevelbg.jpg")
        except:
            mode.bg = mode.loadImage("https://i.ibb.co/8DwvThD/muslevelbg.jpg")
        mode.Progress = Progress()
        mode.gameState = "levels"
        mode.game = "music"
        (mode.marginX, mode.marginY) = (mode.app.width//10,mode.app.height//9)
        (mode.puzzleW, mode.puzzleH) = (mode.app.width-2*mode.marginX, mode.app.height-2*mode.marginY)
        mode.widthUnit = mode.app.width//10
        mode.heightUnit = mode.app.height//9
        mode.selected = [(-100,-100)]
        mode.complete = False

        mode.lastBeatTimer = 0
        mode.beatTimer = 0

        mode.dots = []
        mode.createButtons()
        mode.levelButtons = []
        levelPageB = FakeButton(mode.widthUnit*0.5, mode.heightUnit*5.5, 
                           mode.widthUnit*0.8, mode.heightUnit*0.6,
                           "Levels", mode.levelPageBCom, mode)
        mode.buttons.append(levelPageB)
        cusLevelB = FakeButton(mode.widthUnit*0.5, mode.heightUnit*1.5, mode.widthUnit*0.8, 
                   mode.heightUnit*0.6, " S ", mode.cusBCom, mode, " S ")
        level1B = FakeButton(mode.widthUnit*1.5, mode.heightUnit*1.5, mode.widthUnit*0.8, 
                   mode.heightUnit*0.6, " 1 ", mode.levelBCom, mode, " 1 ")
        mode.levelButtons.append(cusLevelB)
        mode.levelButtons.append(level1B)
        
        mode.fourierColors="#FFC5C5"
        mode.fourierGraph = Graph((mode.app.width, 0), mode.app.height, 
                          mode.fourierColors, 1.5, 0.684 * MusicGameMode.fourierInterval, False)

        mode.colorschemas = [["#55efc4", "#81ecec", "#74b9ff", "#a29bfe", "#ffeaa7", "#fab1a0"],
                            ["#fa983a", "#b71540", "#F8EFBA","#1e3799", "#3c6382"],
                            ["#00CCCD", "#1287A5", "#EA7773", "#2B2B52", "#F5BCBA"],
                            ["#30336B", "#67E6DC", "#0A3D62", "#6A89CC"],
                            ["#40407a", "#706fd3", "#f7f1e3", "#34ace0", "#33d9b2"]]
        mode.colors = mode.colorschemas[0]
        mode.time = 0
        mode.last = 0
    
        mode.backgroundColor = "#FEFEFE"
        mode.font = "Calibri"

        mode.velx = 10
        mode.vely = 10
        mode.offset = 0
        mode.lastBeat = int(round(time.time() * 1000))

    def keyPressed(mode, event):
        if event.key == 'c':
            mode.Progress.loadProgress()
            username = mode.getUserInput("Please enter your existing username for the Ultimate Puzzle Game.").lower()
            mode.currLevel = mode.Progress.progressDict[username]['music']
            for i in range(2, mode.currLevel+1):
                col = (i-1) % 8
                row = (i-1) // 8
                levelB = FakeButton(mode.widthUnit*(col+1.5), mode.heightUnit*(row+1.5), mode.widthUnit*0.8, 
                                    mode.heightUnit*0.6, " %d " % i, mode.levelBCom, mode, str(i))
                mode.levelButtons.append(levelB)

    def cusBCom(mode, btn):
        mode.getSizes()
        mode.cellWidth = (mode.app.width - 2*mode.marginX)//mode.col
        mode.cellHeight = (mode.app.height - 2*mode.marginY)//mode.row
        mode.checkAuth()
        mode.createSpotifyBtns()
        mode.gameState = "spotify"
        mode.spotify = "playlists"
    
    def checkAuth(mode):
        username = mode.getUserInput("Please enter your Spotify username :-)")
        mode.SpotifyUser = SpotifyInfo(username)
        if mode.SpotifyUser.gotAuth:
            spotB = FakeButton(mode.widthUnit*0.5, mode.heightUnit*6.5, 
                           mode.widthUnit*0.8, mode.heightUnit*0.6,
                           "Spotify", mode.spotBCom, mode)
            mode.buttons.append(spotB)
            return None
        else:
            messagebox.showerror('Error', "Authorization failed. Please double check your username and authorization.")
            mode.checkAuth()

    def filpBCom(mode, btn):
        if btn.text == " \/ ":
            index = -1
        elif btn.text == " /\ ":
            index = 1
        if mode.spotify == "playlists":
            for btn in mode.playlistBtns:
                btn.cy += index*mode.app.height
                btn.y0 = btn.cy - btn.height//2
                btn.y1 = btn.cy + btn.height//2
        elif mode.spotify == "songs":
            for btn in mode.songBtnsDict[mode.currPlaylist]:
                btn.cy += index*mode.app.height
                btn.y0 = btn.cy - btn.height//2
                btn.y1 = btn.cy + btn.height//2

    def createSpotifyBtns(mode):
        mode.playlistBtns = []
        mode.songBtnsDict = {}
        mode.upDown = []
        downB = FakeButton(mode.app.width - mode.app.width//8+50, mode.app.height//12, 
                           40, 25, " \/ ", mode.filpBCom, mode, " \/ ", '#019031', '#DAE0E2')
        upB = FakeButton(mode.app.width - mode.app.width//8, mode.app.height//12, 
                         40, 25, " /\ ", mode.filpBCom, mode, " /\ ", '#019031', '#DAE0E2')
        mode.upDown.append(downB)
        mode.upDown.append(upB)
                
        lastEnd = 0
        lastRowEndIndex = 0
        r = 0 #row
        scroll = 0
        for i in range(len(mode.SpotifyUser.playlistsNames)):
            playlist = mode.SpotifyUser.playlistsNames[i].strip()
            c = i - lastRowEndIndex
            btnWidth = 12*len(playlist) + 30
            btnHeight = 40
            (gapx, startx, gapy, starty) = (0, lastEnd + 30, 60, mode.app.height//5)
            startTestX = gapx * c + startx + btnWidth
            if (startTestX > mode.app.width - 2*mode.marginX):
                r += 1
                lastRowEndIndex = i
                c = 0
                startx = 30
            if r >= 9:
                r = 0
                scroll += mode.app.height
            cx = gapx * c + startx + mode.marginX + btnWidth//2
            cy = scroll + gapy * r + starty + btnHeight//2
            playlistB = FakeButton(cx, cy, btnWidth, btnHeight, playlist, 
                                   mode.playlistBCom, mode, playlist, '#57606f','#019031')
            mode.playlistBtns.append(playlistB)
            lastEnd = gapx * c + startx + btnWidth
        
        for playlist in mode.SpotifyUser.playlistsNames:
            lastEnd = 0
            lastRowEndIndex = 0
            r = 0 #row
            scroll = 0
            songBs = []
            playlistSongs = list(mode.SpotifyUser.playListDict[playlist])
            for j in range(len(playlistSongs)):
                song = playlistSongs[j]
                url = mode.SpotifyUser.songURLs[song]
                c = j - lastRowEndIndex
                space = song.count(" ")//2 + 2*song.count("(") + song.count(".")
                btnWidth = 15*(len(song)-space) + 30
                btnHeight = 40
                (gapx, startx, gapy, starty) = (0, lastEnd + 30, 60, mode.app.height//5)
                startTestX = gapx * c + startx + btnWidth
                startTestY = gapy * r + starty + btnHeight
                if (startTestX > mode.app.width - mode.marginX):
                    r += 1
                    lastRowEndIndex = j
                    c = 0
                    startx = 30
                if r >= 9:
                    r = 0
                    scroll += mode.app.height
                cx = gapx * c + startx + mode.marginX//2 + btnWidth//2
                cy = scroll + gapy * r + starty + btnHeight//2
                songB = FakeButton(cx, cy, btnWidth, btnHeight, song, 
                                   mode.songBCom, mode, url,'#57606f','#019031')
                                   # + outline and background color
                songBs.append(songB)
                lastEnd = gapx * c + startx + btnWidth
            mode.songBtnsDict[playlist] = set(songBs)
                
    def playlistBCom(mode, btn):
        mode.currPlaylist = btn.text
        mode.spotify = "songs"
        
    def songBCom(mode, btn):
        mode.songPath = os.path.abspath(mode.SpotifyUser.getFile(btn.text))
        mode.fileName = mode.songPath[0:-4]
        mode.posx = mode.marginX + mode.widthUnit//2
        mode.posy = mode.marginY + mode.heightUnit//2
        mode.targets = [(mode.posx, mode.posy)]
        mode.dots = []
        mode.gameState = 'game'
        mode.complete = False
        mode.setStartVals()   

    def levelBCom(mode, btn):
        mode.currLevel = int(btn.text.strip())
        mode.gameState = 'game'
        mode.complete = False
        mode.getFile()
        if mode.currLevel == 1:
            (mode.row, mode.col) = (3, 1)
        elif 2 <= mode.currLevel <= 4:
            (mode.row, mode.col) = (3, mode.currLevel)
        elif 5 <= mode.currLevel <= 9:
            (mode.row, mode.col) = (4, mode.currLevel-2)
        elif 10 <= mode.currLevel <= 12:
            (mode.row, mode.col) = (5, mode.currLevel-4)
        elif 13 <= mode.currLevel <= 18:
            (mode.row, mode.col) = (mode.currLevel-7, 8)
        elif 19 <= mode.currLevel:
            (mode.row, mode.col) = (int(mode.currLevel//1.5), int(mode.currLevel//2))
        
        mode.cellWidth = (mode.app.width - 2*mode.marginX)//mode.col
        mode.cellHeight = (mode.app.height - 2*mode.marginY)//mode.row
        mode.setStartVals()

    def levelPageBCom(mode):
        try:
            if (mode.stream != None):
                    mode.stream.stop_stream()
        except:
            pass
        mode.stream = None
        mode.fourierGraph.maxVal = 0
        mode.setStartVals()

        mode.gameState = 'levels'

    def setStartVals(mode):
        mode.puzzles = []
        mode.solution = []
        mode.currStates = {}
        mode.generatePuzzle()

        mode.p = None
        mode.maxEnergy = 0
        mode.timescale = 1

        mode.fourier = []
        mode.insEnergies = []
        mode.energyAvgs = []
        mode.beats = []

    def getFile(mode):
        # mode.posx = mode.widthUnit
        # mode.posy = mode.height - mode.heightUnit
        mode.posx = mode.marginX + mode.widthUnit//2
        mode.posy = mode.marginY + mode.heightUnit//2
        mode.targets = [(mode.posx, mode.posy)]
        mode.dots = []
        mode.songPath = filedialog.askopenfilename()
        mode.fileName = mode.songPath[0:-4]
        caseCheck = mode.songPath.lower()
        if not (caseCheck.endswith(".wav") or caseCheck.endswith(".mp3") ):
            messagebox.showerror('Error', "Please upload a .wav or .mp3 song file to continue. If you want to go back to the Menu Screen, please upload a filefirst and then click the Menu button.")
            mode.getFile()
        if caseCheck.endswith(".mp3"):
            src = mode.songPath
            lastChar = len(mode.songPath) - 5
            dst = mode.songPath[0: -4] + ".wav"
            # convert wav to mp3                                                            
            sound = AudioSegment.from_mp3(src)
            sound.export(dst, format="wav")
            mode.songPath = dst

    def newColorSchema(mode): 
        #Gets a new colorschema that is different from the last
        bad = mode.colors
        while (mode.colors == bad):
            mode.colors = random.choice(mode.colorschemas)
    
    def mousePressed(mode, event):
        if mode.gameState == 'levels':
            for btn in mode.levelButtons:
                btn.handleClick(event)
        elif mode.gameState == "spotify":
            for btn in mode.upDown:
                btn.handleClick(event)
            if mode.spotify == 'playlists':
                for btn in mode.playlistBtns:
                    btn.handleClick(event)
            elif mode.spotify == 'songs':
                for btn in mode.songBtnsDict[mode.currPlaylist]:
                    btn.handleClick(event)
        elif mode.gameState == 'game':
            super().mousePressed(event)

    def mouseMoved(mode, event):
        if mode.gameState == 'levels':
            for btn in mode.levelButtons:
                btn.update(event)
        elif mode.gameState == "spotify":
            for btn in mode.upDown:
                btn.update(event)
            if mode.spotify == 'playlists':
                for btn in mode.playlistBtns:
                    btn.update(event)
            elif mode.spotify == 'songs':
                for btn in mode.songBtnsDict[mode.currPlaylist]:
                    btn.update(event)
        elif mode.gameState == 'game':
            super().mouseMoved(event)

    def drawMargin(mode, canvas):
        canvas.create_rectangle(0, 0, mode.marginX, mode.app.height, fill = "#99AAAB", width = 0)
        canvas.create_rectangle(mode.app.width-mode.marginX, 0, mode.app.width, mode.app.height, fill = "#99AAAB", width = 0)
        canvas.create_rectangle(0, 0, mode.app.width, mode.marginY, fill = "#99AAAB", width = 0)
        canvas.create_rectangle(0, mode.app.height-mode.marginY, mode.app.width, mode.height, fill = "#99AAAB", width = 0)
        # canvas.create_text(mode.app.width//2, mode.app.height//12, text = mode.fileName, font = 'Times 30 bold' )

    def redrawAll(mode, canvas):
        if mode.gameState == 'levels':
            canvas.create_image(mode.app.width//2, mode.app.height//2, image=ImageTk.PhotoImage(mode.bg))
            for btn in mode.levelButtons:
                btn.draw(canvas, mode)
        elif mode.gameState == 'spotify':
            username = mode.SpotifyUser.displayName
            canvas.create_rectangle(0,0, mode.app.width, mode.app.height, fill ='#a4b0be', width =0 )
            canvas.create_line(0, mode.app.height//7, mode.app.width, mode.app.height//7, width = 8, fill = '#019031')
            for btn in mode.upDown:
                btn.draw(canvas, mode)
            if mode.spotify == "playlists":
                canvas.create_text(mode.app.width//2, mode.app.height//12, 
                                   text = "Welcome to " + username + "'s Spotify Playlists", 
                                   font = 'Times 30 bold')
                for btn in mode.playlistBtns:
                    btn.draw(canvas, mode)
            elif mode.spotify == "songs":
                canvas.create_text(mode.app.width//2, mode.app.height//12, 
                                   text = "Songs in the '" + mode.currPlaylist + "' Playlist", 
                                   font = "Times 30 bold italic")
                for btn in mode.songBtnsDict[mode.currPlaylist]:
                    btn.draw(canvas, mode)
        else:
            canvas.create_rectangle(-10, -10,mode.app.width+10,mode.app.height+10, fill = mode.backgroundColor, width=0) 
            #Apply the background color
            mode.fourierGraph.draw(mode.fourier, canvas) 
            #Draw the equalizer fourier transform behind everything else
        
            for dot in reversed(mode.dots): 
            #Draw all the dots, most recent ones first
                dot.draw(canvas)
            if not mode.complete:
                mode.drawBorder(canvas)
            mode.drawMargin(canvas)
            for btn in mode.buttons:
                btn.draw(canvas,mode)

            if mode.complete:
                try:
                    if mode.spotify == "songs":
                        won = '''                Congratulations on your completion! 
                Please click 'Levels' to proceed or 'Menu' to go to other modes of the Ultimate Puzzle Game! 
                :-)'''
                except:
                    won = '''                Congratulations on your completion! You've unlocked the next level! 
                Please click 'Levels' to proceed or 'Menu' to go to other modes of the Ultimate Puzzle Game! 
                :-)'''
                canvas.create_text(mode.app.width//2, mode.app.height//14, text = won, font = 'Times 18')

    def explode(mode, x, y, pCount = 20, vel = 3, velr = -1.5, offset = 0, 
                r=None, curvy=True): 
        # creates dots for an explosion with the given parameters
        dirts = []
        for i in range(pCount):
            dirts.append(i * (math.pi/2)/pCount + offset)
        for d in dirts:
            velx = math.cos(d) * vel
            vely = math.sin(d) * vel
            mode.dots.append(Dot(x, y, mode, velx, vely, velr, r, curvy))

    def beatExplode(mode, x, y, pCount = 20, vel = 3, velr = -1.5, r=None, curvy=True): 
        # creates dots for an explosion with the given parameters
        dirHalf = []
        dirOtherHalf = []
        for i in range(pCount):
            if i < pCount//2:
                dirHalf.append(i * (math.pi/2)/pCount)
            else:
                dirOtherHalf.append(i * (math.pi/2)/pCount)
        for d in dirHalf:
            # create a list with the radius/whatever, pop the first after used and append it
            # so just keeps poping and appending :-)
            velx = math.cos(d) * vel + dirHalf.index(d)%((len(dirHalf)-1)//2)
            vely = math.sin(d) * vel + dirHalf.index(d)%((len(dirHalf)-1)//2)
            mode.dots.append(Dot(x, y, mode, velx, vely, velr, r, curvy))
        for d in dirOtherHalf:
            # create a list with the radius/whatever, pop the first after used and append it
            # so just keeps poping and appending :-)
            velx = math.cos(d) * vel + dirOtherHalf.index(d)%((len(dirOtherHalf)-1)//2)
            vely = math.sin(d) * vel + dirOtherHalf.index(d)%((len(dirOtherHalf)-1)//2)
            mode.dots.append(Dot(x, y, mode, velx, vely, velr, r, curvy))
            
    def timerFired(mode):
        if mode.gameState == "levels" or mode.gameState == "spotify":
            pass
        else:
            mode.update()
            mode.lastBeatTimer = mode.beatTimer
            if (mode.beatTimer > 0):
                mode.beatTimer -= 2
            mode.time += 1
            #Decay the max value so the song has a chance to trigger another explosion
            decrement = mode.maxEnergy - mode.maxEnergy * MusicGameMode.decay
            mode.maxEnergy -= decrement
            if (mode.p == None):
                mode.playAudio()      
            for dot in (mode.dots):
                dot.update(mode)
            if (mode.time - mode.last >= 1): 
                # more dots at the emitter spot to identify it
                mode.last = mode.time
                for i in range(2):
                    mode.dots.append(Dot(mode.posx, mode.posy, mode, None, None, -1))
            mode.update()
            super().timerFired()

    def playAudio(mode):
        mode.p = pyaudio.PyAudio()
        p = mode.p
        MusicGameMode.wf = wave.open(mode.songPath, 'rb')
        mode.wf = MusicGameMode.wf
        mode.stream = p.open(format=p.get_format_from_width(mode.wf.getsampwidth()),
                    channels=mode.wf.getnchannels(), rate=mode.wf.getframerate(), output=True,
                    stream_callback = mode.callback)
                        # getsampwidth: returns sample width in bytes (in_data)
                # getnchannels: returns numer of audio channels (frame)
                # getframerate: return sampling frequency  

    def menuBCom(mode):
        try:
            if (mode.stream != None):
                    mode.stream.stop_stream()
        except:
            pass
        mode.stream = None
        mode.fourierGraph.maxVal = 0
        mode.setStartVals()
        super().menuBCom()
    
    def changeColors(mode): 
        # Pick a new random color scheme, and create an explosion 
        # of dots to commemorate it
        mode.newColorSchema()
        (x,y) = mode.updateSpecific(mode.posx, mode.posy)
        mode.beatExplode(x, y, 50, 30, -0.5, None, False) 

    def callback(mode, in_data, frame_count, time_info, status): 
        #Handle the audio processing on another thread to keep things fluid
        datum = MusicGameMode.wf.readframes(frame_count)
        #readframes returns frames of audio
        p = mode.p
        stream = mode.stream
        mode.signal = np.frombuffer(datum, dtype=np.int16) 
        #Convert the byte code to an understandable signal
        result = MusicGameMode.beatDetect.detect_beat(mode.signal, mode) 
        #Check if this chunk had a beat or not
        if (result != None):
            curTime = int(round(time.time() * 1000))
            timeSinceLastBeat = curTime - mode.lastBeat
            intervalNeeded = 5
            if (timeSinceLastBeat > intervalNeeded):
                InstantEnergy = result[0].item()
                count = (math.ceil(InstantEnergy))//15
                if (count == 0):
                    count = 1
                    baseSize = 3
                else:
                    baseSize = 5
                if (InstantEnergy > mode.maxEnergy):
                    mode.maxEnergy = InstantEnergy
                    mode.changeColors()
                mode.lastBeat = curTime
                mode.offset += 0.1
                if (mode.offset >= math.pi//2.5):
                    mode.offset = 0
                #offset is the rotation-ish part for new dots
                (x,y) = mode.updateSpecific(mode.posx, mode.posy)
                mode.explode(x, y, count, 15, -0.1, mode.offset, baseSize + random.randrange(4), False)
        return (datum, pyaudio.paContinue)

    def getSmallCanvas(mode,x,y):
        (row, col) = mode.getCell(x,y)
        smallX = int(x - mode.marginX - mode.cellWidth*col)
        smallY = int(y - mode.marginY - mode.cellHeight*row)
        return (row, col, smallX, smallY)

    def getBigCanvas(mode, r, c, smallX, smallY):
        try:
            (startX, startY) = mode.currStates[(r,c)]
            bigX = int(startX + smallX)
            bigY = int(startY + smallY)
            return (bigX, bigY)
        except:
            return (None, None)

    def updateSpecific(mode, x, y):
        (r,c,nx,ny) = mode.getSmallCanvas(x, y)
        if ((r,c)!= (None, None) and 0<=r<mode.row and 0<=c<mode.col): 
            return mode.getBigCanvas(r, c, nx, ny)

    def update(mode):
        for dot in mode.dots:
            (X, Y) = (dot.x, dot.y)
            (r,c,x,y) = mode.getSmallCanvas(X, Y)
            if ((r,c)!= (None, None) and 0<=r<mode.row and 0<=c<mode.col): 
                (dot.x, dot.y) = mode.getBigCanvas(r, c, x, y)
            else:
                (dot.x, dot.y) = (int(dot.x), int(dot.y))
        for target in mode.targets:
            (x,y) = target
            (r,c,nx,ny) = mode.getSmallCanvas(x, y)
            if ((r,c)!= (None, None) and 0<=r<mode.row and 0<=c<mode.col): 
                mode.targets[mode.targets.index(target)] = mode.getBigCanvas(r, c, nx, ny)

    def swap(mode, oldR, oldC, row, col):
        oldTopLeft = mode.currStates[(oldR, oldC)]
        newTopLeft = mode.currStates[(row, col)]
        mode.currStates[(row, col)] = oldTopLeft
        mode.currStates[(oldR, oldC)] = newTopLeft

        oldIndex = mode.puzzles.index((oldR, oldC))
        newIndex = mode.puzzles.index((row, col))
        mode.puzzles[oldIndex] = (row, col)
        mode.puzzles[newIndex] = (oldR, oldC)

        mode.update()
        mode.completionCheck()

    def generatePuzzle(mode):
        mode.topLefts = []
        for i in range(mode.row):
            for j in range(mode.col):
                mode.puzzles.append((i,j))
        mode.solution = copy.copy(mode.puzzles)
        while mode.puzzles == mode.solution:
            random.shuffle(mode.puzzles)
        for item in mode.solution:
            (i, j) = item
            (x0,y0,x1,y1)=mode.getBounds(i,j)
            topLeft = (x0,y0)
            mode.topLefts.append(topLeft)
            cellMatch = mode.puzzles[mode.solution.index(item)]
            mode.currStates[cellMatch] = topLeft

class GameMenuMode(Mode):
    def appStarted(mode):
        mode.Progress = Progress()
        mode.widthUnit = mode.app.width//10
        mode.heightUnit = mode.app.height//18
        (mode.cx, mode.cy) = (mode.app.width//2, mode.app.height//2)
        mode.buttons = []
        cusB = FakeButton(mode.cx, mode.heightUnit*8.5, mode.widthUnit*3.5, mode.heightUnit*1.33, 
                          "Create Your Own Puzzle", mode.cusBCom, mode)
        mode.buttons.append(cusB)
        colB = FakeButton(mode.cx, mode.heightUnit*10.5, mode.widthUnit*3.5, mode.heightUnit*1.33,
                          "Color Puzzle", mode.colBCom, mode)
        mode.buttons.append(colB)
        musB = FakeButton(mode.cx, mode.heightUnit*12.5, mode.widthUnit*3.5, mode.heightUnit*1.33, 
                          "Music Puzzle", mode.musBCom, mode)
        mode.buttons.append(musB)
        helpB = FakeButton(mode.cx, mode.heightUnit*14.5, mode.widthUnit*3.5, mode.heightUnit*1.33, 
                           "Instruction & Help", mode.helpBCom, mode)
        mode.buttons.append(helpB)
        try:
            mode.bg = Image.oen("background.png")
        except:
            mode.bg = mode.loadImage("https://gucki.it/wp-content/uploads/2017/11/app-i-love-hue-gioco.png")
        try:
            mode.title = Image.open("welcome.png")
        except:
            mode.title = mode.loadImage("https://i.ibb.co/h936dpQ/2019-12-01-4-47-45.png")
        
        mode.title = mode.scaleImage(mode.title, 1/2)
        mode.bg = mode.scaleImage(mode.bg, 6/7)

    def cusBCom(mode):
        mode.app.gameModeCustomized = CustomizedGameMode()
        mode.app.gameModeCustomized.getSizes()
        mode.app.setActiveMode(mode.app.gameModeCustomized)

    def musBCom(mode):
        mode.app.setActiveMode(mode.app.gameModeMusic)

    def colBCom(mode):
        mode.app.setActiveMode(mode.app.gameModeColor)

    def helpBCom(mode):
        mode.app.setActiveMode(mode.app.helpMode)

    def mousePressed(mode, event):
        for btn in mode.buttons:
            btn.handleClick(event)

    def mouseMoved(mode, event):
        for btn in mode.buttons:
            btn.update(event)

    def sizeChanged(mode):
        mode.appStarted()
    
    def keyPressed(mode, event):
        if event.key == 's':
            username = mode.getUserInput("Please create or enter your username for the Ultimate Puzzle Game.").lower()
            colorLevel = mode.app.gameModeColor.currLevel
            musicLevel = mode.app.gameModeMusic.currLevel
            mode.Progress.writeProgress(username, colorLevel, musicLevel)

    def redrawAll(mode, canvas):
        cx = mode.app.width//2
        cy = mode.app.height//2
        canvas.create_image(cx, cy, image=ImageTk.PhotoImage(mode.bg))
        canvas.create_image(cx, cy//2, image=ImageTk.PhotoImage(mode.title))
        for btn in mode.buttons:
            btn.draw(canvas, mode)

class HelpMode(Mode):
    def appStarted(mode):
        mode.instruction = '''
        Welcome to the Ultimate Puzzle Game!!!
        This game is composed of 3 different modes.

        'Create Your Own Puzzle': 
            allows you to upload an image and customize your own unique puzzle and its difficulty.
        'Color Puzzle': 
            has different levels with random image of a color gradient. Levels will be generated once you complete the current level!
        'Music Puzzle': 
            upload a .wav or .mp3 file or get access to your Spotify and challenge yourself with completing a puzzle in motion 
            with the music! Please be aware that you can only access 30s if you choose to use audio from your Spotify account.
        
        In each mode, the 'Hint' button will help you move one piece of the puzzle in place, 
        and the 'Solve' button will automatically solve the entire puzzle.

        To swap place for two pieces, simply click the two pieces that you want to swap. The piece already selected will have a 
        red outline. Outlines will disappear once the puzzle is completed.

        You can return to the Menu page from each mode by clicking the 'Menu' button. 

        If you wish to continue with your past progress, please press 'c' in the respective mode and enter your username.

        If you wish to save progress, please press 's' in the game Menu screen and create a username. Usernames are not case-sensitive.
        
        Enjoy the game! :-) '''
        mode.widthUnit = mode.app.width//10
        mode.heightUnit = mode.app.height//9
        try:
            mode.bg = mode.loadImage("helpbg.jpg")
        except:
            mode.bg = mode.loadImage("https://i.ibb.co/2thJTH9/helpbg.jpg")
        mode.menuB = FakeButton(mode.app.width//2, mode.heightUnit*8, 
                           mode.widthUnit*0.8, mode.heightUnit*0.6, 
                           "Menu", mode.menuBCom, mode)

    def redrawAll(mode, canvas):
        canvas.create_image(mode.app.width//2, mode.app.height//2, image=ImageTk.PhotoImage(mode.bg))
        canvas.create_text(mode.app.width//2, mode.app.height//2-20, text = mode.instruction, font = "Times 17 bold")
        mode.menuB.draw(canvas, mode)
    
    def mousePressed(mode, event):
        mode.menuB.handleClick(event)

    def mouseMoved(mode, event):
        mode.menuB.update(event)

    def menuBCom(mode):
        mode.app.setActiveMode(mode.app.gameMenuMode)

class MyModalApp(ModalApp):
    def appStarted(app):
        app.gameMenuMode = GameMenuMode()
        app.gameModeColor = ColorGameMode()
        app.gameModeCustomized = CustomizedGameMode()
        app.gameModeMusic = MusicGameMode()
        app.helpMode = HelpMode()
        app.setActiveMode(app.gameMenuMode)

def main():
    app = MyModalApp(width = 1000, height = 700)

if __name__ == '__main__':
    main()
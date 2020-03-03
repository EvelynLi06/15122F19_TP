############################################
#### Evelyn - the Ultimate Puzzle Game ##### 
######### Detect Beat/Explosion  ###########
############################################
# modified from Devansh Kukreja TP - Pulse 
# https://github.com/devanshk/Pulse

import numpy
import pyaudio
import wave
from grapher import Graph

fourierInterval = 5

# modified from Devansh Kukreja TP - Pulse 
class SimpleBeatDetection:
    # Beat detection algorithm from: 
    # http://archive.gamedev.net/archive/reference/programming/features/beatdetection/index.html
    def __init__(self):
        self.localNrg = numpy.zeros(200) # the last 200 'frames' --> buffer
        self.localNrgIndex = 199 # last element 

    def detect_beat(self, signal, data = None): 
        localNrgAvg = self.localNrg.mean() # the average energy from the history
        localNrgVar = self.localNrg.var() # variance

        beatSens = (-0.0025714 * localNrgVar) + 1.15142857 
        # Remove noises

        instantNrg = numpy.dot(signal.astype(numpy.int), 
                                  signal.astype(numpy.int)) / float(0xffffffff)
        # Creates a copy of the array, casted to integers, square it and get sum 
        self.localNrg[self.localNrgIndex] = instantNrg
        # Push the current chunk's value into the ring buffer

        beat = (abs(instantNrg) > abs(beatSens * \
                 localNrgAvg) and instantNrg > 1) 
        # check volume

        self.localNrgIndex -= 1 
        if self.localNrgIndex < 0: 
            #If we've gone all the way around the buffer, reset the index
            self.localNrgIndex = len(self.localNrg) - 1
        if len(data.signal) == 0: 
            print(data.complete)
            if data.complete:
                data.playAudio()
            else:
                data.stream.stop_stream()
                data.p = None
                data.stream = None
                data.maxEnergy = 0
                data.timescale = 1
                data.fourier = []
                data.fourierGraph.maxVal = 0
        data.insEnergies += [instantNrg]
        data.energyAvgs += [localNrgAvg]
        data.beats += [beat]

        ###################################################
        #fourier portion copied form past project Pulse
        fourier = numpy.fft.fft(data.signal) 
        #Do the fourier transform
        data.fourier = fourier.real[::fourierInterval] 
        #And save a version we can use to data for graphing
        ###################################################

        if len(data.insEnergies) > 500: 
            #keep 150 dots, remove the oldest one
            removedTop = False
            #And if we got rid of the previous max, compute a new maximum value for the graph
            if (data.insEnergies.pop(0) >= Graph.maxVal or 
                data.energyAvgs.pop(0) >= Graph.maxVal or 
                data.beats.pop(0) >= Graph.maxVal): 
                removedTop = True
            if (removedTop):
                self.max = 0
                for i in range(500):
                    if (data.insEnergies[i] > self.max):
                        self.max = data.insEnergies[i]
                    if (data.energyAvgs[i] > self.max):
                        self.max = data.energyAvgs[i]
                Graph.maxVal = self.max
        if (beat):
            return (instantNrg, localNrgAvg)
        return None
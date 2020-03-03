############################################
#### Evelyn - the Ultimate Puzzle Game ##### 
######### load and save Progress ###########
############################################
import csv

# algorithm modified from https://realpython.com/python-csv/#reading-csv-files-with-csv
class Progress():
    def __init__(self):
        self.progressDict = {}
        self.newPlayer = True
        self.progressLoaded = False

    def loadProgress(self):
        self.progressLoaded = True
        with open('PlayerProgress.csv', mode = 'r') as csvfile:
            csvReader = csv.reader(csvfile)
            next(csvReader, None)
            for row in csvReader:
                username = row[0]
                colorLevel = int(row[1])
                musicLevel = int(row[2])
                self.progressDict[username] = {'color': colorLevel,
                                            'music': musicLevel}

    def writeProgress(self, username, colorLevel, musicLevel):
        progressList = list()
        with open('PlayerProgress.csv', mode = 'r') as csvfile:
            csvReader = csv.reader(csvfile)
            next(csvReader, None)
            for row in csvReader:
                if row[0] == username:
                    self.newPlayer = False
                    info = [row[0], colorLevel, musicLevel]
                else:
                    info = [row[0], row[1], row[2]]
                progressList.append(info)
            
        with open('PlayerProgress.csv', mode = 'w') as csvfile:
            csvWriter = csv.writer(csvfile)
            csvWriter.writerow(['username', 'color levels', 'music levels'])
            for person in progressList:
                csvWriter.writerow(person)
            if self.newPlayer:
                currentInfo = [username,colorLevel, musicLevel]
                csvWriter.writerow(currentInfo)
import math

class ProbabilityComputer():
    def __init__(self):
        self.flashCount = 0 #Voir ce qu'on fait de cette variable
        self.prior = []
        self.post = []

        self.maxProbability = 0
        self.priorProbabilities = []

    def getP300Results(self, n):
        proba = []
        p300Data = "" #Ici on doit avoir le résultat reçu

        set = False
        if(";" in p300Data):
            lf_list = p300Data.split(";")
            if(len(lf_list) == 2 * n):
                for i in range(0, len(lf_list), 2):
                    LF0 = 0
                    LF1 = 0
                    if(self.isfloat(lf_list[i])):
                        if(self.isfloat(lf_list[i + 1])):
                            LF = [LF0, LF1]
                            proba.append(LF)
                            set = True
            else:
                print("ProbaComputer received " + len(lf_list / 2) + " instead of " + n)

        if(not set):
            print("ProbaComputer received inconsistent data as LF: '" + p300Data + "'. Data dropped")


        #Prevent missing data
        if(len(proba) < n):
            for i in range(len(proba), n, 1):
                LF = [0, 0]
                proba.append(LF)

        #We are done, release used data
        p300Data = ""

        return proba

    def computePosteriorProbabilities(self, flashSequenceList, likelyhoods):
        finalProbabilities = []
        nbItems = 7
        self.priorProbabilities = []
        if(len(self.priorProbabilities == 0)):
            equiproba = 1 / nbItems
            self.priorProbabilities = []
            for idx in range(0, nbItems, 1):
                self.priorProbabilities.append(equiproba)
                finalProbabilities.append(0)

        if(len(likelyhoods) == len(flashSequenceList)):
            for flashIdx in range(0, len(flashSequenceList), 1):
                for itemIdx in range(0, nbItems, 1):
                    if(flashSequenceList[flashIdx] == itemIdx):
                        finalProbabilities[itemIdx] = math.log(self.priorProbabilities[itemIdx]) + likelyhoods[flashIdx][0]
                    else:
                        finalProbabilities[itemIdx] = math.log(self.priorProbabilities[itemIdx]) + likelyhoods[flashIdx][1]

                maxProba = 0
                for proba in finalProbabilities:
                    if(proba > maxProba):
                        maxProba = proba

                sumProba = 0
                for idx in range(0, len(finalProbabilities), 1):
                    finalProbabilities[idx] -= maxProba - 1
                    finalProbabilities[idx] = math.exp(finalProbabilities[idx])
                    sumProba += finalProbabilities[idx]

                for idx in range(0, len(finalProbabilities), 1):
                    finalProbabilities[idx] /= sumProba
                    self.priorProbabilities[idx] = finalProbabilities[idx]

        #Compute Entropie here

        #
        else:
            print("We don't have the same number of LF ('" + len(likelyhoods) + "') and flashes (" + len(flashSequenceList) + ") provided in our analysis")

        return finalProbabilities

    def isfloat(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

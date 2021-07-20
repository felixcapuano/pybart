import math
import sys

class ProbabilityComputerClassic:
    def __init__(self, stimulusLabelList):
        self.stimulusLabelList = stimulusLabelList
        self.triggerCount = len(stimulusLabelList)
        self.reset()

    def reset(self):
        self.flashCount = 0  # Voir ce qu'on fait de cette variable
        self.prior = []
        self.post = []

        self.maxProbability = 0
        self.priorProbabilities = []

        equiproba = 1.0 / self.triggerCount
        self.priorProbabilities = []

        for label in self.stimulusLabelList:
            self.priorProbabilities.append(equiproba)


        self.computedStimCount = 0

    def setPipelineFeedback(self, pipelineFeedback):
        self.pipelineFeedback = pipelineFeedback

    def computeNewProbas(self, computedLikelihoodList):
        finalProbabilities = self.computePosteriorProbabilities(computedLikelihoodList)
        for triggerIndex in range(0, self.triggerCount, 1):
            print("Label : " + self.stimulusLabelList[triggerIndex] + " | " + str(finalProbabilities[triggerIndex]) + "\n")
            self.pipelineFeedback.write("Label : " + self.stimulusLabelList[triggerIndex] + " | " + str(finalProbabilities[triggerIndex]) + "\n")
        return finalProbabilities


    def computePosteriorProbabilities(self, computedLikelyhoodList):
        finalProbabilities = []
        for idx in range(0, self.triggerCount, 1):
            finalProbabilities.append(0.0)

        # self.priorProbabilities = []
        # if(len(self.priorProbabilities == 0)):
        #     equiproba = 1.0/self.triggerCount
        #     for idx in range(0, self.triggerCount, 1):
        #         self.priorProbabilities.append(equiproba)
        #         finalProbabilities.append(0.0)

        for stimulusIndex in range(0, len(self.stimulusLabelList), 1):
            for triggerIndex in range(0, self.triggerCount, 1):
                if (self.priorProbabilities[triggerIndex] == 0.0):
                    self.priorProbabilities[triggerIndex] = sys.float_info.min
                if (self.stimulusLabelList[stimulusIndex] == self.stimulusLabelList[triggerIndex]):
                    finalProbabilities[triggerIndex] = math.log(self.priorProbabilities[triggerIndex]) + \
                                                       computedLikelyhoodList[stimulusIndex][0]
                else:
                    finalProbabilities[triggerIndex] = math.log(self.priorProbabilities[triggerIndex]) + \
                                                       computedLikelyhoodList[stimulusIndex][1]

            maxProba = 0.0
            for proba in finalProbabilities:
                if proba > maxProba:
                    maxProba = proba

            sumProba = 0.0
            for idx in range(0, len(finalProbabilities), 1):
                finalProbabilities[idx] -= maxProba - 1.0
                finalProbabilities[idx] = math.exp(finalProbabilities[idx])
                sumProba += finalProbabilities[idx]

            for idx in range(0, len(finalProbabilities), 1):
                finalProbabilities[idx] /= sumProba
                self.priorProbabilities[idx] = finalProbabilities[idx]

        # Compute Entropie here

        #

        return finalProbabilities
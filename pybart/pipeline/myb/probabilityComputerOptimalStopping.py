import math
import sys

class ProbabilityComputerOptimalStopping:
    def __init__(self, stimulusLabelList, triggerSelectionThreshold, optimalStopping):
        self.stimulusLabelList = stimulusLabelList
        self.triggerCount = len(stimulusLabelList)
        self.triggerSelectionThreshold = triggerSelectionThreshold
        self.maxRepetitionCount = 10  # TODO: need param
        self.optimalStopping = optimalStopping
        print("Max stim count : " + str(self.maxRepetitionCount * self.triggerCount))
        self.reset()

    def reset(self):
        self.flashCount = 0  # Voir ce qu'on fait de cette variable
        self.prior = []
        self.post = []

        self.maxProbability = 0
        self.priorProbabilities = []

        equiproba = 1.0 / self.triggerCount
        self.priorProbabilities = []

        self.passCountDic = {}

        for label in self.stimulusLabelList:
            self.priorProbabilities.append(equiproba)
            self.passCountDic[label] = 0

        self.computedStimCount = 0

    def setPipelineFeedback(self, pipelineFeedback):
        self.pipelineFeedback = pipelineFeedback

    def computeNewProbas(self, computedLikelihood, stimulusLabel):
        finalProbabilities = self.computePosteriorProbabilities(computedLikelihood, stimulusLabel)
        for triggerIndex in range(0, self.triggerCount, 1):
            print("Label : " + self.stimulusLabelList[triggerIndex] + " | " + str(finalProbabilities[triggerIndex]) + "\n")
            self.pipelineFeedback.write("Label : " + self.stimulusLabelList[triggerIndex] + " | " + str(finalProbabilities[triggerIndex]) + "\n")
        if self.optimalStopping:
            return self.selectionPass(finalProbabilities)
        else:
            return finalProbabilities

    def computePosteriorProbabilities(self, computedLikelyhood, stimulusLabel):
        finalProbabilities = []
        for idx in range(0, self.triggerCount, 1):
            finalProbabilities.append(0.0)

        for triggerIndex in range(0, self.triggerCount, 1):
            if(self.priorProbabilities[triggerIndex] == 0.0):
                self.priorProbabilities[triggerIndex] = sys.float_info.min
            if(stimulusLabel == self.stimulusLabelList[triggerIndex]):
                finalProbabilities[triggerIndex] = math.log(self.priorProbabilities[triggerIndex]) + computedLikelyhood[0]
            else:
                finalProbabilities[triggerIndex] = math.log(self.priorProbabilities[triggerIndex]) + computedLikelyhood[1]

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
            # print("final prob " + str(idx) + " : " + str(finalProbabilities[idx]))
            self.priorProbabilities[idx] = finalProbabilities[idx]

        # Compute Entropie here

        #

        self.computedStimCount += 1

        return finalProbabilities

    def selectionPass(self, finalProbabilities):
        isMaxComputedStimCount = self.computedStimCount == self.maxRepetitionCount * self.triggerCount
        #  print("computed : " + str(self.computedStimCount))
        for triggerIndex in range(0, self.triggerCount, 1):
            if finalProbabilities[triggerIndex] < self.triggerSelectionThreshold:
                self.passCountDic[self.stimulusLabelList[triggerIndex]] = 0

        for triggerIndex in range(0, self.triggerCount, 1):
            if finalProbabilities[triggerIndex] >= self.triggerSelectionThreshold and self.passCountDic[self.stimulusLabelList[triggerIndex]] >= 3:
                return self.stimulusLabelList[triggerIndex]

            elif finalProbabilities[triggerIndex] >= self.triggerSelectionThreshold and self.passCountDic[self.stimulusLabelList[triggerIndex]] < 3:
                self.passCountDic[self.stimulusLabelList[triggerIndex]] += 1
                if isMaxComputedStimCount:
                    return self.stimulusLabelList[finalProbabilities.index(max(finalProbabilities))]
                else:
                    return ""

        if isMaxComputedStimCount:
            return self.stimulusLabelList[finalProbabilities.index(max(finalProbabilities))]

        return ""
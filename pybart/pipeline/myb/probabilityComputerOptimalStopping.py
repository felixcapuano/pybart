import math
import sys

class ProbabilityComputerOptimalStopping:
    def __init__(self, stimulusLabelList, triggerSelectionThreshold):
        self.stimulusLabelList = stimulusLabelList
        self.triggerCount = len(stimulusLabelList)
        self.triggerSelectionThreshold = triggerSelectionThreshold
        self.maxRepetitionCount = 10  # TODO: need param
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
            self.pipelineFeedback.write("Label : " + self.stimulusLabelList[triggerIndex] + " | " + str(finalProbabilities[triggerIndex]) + "\n")
        return self.selectionPass(finalProbabilities)

    # def computeNewProbas(self, computedLikelihoodList):
    #     finalProbabilities = self.computePosteriorProbabilities(computedLikelihoodList)
    #     return self.selectionPass(finalProbabilities)

    # def getP300Results(self, p300Data, n):
    #     proba = []
    #
    #     set = False
    #     if(";" in p300Data):
    #         lf_list = p300Data.split(";")
    #         if(len(lf_list) == 2 * n):
    #             for i in range(0, len(lf_list), 2):
    #                 LF0 = 0
    #                 LF1 = 0
    #                 if(self.isfloat(lf_list[i])):
    #                     if(self.isfloat(lf_list[i + 1])):
    #                         LF = [LF0, LF1]
    #                         proba.append(LF)
    #                         set = True
    #         else:
    #             print("ProbaComputer received " + len(lf_list / 2) + " instead of " + n)
    #
    #     if(not set):
    #         print("ProbaComputer received inconsistent data as LF: '" + p300Data + "'. Data dropped")
    #
    #
    #     #Prevent missing data
    #     if(len(proba) < n):
    #         for i in range(len(proba), n, 1):
    #             LF = [0, 0]
    #             proba.append(LF)
    #
    #     #We are done, release used data
    #     p300Data = ""
    #
    #     return proba

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
            if(proba > maxProba):
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


    # def computePosteriorProbabilities(self, computedLikelyhoodList):
    #     finalProbabilities = []
    #
    #     self.priorProbabilities = []
    #     if(len(self.priorProbabilities == 0)):
    #         equiproba = 1.0/self.triggerCount
    #         for idx in range(0, self.triggerCount, 1):
    #             self.priorProbabilities.append(equiproba)
    #             finalProbabilities.append(0.0)
    #
    #     if(len(computedLikelyhoodList) == len(self.stimulusLabelList)):
    #         for stimulusIndex in range(0, len(self.stimulusLabelList), 1):
    #             for triggerIndex in range(0, self.triggerCount, 1):
    #                 if (self.priorProbabilities[triggerIndex] == 0.0):
    #                     self.priorProbabilities[triggerIndex] = sys.float_info.min
    #                 if(self.stimulusLabelList[stimulusIndex] == self.stimulusLabelList[triggerIndex]):
    #                     finalProbabilities[triggerIndex] = math.log(self.priorProbabilities[triggerIndex]) + computedLikelyhoodList[stimulusIndex][0]
    #                 else:
    #                     finalProbabilities[triggerIndex] = math.log(self.priorProbabilities[triggerIndex]) + computedLikelyhoodList[stimulusIndex][1]
    #
    #             maxProba = 0.0
    #             for proba in finalProbabilities:
    #                 if (proba > maxProba):
    #                     maxProba = proba
    #
    #             sumProba = 0.0
    #             for idx in range(0, len(finalProbabilities), 1):
    #                 finalProbabilities[idx] -= maxProba - 1
    #                 finalProbabilities[idx] = math.exp(finalProbabilities[idx])
    #                 sumProba += finalProbabilities[idx]
    #
    #             for idx in range(0, len(finalProbabilities), 1):
    #                 finalProbabilities[idx] /= sumProba
    #                 self.priorProbabilities[idx] = finalProbabilities[idx]
    #
    #     # Compute Entropie here
    #
    #     #
    #
    #     return finalProbabilities

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

    def isfloat(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

import logging
import os

import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal

from ..toolbox.h5file import writeH5FileTemplate
from ..toolbox.covariance import covariances_EP, matCov
from ..toolbox.riemann import distance_riemann, mean_riemann
from ...streamengine import StreamEngine
from .mybsetting import MybSettingDialog

from datetime import datetime

import sys


import scipy.io

from .probabilityComputerOptimalStopping import ProbabilityComputerOptimalStopping


import distutils
from distutils import util

#Todo : Create new file after each calib or game without restarting pipeline

#logger = logging.getLogger(__name__)
#logger.setLevel(logging.INFO)

#formatter = logging.Formatter('%(asctime)s  %(levelname)s (%(name)s) -> %(message)s')

#file_handler = logging.FileHandler(os.environ['USERPROFILE'] + '\AppData\Local\Pybart\log\pipeline.log')
#file_handler.setFormatter(formatter)

#logger.addHandler(file_handler)

class MybPipeline(MybSettingDialog, QObject):
    """Pipe line use to compute epochs to determine the likelihood"""

    dump = pyqtSignal(str)



    def __init__(self, parent, display=None):
        super(MybSettingDialog, self).__init__(parent)
        QObject.__init__(self)

        MybSettingDialog.__init__(self, parent)

        self.running = False
        self.stream_engine = None

        self.tab_gaze = ""
        self.tab_lf = ""
        self.likelihood_computed = 0

        self.allEpochs = []
        self.epochs_T = []
        self.epochs_NT = []

        self.probabilityComputer = None


        if not self.dump == None:
            self.dump.connect(display)

        self.ignoreEpochs = False  # Used to ignore epochs coming after a result

        self.optimalStopping = True

        self.stimulusLabelStringReceived = ""
        np.set_printoptions(threshold=np.inf)
        # filename  = "C:/Users/AlexM/Documents/Projets/Python/pybart/log/Trig-" +  dt_string + ".txt"
        # self.TrigFile = open(filename, "a+")
        self.pipelineFeedback = None
        self.epochTFile = None
        self.epochNTFile = None
        self.gameEpochFile = None

        self.sessionPath = ""






    def start(self, low_frequency, high_frequency, trig_params, brain_amp_device, stream_params):
        """On configure the Steam engine

        - the pass band-frequency
        - the epochs output slot

        Then get the StreamEngine communication inferface (sender) with the myb
        game and reset it.

        """
        self.stream_engine = StreamEngine(**stream_params)

        self.oldLowFrequency = low_frequency
        self.oldHighFrequency = high_frequency
        self.oldStreamParams = stream_params

        self.stream_engine.configuration(low_frequency, high_frequency, trig_params, brain_amp_device)

        self.stream_engine.nodes['epochermultilabel'].new_chunk.connect(self.new_epochs)
        self.stream_engine.start_nodes()
        self.sender = self.stream_engine.nodes["eventpoller"].sender_poller

        self.sender.stop_communicate.connect(self.reset)

        self.sender.helper.resetSignal.connect(self.reset)
        self.sender.helper.resultSignal.connect(self.send_probas)
        self.sender.helper.triggerSetupSignal.connect(self.setupProbabilityComputer)
        self.sender.helper.settingSignal.connect(self.setSettingValue)
        self.sender.helper.startSessionSignal.connect(self.on_game_session_start)
        #self.sender.game_stop.connect(self.reset)


        self.running = True



    def stop(self):
        self.stream_engine.stop_nodes()
        self.stream_engine = None

        self.running = False

        self.closeFiles()

    def closeFiles(self):
        if self.pipelineFeedback is not None:
            self.pipelineFeedback.close()
        if self.epochTFile is not None:
            self.epochTFile.close()
        if self.epochNTFile is not None:
            self.epochNTFile.close()
        if self.gameEpochFile is not None:
            self.gameEpochFile.close()

    def setupProbabilityComputer(self, setupString):
        if setupString != "":
            setupTab = setupString.split(":")
            brainAmpDevice = setupTab[0]
            self.stimulusLabelStringReceived = setupTab[1]
        stimulusLabelList = self.stimulusLabelStringReceived.split(";")

        self.probabilityComputer = ProbabilityComputerOptimalStopping(stimulusLabelList, 0.8, self.optimalStopping)

    def setSettingValue(self, newSettingsValues): # Todo: some setting need a restart of pipeline, see if we can avoid this
        newSettings = newSettingsValues.split(";")
        for setting in newSettings:
            if "optimalStopping" in setting:
                # print("value : " + setting.partition("=")[2])
                self.optimalStopping = bool(distutils.util.strtobool(setting.partition("=")[2]))
                self.probabilityComputer.optimalStopping = self.optimalStopping
                # self.setupProbabilityComputer("")
                self.probabilityComputer.setPipelineFeedback(self.pipelineFeedback)
                print("optimal stopping : " + str(self.optimalStopping))

    def new_epochs(self, label, additionalInformation, epochs): # TODO: create raw data files
        """This function is a slot who classifies epoch according to learning parameters
        and bayes priors for myb games with dynamic bayesian classification
        
        :param label: This is the label of the epochs stack
        :type label: str
        :param epochs: This it a matrix 3d (times*channels*stack)
        :type epochs: numpy.ndarray

        This is the most important part of the class.
        Each stack of epoch build by the StreamEngine 
        arrives here with his label.

        """
        # TEST Visualize epoch compare to mne
        # print(self.counter_epoch)
        # if self.counter_epoch == 30:
        #     self.stream_engine.nodes['epochermultilabel'].new_chunk.disconnect()
        #     epoch = epochs.reshape((epochs.shape[1], epochs.shape[2]))
            
        #     print(epoch.shape)
        #     compare_epoch(epoch, self.counter_epoch)



        #logger.info("Epoch received : {}".format(label))

        # reshaping epoch because epocher send epoch stack who have
        # 3D (time * channel * nb epoch) but this pipeline is build
        # to receive epochs one by one, so `nb epoch` dimension isn't use.
        if not self.ignoreEpochs:

            epoch = epochs.reshape((epochs.shape[1], epochs.shape[2]))
            infoTab = additionalInformation.split(";")
            isLastStr = infoTab[0]
            isTargetStr = infoTab[1]
            isPlayerFocused = infoTab[2]
            if self.sender.calibrationMode:
                # check if label contains "last" tag
                if isPlayerFocused == "True" or isPlayerFocused == "null":
                    # print("process epoch")
                    self.allEpochs.append(epoch)
                    if isTargetStr == "True":
                        self.epochs_T.append(epoch)
                        self.epochTFile.write(str(epoch) + "\r\n \r\n")
                    elif isTargetStr == "False":
                        self.epochs_NT.append(epoch)
                        self.epochNTFile.write(str(epoch) + "\r\n \r\n")
                if isLastStr == "True":
                    self.ComputeCalibration()

            else:
                if isPlayerFocused == "True" or isPlayerFocused == "null":
                    # print("process epoch")
                    self.gameEpochFile.write(str(epoch) + "\r\n \r\n")
                    #print("mu_Epoch_T",self.template_riemann['mu_Epoch_T'])
                    ERP_template_target = self.template_riemann['mu_Epoch_T'][...]

                    self.covmats = covariances_EP(epoch, ERP_template_target)

                    matCov_T = self.template_riemann['mu_MatCov_T'][...]
                    matCov_NT = self.template_riemann['mu_MatCov_NT'][...]

                    curr_r_TNT = self.predict_R_TNT(self.covmats, matCov_T, matCov_NT)

                    mu_rTNT_T = self.template_riemann['mu_rTNT_T'][...]
                    mu_rTNT_NT = self.template_riemann['mu_rTNT_NT'][...]
                    sigma_rTNT_T = self.template_riemann['sigma_rTNT_T'][...]
                    sigma_rTNT_NT = self.template_riemann['sigma_rTNT_NT'][...]

                    likelihood = self.compute_likelihood(curr_r_TNT,
                                                         mu_rTNT_T,
                                                         mu_rTNT_NT,
                                                         sigma_rTNT_T,
                                                         sigma_rTNT_NT)

                    # send likelihood to Myb game using the sender
                    self.likelihood_computed += 1

                    self.process_likelihood(likelihood, label, isLastStr)

                #TODO: Quoi qu'il arrive on enregistre le flash avec ses infos dans le fichier

    def process_likelihood(self, likelihood, label, isLastStr):
        # self.tab_lf += "{0:.6f}".format(float(likelihood[0])) + ";"
        # self.tab_lf += "{0:.6f}".format(float(likelihood[1])) + ";"
        self.pipelineFeedback.write("Label : " + label + " || likelihood[0] : " + str(likelihood[0]) + " | likelihood[1] : " + str(likelihood[1]) + '\n')
        if self.optimalStopping:
            selectedTrigger = self.probabilityComputer.computeNewProbas(likelihood, label)
            if (selectedTrigger is not ""):
                self.sender.socket.send_string(self.sender.RESULT_ZMQ + "|" + selectedTrigger)
                self.ignoreEpochs = True
                self.pipelineFeedback.write("Selected label : " + selectedTrigger + "\n")

        else:
            probas = self.probabilityComputer.computeNewProbas(likelihood, label)
            if isLastStr == "True":
                probaStr = ""
                for i in range(len(probas)):
                    if i == len(probas) - 1:
                        probaStr += str(probas[i])
                    else:
                        probaStr += str(probas[i]) + ";"
                self.sender.socket.send_string(self.sender.RESULT_ZMQ + "|" + probaStr)
                self.ignoreEpochs = True

    def send_probas(self): # todo: delete if not used
        #self.dump.emit("Sending {} results".format(content))

        frame = self.tab_lf[0:-1]

        self.sender.set_result_frame(frame)
        self.reset()

    def _fake_gaze_result(self, nb_flash):
            # building fake gaze result
            TabXY = np.ones(nb_flash * 24) * 800
            for i in range(len(TabXY)):
                self.tab_gaze += "{0:.6f}".format(TabXY[i]) + ";"

    def setting(self):
        """This function is use to configure the pipeline.
        
        Here it just show the the UI setting interface.
        Every needed tools and parameters to configure
        the pipeline are in.
        
        This function is call by the configuration panel,
        when setting button is clicked.
        """
        self.show()

    def on_game_session_start(self, sessionInfo):
        sessionInfoTab = sessionInfo.split(";")
        calibrationModeStr = sessionInfoTab[0]
        sessionPath = sessionInfoTab[1]
        self.sessionPath = sessionPath
        self.sender.calibrationMode = bool(distutils.util.strtobool(calibrationModeStr))
        # self.sender.calibrationMode = calibrationMode
        self.reset()
        self.closeFiles()
        now = datetime.now()
        dt_string = now.strftime("%Y.%m.%d-%H.%M.%S")
        filename = os.environ['USERPROFILE'] + "\Documents\CophyExperimentsData" + sessionPath + "\PybartFeedback\\" + dt_string + ".txt"
        epochTargetFilename = os.environ[
                                       'USERPROFILE'] + "\Documents\CophyExperimentsData" + sessionPath + "\EEGRawData\EpochTarget_" + dt_string + ".txt"
        epochNonTargetFilename = os.environ[
                                          'USERPROFILE'] + "\Documents\CophyExperimentsData" + sessionPath + "\EEGRawData\EpochNonTarget_" + dt_string + ".txt"
        gameEpochFilename = os.environ[
                                     'USERPROFILE'] + "\Documents\CophyExperimentsData" + sessionPath + "\EEGRawData\GameEpoch_" + dt_string + ".txt"

        if self.sender.calibrationMode :
            self.createDirectories(epochTargetFilename)
            self.createDirectories(epochNonTargetFilename)
            self.epochTFile = open(epochTargetFilename, "a+")
            self.epochNTFile = open(epochNonTargetFilename, "a+")
        else:
            self.createDirectories(gameEpochFilename)
            self.createDirectories(filename)
            self.pipelineFeedback = open(filename, "a+")
            self.gameEpochFile = open(gameEpochFilename, "a+")
            if self.probabilityComputer is not None:
                self.probabilityComputer.setPipelineFeedback(self.pipelineFeedback)

    def createDirectories(self, filename):
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

    def reset(self):
        self.tab_gaze = ""
        self.tab_lf = ""
        self.likelihood_computed = 0

        self.allEpochs = []
        self.epochs_T = []
        self.epochs_NT = []

        if self.probabilityComputer is not None:
            self.probabilityComputer.reset()

        self.ignoreEpochs = False
        print("reset")


    def predict_R_TNT(self, X, mu_MatCov_T, mu_MatCov_NT):
        """Predict the r_TNT for a new set of trials."""

        dist_T = distance_riemann(X, mu_MatCov_T)
        dist_NT = distance_riemann(X, mu_MatCov_NT)

        return np.log(dist_T / dist_NT)

    def compute_rTNT(self, MatCov_Trial, mean_MatCov_Target, mean_MatCov_NoTarget):
        All_rTNT = []
        for i, epoch in enumerate(MatCov_Trial):
            dT = distance_riemann(epoch, mean_MatCov_Target)
            dNT = distance_riemann(epoch, mean_MatCov_NoTarget)
            All_rTNT.append(np.log(dT / dNT))

        All_rTNT = np.array(All_rTNT)

        # MOYENNES des rTNT
        Mu_rTNT = np.mean(All_rTNT)

        # Variance des rTNT
        Var_rTNT = np.var(All_rTNT)

        return Mu_rTNT, Var_rTNT, All_rTNT

    def compute_likelihood(self, l_r_TNT,  l_mu_TNT_T, l_mu_TNT_NT, l_sigma_TNT_T, l_sigma_TNT_NT):
        """Compute likelihood value for Target and NoTarget"""
        
        # 0 is target, 1 is nontarget
        Vec_T = (l_r_TNT - l_mu_TNT_T) ** 2
        Vec_T = Vec_T / l_sigma_TNT_T

        Vec_NT = (l_r_TNT - l_mu_TNT_NT) ** 2
        Vec_NT = Vec_NT / l_sigma_TNT_NT

        ld_T = np.log(2 * np. pi * l_sigma_TNT_T)
        ld_NT = np.log(2 * np.pi * l_sigma_TNT_NT)

        lf_T = float(- 0.5 * (Vec_T + ld_T))
        lf_NT = float(- 0.5 * (Vec_NT + ld_NT))
        
        #logger.info('Likelihood computed (Target : {}, No target : {})'.format(lf_T, lf_NT))

        return [lf_T, lf_NT]

    def isRunning(self):
        return self.running

    def ComputeCalibration(self, threshold_rejection=0.1):
        self.allEpochs = np.array(self.allEpochs)
        self.epochs_T = np.array(self.epochs_T)
        self.epochs_NT = np.array(self.epochs_NT)

        absallepochs_maxvalue = np.fabs(self.allEpochs)
        allepochs_maxvalue = absallepochs_maxvalue.max(2).max(1)

        if threshold_rejection > 0:
            reject_above_threshold = np.sort(allepochs_maxvalue)[np.fix(allepochs_maxvalue.size * (1 - threshold_rejection)).astype(np.int)]

        absepochsT_maxvalue = np.fabs(self.epochs_T)
        epochsT_maxvalue = absepochsT_maxvalue.max(2).max(1)

        absepochsNT_maxvalue = np.fabs(self.epochs_NT)
        epochsNT_maxvalue = absepochsNT_maxvalue.max(2).max(1)

        if threshold_rejection > 0:
            epochs_to_remove_indexes = np.where(epochsT_maxvalue > reject_above_threshold)[0]
            epochsT_with_threshold_rejection = np.delete(self.epochs_T, epochs_to_remove_indexes, axis=0)
            epochs_to_remove_indexes = np.where(epochsNT_maxvalue > reject_above_threshold)[0]
            epochsNT_with_threshold_rejection = np.delete(self.epochs_NT, epochs_to_remove_indexes, axis=0)

        else:
            epochs_to_remove_indexes = []
            epochsT_with_threshold_rejection = self.epochs_T
            epochsNT_with_threshold_rejection = self.epochs_NT

        ERP_Template_Target = np.mean(epochsT_with_threshold_rejection, axis=0)
        ERP_Template_NoTarget = np.mean(epochsNT_with_threshold_rejection, axis=0)

        VarERP_Template_Target = np.var(epochsT_with_threshold_rejection, axis=0)
        VarERP_Template_NoTarget = np.var(epochsNT_with_threshold_rejection, axis=0)

        MatCov_TrialTarget = matCov(epochsT_with_threshold_rejection, ERP_Template_Target)
        MatCov_TrialNoTarget = matCov(epochsNT_with_threshold_rejection, ERP_Template_Target)

        MatCov_TrialTarget = np.array(MatCov_TrialTarget)
        MatCov_TrialNoTarget = np.array(MatCov_TrialNoTarget)

        # scipy.io.savemat('D:\Dycog\wip\MatCov_TrialTarget.mat', mdict={'MatCov_TrialTarget': MatCov_TrialTarget})
        # scipy.io.savemat('D:\Dycog\wip\MatCov_TrialNoTarget.mat', mdict={'MatCov_TrialNoTarget': MatCov_TrialNoTarget})

        mean_MatCov_Target = mean_riemann(MatCov_TrialTarget)
        mean_MatCov_NoTarget = mean_riemann(MatCov_TrialNoTarget)
        print("Matcov trial target : ", MatCov_TrialNoTarget.shape)
        print("meanTarget : ", mean_MatCov_Target.shape)
        print("meanNTarget ; ", mean_MatCov_NoTarget.shape)
        # scipy.io.savemat('D:\Dycog\wip\mean_MatCov_Target.mat', mdict={'mean_MatCov_Target': mean_MatCov_Target})
        # scipy.io.savemat('D:\Dycog\wip\mean_MatCov_NoTarget.mat', mdict={'mean_MatCov_NoTarget': mean_MatCov_NoTarget})
        Mu_rTNT_TrialTarget, Var_rTNT_TtrialTarget, All_rTNT_TrialTarget = self.compute_rTNT(MatCov_TrialTarget,
                                                                                                    mean_MatCov_Target,
                                                                                                    mean_MatCov_NoTarget)
        Mu_rTNT_TrialNoTarget, Var_rTNT_TrialNoTarget, All_rTNT_TrialNoTarget = self.compute_rTNT(
            MatCov_TrialNoTarget, mean_MatCov_Target, mean_MatCov_NoTarget)
        NbGoodTarget = float(np.sum(All_rTNT_TrialTarget < .0))
        NbGoodNoTarget = float(np.sum(All_rTNT_TrialNoTarget > .0))
        NbTotTrials = float(All_rTNT_TrialTarget.shape[0] + All_rTNT_TrialNoTarget.shape[0])
        AccP300 = np.float64((NbGoodTarget + NbGoodNoTarget) * 100 / NbTotTrials)

        TemplateRiemann = {}
        TemplateRiemann['mu_Epoch_T'] = ERP_Template_Target
        TemplateRiemann['mu_Epoch_NT'] = ERP_Template_NoTarget
        TemplateRiemann['var_Epoch_T'] = VarERP_Template_Target
        TemplateRiemann['var_Epoch_NT'] = VarERP_Template_NoTarget
        TemplateRiemann['mu_MatCov_T'] = mean_MatCov_Target
        TemplateRiemann['mu_MatCov_NT'] = mean_MatCov_NoTarget
        TemplateRiemann['mu_rTNT_T'] = Mu_rTNT_TrialTarget
        TemplateRiemann['mu_rTNT_NT'] = Mu_rTNT_TrialNoTarget
        TemplateRiemann['sigma_rTNT_T'] = Var_rTNT_TtrialTarget
        TemplateRiemann['sigma_rTNT_NT'] = Var_rTNT_TrialNoTarget
        TemplateRiemann['AccP300'] = AccP300

        now = datetime.now()
        dt_string = now.strftime("%Y.%m.%d-%H.%M.%S")
        #fileTemplateName = "C:/Users/AlexM/Documents/Projets/Python/pybart/TemplateRiemann/template.h5"
        #copyFileTemplateName = "C:/Users/AlexM/Documents/Projets/Python/pybart/TemplateRiemann/template_" + dt_string + ".h5"



        fileTemplateName = os.environ['USERPROFILE'] + "\Documents\CophyExperimentsData\TemplateRiemann\\template.h5"
        copyFileTemplateName = os.environ['USERPROFILE'] + "\Documents\CophyExperimentsData" + self.sessionPath + "\TemplateRiemann\\template_" + dt_string + ".h5"
        self.createDirectories(copyFileTemplateName)
        MybSettingDialog.close_template(self)
        writeH5FileTemplate(TemplateRiemann, fileTemplateName)
        writeH5FileTemplate(TemplateRiemann, copyFileTemplateName)
        MybSettingDialog.load_template(self)
        self.reset() # Calibration goes to False thanks to this reset

        self.sender.socket.send_string(self.sender.CALIBRATION_CHECK_ZMQ + "|")
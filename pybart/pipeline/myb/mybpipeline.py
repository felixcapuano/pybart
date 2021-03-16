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

        if not self.dump == None:
            self.dump.connect(display)



    def start(self, low_frequency, high_frequency, trig_params, stream_params):
        """On configure the Steam engine

        - the pass band-frequency
        - the epochs output slot
        
        Then get the StreamEngine communication inferface (sender) with the myb
        game and reset it.

        """
        self.stream_engine = StreamEngine(**stream_params)
        
        self.stream_engine.configuration(low_frequency, high_frequency, trig_params)

        self.stream_engine.nodes['epochermultilabel'].new_chunk.connect(self.new_epochs)
        self.stream_engine.start_nodes()
        self.sender = self.stream_engine.nodes["eventpoller"].sender_poller

        self.sender.stop_communicate.connect(self.reset)

        self.sender.helper.resetSignal.connect(self.reset)
        self.sender.helper.resultSignal.connect(self.send_likelihood_result)
        #self.sender.game_stop.connect(self.reset)

        self.running = True
    def stop(self):
        self.stream_engine.stop_nodes()
        self.stream_engine = None

        self.running = False

    def new_epochs(self, label, epochs):
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
        epoch = epochs.reshape((epochs.shape[1], epochs.shape[2]))


        if self.sender.calibrationMode:
            self.allEpochs.append(epoch)
            if label == "S  2":
                self.epochs_T.append(epoch)
            elif label == "S  1":
                self.epochs_NT.append(epoch)
            elif label == "S  4":
                self.epochs_T.append(epoch)
                self.ComputeCalibration()
            elif label == "S  3":
                self.epochs_NT.append(epoch)
                self.ComputeCalibration()


        else:
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
            self.send_likelihood(likelihood, label)


    def send_likelihood(self, likelihood, label):
        self.tab_lf += "{0:.6f}".format(float(likelihood[0])) + ";"
        self.tab_lf += "{0:.6f}".format(float(likelihood[1])) + ";"
        
        if self.sender.isConnected:
            self.dump.emit("Epoch processed (id = {})".format(label))
            
            request, content = self.sender.get_request()

            sys.stdout.write("## Message for Unity game : LikelihoodComputedCount --" + str(self.likelihood_computed) + "-- ## \n"); sys.stdout.flush()  # Don't delete this message -> it's read by Unity

            #print("\ncontent : ", content)
            #print("likelihood_computed : ", self.likelihood_computed)
            #if(request == self.sender.RESULT_ZMQ and content == str(self.likelihood_computed)):
                
                #self.dump.emit("Sending {} results".format(content))
                ###
                #Old version :

                #self._fake_gaze_result(int(content))
                #frame = self.tab_gaze[0:-1] + '|' + self.tab_lf[0:-1]
                ###
                #frame = self.tab_lf[0:-1]

                
                #self.sender.set_result_frame(frame)
                #self.reset()
        else:
            self.likelihood_computed = 0
            self.dump.emit("Disconnected")

    def send_likelihood_result(self):
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
        
    def reset(self, calibrationMode=False):
        print("reset")
        print(calibrationMode)
        self.sender.calibrationMode = calibrationMode
        self.tab_gaze = ""
        self.tab_lf = ""
        self.likelihood_computed = 0

        self.allEpochs = []
        self.epochs_T = []
        self.epochs_NT = []

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
        allepochs_maxvalue = absallepochs_maxvalue.max(2).max(0)

        if threshold_rejection > 0:
            reject_above_threshold = np.sort(allepochs_maxvalue)[np.fix(allepochs_maxvalue.size * (1 - threshold_rejection)).astype(np.int)]

        absepochsT_maxvalue = np.fabs(self.epochs_T)
        epochsT_maxvalue = absepochsT_maxvalue.max(2).max(0)

        absepochsNT_maxvalue = np.fabs(self.epochs_NT)
        epochsNT_maxvalue = absepochsNT_maxvalue.max(2).max(0)

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



        fileTemplateName = os.environ['USERPROFILE'] + "\Documents\PybartData\TemplateRiemann\\template.h5"
        copyFileTemplateName = os.environ['USERPROFILE'] + "\Documents\PybartData\TemplateRiemann\\template_" + dt_string + ".h5"
        MybSettingDialog.close_template(self)
        writeH5FileTemplate(TemplateRiemann, fileTemplateName)
        writeH5FileTemplate(TemplateRiemann, copyFileTemplateName)
        MybSettingDialog.load_template(self)
        self.reset() # Calibration goes to False thanks to this reset

        sys.stdout.write("## Message for Unity game : CalibrationResult ready ## \n"); sys.stdout.flush()  # Don't delete this message -> it's read by Unity

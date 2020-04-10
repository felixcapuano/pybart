import logging
import os

import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal

from ..toolbox.covariance import covariances_EP
from ..toolbox.riemann import distance_riemann
from ...streamengine import StreamEngine
from .mybsetting import MybSettingDialog


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s  %(levelname)s (%(name)s) -> %(message)s')

file_handler = logging.FileHandler('log\\pipeline.log')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

class MybPipeline(MybSettingDialog, QObject):
    """Pipe line use to compute epochs to determine the likelihood"""

    dump = pyqtSignal(str)

    def __init__(self, parent, display=None):
        super(MybSettingDialog, self).__init__(parent)
        QObject.__init__(self)

        MybSettingDialog.__init__(self, parent)

        self.running = False
        self.stream_engine = None
        self.reset()

        if not self.dump == None:
            self.dump.connect(display)

    def start(self, low_frequency, high_frequency, trig_params, stream_params):

        self.stream_engine = StreamEngine(**stream_params)
        
        self.stream_engine.configuration(low_frequency, high_frequency, trig_params)

        self.stream_engine.nodes['epochermultilabel'].new_chunk.connect(self.new_epochs)
        self.stream_engine.start_nodes()
        self.sender = self.stream_engine.nodes["eventpoller"]

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

        logger.info("Epoch received : {}".format(label))
        self.dump.emit("Epoch received (id = {})".format(label))

        # reshaping epoch because epocher send epoch stack who have 
        # 3D (time * channel * nb epoch) but this pipeline is build
        # to receive epochs one by one, so `nb epoch` dimension isn't use.
        epoch = epochs.reshape((epochs.shape[1], epochs.shape[2]))

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
        self.send_likelihood(likelihood)        

    def send_likelihood(self, likelihood):
        self.tab_lf += "{0:.6f}".format(float(likelihood[0])) + ";"
        self.tab_lf += "{0:.6f}".format(float(likelihood[1])) + ";"
        
        # TODO get flags of EventPollerThread
        request, content = self.sender.get_current_request()
        if(request == "4" and content == str(self.likelihood_computed)):
            self.dump.emit("Sending result")

            self._fake_gaze_result(int(content))

            frame = self.tab_gaze[0:-1] + '|' + self.tab_lf[0:-1]
            self.sender.send_result(frame)
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
        
    def reset(self):
        self.tab_gaze = ""
        self.tab_lf = ""
        self.likelihood_computed = 0

    def predict_R_TNT(self, X, mu_MatCov_T, mu_MatCov_NT):
        """Predict the r_TNT for a new set of trials."""

        dist_T = distance_riemann(X, mu_MatCov_T)
        dist_NT = distance_riemann(X, mu_MatCov_NT)

        return np.log(dist_T / dist_NT)

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
        
        logger.info('Likelihood computed (Target : {}, No target : {})'.format(lf_T, lf_NT))

        return [lf_T, lf_NT]

    def isRunning(self):
        return self.running

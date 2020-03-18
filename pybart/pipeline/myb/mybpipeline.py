import logging
import os

import numpy as np

from ..toolbox.covariance import covariances_EP
from ..toolbox.riemann import distance_riemann
from .mybsender import MybLikelihoodSender
from .mybsetting import MybSettingDialog


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s  %(levelname)s (%(name)s) -> %(message)s')

file_handler = logging.FileHandler('log\\pipeline.log')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

class MybPipeline(MybSettingDialog, MybLikelihoodSender):
    """Pipe line use to compute epochs to determine the likelihood"""

    def __init__(self, parent):
        super(MybSettingDialog, self).__init__(parent)

        MybSettingDialog.__init__(self, parent)
        MybLikelihoodSender.__init__(self)

  
    def new_epochs(self, label, epochs):
        """This function is a slot who classifies epoch according to learning parameters
        and bayes priors for myb games with dynamic bayesian classification

        """
        logger.info("Epoch received : {}".format(label))

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
        self.send_new_likelihood(likelihood)        

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
        self.reset_sender()

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

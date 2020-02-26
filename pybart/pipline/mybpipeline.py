import h5py
import numpy as np
import zmq
from pyqtgraph.Qt import QtCore
from scipy.linalg import eigvalsh

from pipline.toolbox.riemann import distance_riemann
from pipline.toolbox.covariance import covariances_EP

class MybPipeline(QtCore.QObject):  # inherits QObject to send signals

    sig_new_likelihood = QtCore.pyqtSignal(np.ndarray)

    def __init__(self, parent=None):
        QtCore.QObject.__init__(self, parent)

        # Default setting
        self.template_path = "TemplateRiemann/Template.h5"
        self.init_template()

        self.sig_new_likelihood.connect(self.on_new_likelihood)

        self._init_zmq_pub()

    def set_template_name(self, template_path):
        self.template_path = template_path

    def init_template(self):
        self._init_Template_Riemann(self.template_path)

    def _init_zmq_pub(self):
        self.context_pub = zmq.Context()
        self.zmq_pub = self.context_pub.socket(zmq.REP)    
        self.zmq_pub.bind('tcp://127.0.0.1:5555')  
        
        self.reset()

    
    def _init_Template_Riemann(self, Template_H5Filename):
        self.f = h5py.File(Template_H5Filename, 'r')

        self.dict = {}
        for element in self.f:
            groupe = self.f[element]

            for element in groupe:
                self.dict[element] = groupe[element]

        self.TemplateRiemann = self.dict

    def new_epochs_classifier(self, label, epochs):
        """This function is a slot who classifies epoch according to learning parameters
        and bayes priors for myb games with dynamic bayesian classification

        """
        epoch = epochs.reshape((epochs.shape[1], epochs.shape[2]))

        ERP_template_target = self.TemplateRiemann['mu_Epoch_T'][...]

        self.covmats = self.covariances_EP(epoch, ERP_template_target)

        matCov_T = self.TemplateRiemann['mu_MatCov_T'][...]
        matCov_NT = self.TemplateRiemann['mu_MatCov_NT'][...]

        curr_r_TNT = self.predict_R_TNT(self.covmats, matCov_T, matCov_NT)

        mu_rTNT_T = self.TemplateRiemann['mu_rTNT_T'][...]
        mu_rTNT_NT = self.TemplateRiemann['mu_rTNT_NT'][...]
        sigma_rTNT_T = self.TemplateRiemann['sigma_rTNT_T'][...]
        sigma_rTNT_NT = self.TemplateRiemann['sigma_rTNT_NT'][...]

        likelihood = self.compute_likelihood(curr_r_TNT,
                                             mu_rTNT_T,
                                             mu_rTNT_NT,
                                             sigma_rTNT_T,
                                             sigma_rTNT_NT)
        print(likelihood)
        self.sig_new_likelihood.emit(likelihood)

    def predict_R_TNT(self, X, mu_MatCov_T, mu_MatCov_NT):
        """Predict the r_TNT for a new set of trials."""

        dist_T = self.distance_riemann(X, mu_MatCov_T)
        dist_NT = self.distance_riemann(X, mu_MatCov_NT)

        return np.log(dist_T / dist_NT)

    def compute_likelihood(self, l_r_TNT,  l_mu_TNT_T, l_mu_TNT_NT, l_sigma_TNT_T, l_sigma_TNT_NT):

        # 0 is target, 1 is nontarget

        Vec0 = (l_r_TNT - l_mu_TNT_T) ** 2
        Vec0 = Vec0 / l_sigma_TNT_T

        Vec1 = (l_r_TNT - l_mu_TNT_NT) ** 2
        Vec1 = Vec1 / l_sigma_TNT_NT

        ld0 = np.log(2 * np. pi * l_sigma_TNT_T)
        ld1 = np.log(2 * np.pi * l_sigma_TNT_NT)

        lf0 = - 0.5 * (Vec0 + ld0)
        lf1 = - 0.5 * (Vec1 + ld1)

        return np.array([lf0, lf1])




    @QtCore.pyqtSlot(np.ndarray)
    def on_new_likelihood(self, likelihood):
        """Within a QtSlot function, use sender() method returns a ref on signal sender instance object (the object connected to this slot).
        this way, we can have a single slot function (callback function) for several objects. 
        (both player1 and player2's signal_new_classifier_result are connected to this slot)

        """

        # sender = self.sender()

        self.tab_lf = self.tab_lf + "{0:.6f}".format(float(likelihood[0])) + ";"
        self.tab_lf = self.tab_lf + "{0:.6f}".format(float(likelihood[1])) + ";"
        self.count_epoch = self.count_epoch + 1


        try:
            self.message = self.zmq_pub.recv(flags=zmq.NOBLOCK)

            if (int(self.message) > 0 and int(self.message) < 120):
                self.nb_flash = int(self.message)
                self.message = ""

        except zmq.ZMQError:
            self.message = ""


        print(".count_epoch {} :: .nb_flash {}".format( self.count_epoch, self.nb_flash))
        if ((self.nb_flash > 0) and (self.count_epoch == self.nb_flash)):

            TabXY = np.ones(self.nb_flash*24)*800
            self.tab_gaze = ""
            for i in range(len(TabXY)):
                self.tab_gaze = self.tab_gaze + "{0:.6f}".format(TabXY[i]) + ";"

            MSGRES = self.zmq_pub.send_string(self.tab_gaze[0:-1] + '|' + self.tab_lf[0:-1])
            
            print('Send to unity (EEG Epoch) :', MSGRES)
            
            self.reset()

    def reset(self):
        self.tab_gaze = ""
        self.tab_lf = ""
        self.count_epoch = 0
        self.nb_flash = 0

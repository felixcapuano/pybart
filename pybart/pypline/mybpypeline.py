import h5py
import numpy as np
import zmq
from pyqtgraph.Qt import QtCore
from scipy.linalg import eigvalsh


class MybPypeline(QtCore.QObject):  # inherits QObject to send signals

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

    def covariances_EP(self, X, P):
        """
        Covariances between two matrix
        """
        return np.cov(np.concatenate((X, P), axis=0))

    def predict_R_TNT(self, X, mu_MatCov_T, mu_MatCov_NT):
        """
        Predict the r_TNT for a new set of trials.
        """

        dist_T = self.distance_riemann(X, mu_MatCov_T)
        dist_NT = self.distance_riemann(X, mu_MatCov_NT)

        return np.log(dist_T / dist_NT)

    def distance_riemann(self, A, B):
        """Riemannian distance between two covariance matrices A and B.
        .. math::
                d = {\left( \sum_i \log(\lambda_i)^2 \\right)}^{-1/2}
        where :math:`\lambda_i` are the joint eigenvalues of A and B
        :param A: First covariance matrix
        :param B: Second covariance matrix
        :returns: Riemannian distance between A and B
        """
        return np.sqrt((np.log(eigvalsh(A, B))**2).sum())

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

    def _init_Template_Riemann(self, Template_H5Filename):

        self.f = h5py.File(Template_H5Filename, 'r')

        print('## Lecture du fichier {}'.format(Template_H5Filename))

        self.dict = {}
        for element in self.f:
            groupe = self.f[element]

            for element in groupe:
                self.dict[element] = groupe[element]

        self.TemplateRiemann = self.dict

    def _init_zmq_pub(self):
    
        self.context_pub = zmq.Context()
        self.zmq_pub = self.context_pub.socket(zmq.REP)    
        self.zmq_pub.bind('tcp://127.0.0.1:5555')  
        
        self.TabLF = ""
        self.NbFlashs = 0
        self.CountEpoch = 0

    @QtCore.pyqtSlot(np.ndarray)
    def on_new_likelihood(self, Likelihood):
        """
        within a QtSlot function, use sender() method returns a ref on signal sender instance object (the object connected to this slot).
        this way, we can have a single slot function (callback function) for several objects. 
        (both player1 and player2's signal_new_classifier_result are connected to this slot)

        """

        sender = self.sender()

        self.player0_Likelihood = Likelihood
#        LikelihoodCurr =  "{0:.6f}".format(float(self.player0_Likelihood[0])) + "\t" +  "{0:.6f}".format(float(self.player0_Likelihood[1])) + "\n"

        self.TabLF = self.TabLF + \
            "{0:.6f}".format(float(self.player0_Likelihood[0])) + ";"
        self.TabLF = self.TabLF + \
            "{0:.6f}".format(float(self.player0_Likelihood[1])) + ";"

        self.CountEpoch = self.CountEpoch + 1

#        print(".CountEpoch",self.CountEpoch)

        try:
            self.message = self.zmq_pub.recv(flags=zmq.NOBLOCK)
            print("Message Received EEG Epoch  ", self.message)
            print("CountEpoch current  ", self.CountEpoch)

            if (int(self.message) > 0 and int(self.message) < 120):
                self.NbFlashs = int(self.message)
                self.message = ""

        except zmq.ZMQError:
            self.message = ""

        if ((self.NbFlashs > 0) and (self.CountEpoch == self.NbFlashs)):

            #            print('           ----------------               Send to unity (EEG Epoch)')
            TabXY = np.ones(self.NbFlashs*24)*800
            self.TabGaze = ""
            for i in range(len(TabXY)):
                self.TabGaze = self.TabGaze + "{0:.6f}".format(TabXY[i]) + ";"

            # MSGRES = self.zmq_pub.send('100;100;100;100;100;100;100;100;100;100;100;100;100;100;100;100;100;100;100;100;100;100;100;100;100;100;100;100;100;100' + '|' + self.TabLF[0:-1])
            MSGRES = self.zmq_pub.send(self.TabGaze[0:-1] + '|' + self.TabLF[0:-1])
            
            print('Send to unity (EEG Epoch) :', MSGRES)
            
            self.TabGaze = ""
            self.TabLF = ""
            self.CountEpoch = 0
            self.NbFlashs = 0

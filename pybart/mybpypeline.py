from pyqtgraph.Qt import QtCore
from scipy.linalg import eigvalsh
import numpy as np

class MybPypeline(QtCore.QObject): #inherits QObject to send signals

    signal_new_likelihoodFunction_result = QtCore.pyqtSignal(np.ndarray)
    
    def __init__(self, parent=None):
            self.setupUI(self)
    
    def on_new_epochs(self, label, epoch):
            """
            classifies new ERP according to learning parameters and bayes priors for connect_four with dynamic bayesian classification
            """
            #find the epoch data corresonding to this label.
            # TODO type a matix?????
            label_new_erp = self._multi_epoch_EEG.means_by_labels[label]
            


            ERP_template_target = self.TemplateRiemann['mu_Epoch_T'][...]

            self.covmats = self.covariances_EP(label_new_erp, ERP_template_target)


            matCov_T = self.TemplateRiemann['mu_MatCov_T'][...]
            matCov_NT = self.TemplateRiemann['mu_MatCov_NT'][...]
            
            curr_r_TNT = self.predict_R_TNT(self.covmats, matCov_T, matCov_NT)        
            

            mu_rTNT_T  = self.TemplateRiemann['mu_rTNT_T'][...]
            mu_rTNT_NT = self.TemplateRiemann['mu_rTNT_NT'][...]
            sigma_rTNT_T  = self.TemplateRiemann['sigma_rTNT_T'][...]
            sigma_rTNT_NT = self.TemplateRiemann['sigma_rTNT_NT'][...]
            
            likelihoodFunction = self.compute_likelihood(curr_r_TNT, mu_rTNT_T, mu_rTNT_NT, sigma_rTNT_T, sigma_rTNT_NT)



            self.signal_new_likelihoodFunction_result.emit(likelihoodFunction)

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
        
    def distance_riemann(self,A, B):
        """Riemannian distance between two covariance matrices A and B.
        .. math::
        d = {\left( \sum_i \log(\lambda_i)^2 \\right)}^{-1/2}
    		
        where :math:`\lambda_i` are the joint eigenvalues of A and B
    		
        :param A: First covariance matrix
        :param B: Second covariance matrix
        :returns: Riemannian distance between A and B
    		
        """
        l_logsquare = np.sum(np.log(eigvalsh(A, B))**2)

        return np.sqrt(l_logsquare)

    def compute_likelihood(self, l_r_TNT,  l_mu_TNT_T, l_mu_TNT_NT, l_sigma_TNT_T, l_sigma_TNT_NT):
        """
        likelihood????????????????????????????????????????????????
        """

		# 0 is target, 1 is nontarget
		
        Vec0 = (l_r_TNT - l_mu_TNT_T) ** 2
        Vec0 = Vec0 / l_sigma_TNT_T
		
        Vec1 = (l_r_TNT - l_mu_TNT_NT) ** 2
        Vec1 = Vec1 / l_sigma_TNT_NT
		
		
        ld0 = np.log( 2 *np. pi *l_sigma_TNT_T)
        ld1 = np.log(2 * np.pi * l_sigma_TNT_NT)
		
		
        lf0 = - 0.5 * (Vec0 + ld0)
        lf1 = - 0.5 * (Vec1 + ld1)
		

        return np.array([lf0 , lf1])   
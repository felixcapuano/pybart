from pyqtgraph.Qt import QtCore
import numpy as np

class MybPypeline(QtCore.QObject): #inherits QObject to send signals

    signal_new_likelihoodFunction_result = QtCore.pyqtSignal(np.ndarray)
    
    def __init__(self, parent=None):
            QtCore.QObject.__init__(self, parent)
    
    def on_new_chunk(self, label):
            """
            classifies new ERP according to learning parameters and bayes priors for connect_four with dynamic bayesian classification
            """
            #find the epoch data corresonding to this label.
            label_new_erp = self._multi_epoch_EEG.means_by_labels[label]
            
            self.ERP_Template_Target = self.TemplateRiemann['mu_Epoch_T'][...]

            self.CurrCov = self.covariances_EP(label_new_erp, self.ERP_Template_Target)


        #     scipy.io.savemat('D:\Dycog\Dev_Python\ERP_Template_Target.mat', mdict={'ERP_Template_Target': self.ERP_Template_Target })
        #     scipy.io.savemat('D:\Dycog\Dev_Python\label_new_erp.mat', mdict={'label_new_erp': label_new_erp })
        #     scipy.io.savemat('D:\Dycog\Dev_Python\CurrCov.mat', mdict={'CurrCov': self.CurrCov })        
            
            
            MatCov_T = self.TemplateRiemann['mu_MatCov_T'][...]
            MatCov_NT = self.TemplateRiemann['mu_MatCov_NT'][...]
            
            
        #     scipy.io.savemat('D:\Dycog\Dev_Python\MatCov_T.mat', mdict={'MatCov_T': MatCov_T })        
        #     scipy.io.savemat('D:\Dycog\Dev_Python\MatCov_NT.mat', mdict={'MatCov_NT': MatCov_NT })        
        
            
            self.Curr_r_TNT = self.predict_R_TNT(self.CurrCov, MatCov_T,MatCov_NT)
            
        #     scipy.io.savemat('D:\Dycog\Dev_Python\Curr_r_TNT.mat', mdict={'Curr_r_TNT': self.Curr_r_TNT })        
        
            
            mu_rTNT_T  = self.TemplateRiemann['mu_rTNT_T'][...]
            mu_rTNT_NT = self.TemplateRiemann['mu_rTNT_NT'][...]
            sigma_rTNT_T  = self.TemplateRiemann['sigma_rTNT_T'][...]
            sigma_rTNT_NT = self.TemplateRiemann['sigma_rTNT_NT'][...]
            

            likelihoodFunction = self.compute_likelihood(self.Curr_r_TNT, mu_rTNT_T, mu_rTNT_NT,sigma_rTNT_T,sigma_rTNT_NT)
        #     scipy.io.savemat('D:\Dycog\Dev_Python\LikelihoodFunction.mat', mdict={'LikelihoodFunction': LikelihoodFunction })        

            self.signal_new_likelihoodFunction_result.emit(likelihoodFunction)
            self._multi_epoch_EEG.global_reset_trial()

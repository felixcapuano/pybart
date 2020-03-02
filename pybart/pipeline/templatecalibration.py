import mne
import numpy as np
import scipy
import matplotlib.pyplot as plt

from .toolbox.covariance import matCov
from .toolbox.riemann import mean_riemann
from .toolbox.varioustools import compute_rTNT


def riemann_template_learn(file_complete_path):
    """This function is generating a riemann template.

    It take one .vhdr path in argument and return
    a dict containing all calibration data.

    Riemann template is use to calibrate the MYB game.
    """

    # reading the raw brainvison file .vhdr
    raw = mne.io.read_raw_brainvision(file_complete_path, preload=True, verbose=False)

    # deleting the first market(unused)
    raw.annotations.delete(0)

    # converting annotations from the raw to events for epoching
    raw_events, raw_events_id = mne.events_from_annotations(raw, verbose=False)

    # applying a filter TODO  Need to be approved
    iir_params = dict(order=2, ftype='butter', output='sos')  
    iir_params = mne.filter.construct_iir_filter(iir_params, f_pass=[.5, 20], sfreq=raw.info['sfreq'], btype='bandpass', verbose=False) 
    raw_filtered = raw.filter(None, None, iir_params=iir_params, method='iir')

    # epoching
    epochs = mne.Epochs(raw_filtered, raw_events, raw_events_id,
                            tmin=0.001, tmax=0.600,
                            baseline=None,
                            reject_by_annotation=False, 
                            preload=True, verbose=False)

    # setting of the calibration sequence
    calib_target_sequence = [7, 4, 2, 6, 3, 1, 5, 1, 4, 3, 7, 6, 2, 5, 2, 5, 7, 1, 6, 3, 4]

    # marking the targeted events
    raw_events_targeted = marking_target_events(raw_events, calib_target_sequence)

    # get index of epochs above threshold
    epochs_to_remove = get_index_reject_epochs(epochs=epochs, rejection_rate=0.1)

    # removing epochs and events to get thresholded data
    epochs.drop(epochs_to_remove)
    raw_events_thresholded = np.delete(raw_events_targeted, epochs_to_remove, axis=0)

    epochs_T = []
    epochs_NT = []

    # browse all epochs
    for index_epoch, epoch in enumerate(epochs):

        # check if the epoch is targeted
        # and add it to the corresponding list
        if raw_events_thresholded[index_epoch][1] == 1:
            epochs_T.append(epoch)
        else:
            epochs_NT.append(epoch)

    epochs_T = np.array(epochs_T)
    epochs_NT = np.array(epochs_NT)
    
    ERP_Template_Target = np.mean(epochs_T, axis=0)
    plt.plot(ERP_Template_Target[0,:])
    return
    ERP_Template_NoTarget = np.mean(epochs_NT, axis=0)

    VarERP_Template_Target = np.var(epochs_T, axis=0)
    VarERP_Template_NoTarget = np.var(epochs_NT, axis=0)

    MatCov_TrialTarget = matCov(epochs_T, ERP_Template_Target)
    MatCov_TrialNoTarget = matCov(epochs_NT, ERP_Template_Target)

    MatCov_TrialTarget = np.array(MatCov_TrialTarget)
    MatCov_TrialNoTarget = np.array(MatCov_TrialNoTarget)

    # mean logm
    mean_MatCov_Target = mean_riemann(MatCov_TrialTarget)
    mean_MatCov_NoTarget = mean_riemann(MatCov_TrialNoTarget)

    Mu_rTNT_TrialTarget,  Var_rTNT_TtrialTarget, All_rTNT_TrialTarget = compute_rTNT(MatCov_TrialTarget, mean_MatCov_Target, mean_MatCov_NoTarget)
    Mu_rTNT_TrialNoTarget, Var_rTNT_TrialNoTarget, All_rTNT_TrialNoTarget = compute_rTNT(MatCov_TrialNoTarget, mean_MatCov_Target, mean_MatCov_NoTarget)

    NbGoodTarget = float(np.sum(All_rTNT_TrialTarget < .0))
    NbGoodNoTarget = float(np.sum(All_rTNT_TrialNoTarget > .0))
    NbTotTrials = float(All_rTNT_TrialTarget.shape[0] + All_rTNT_TrialNoTarget.shape[0])

    AccP300 = np.float64((NbGoodTarget+NbGoodNoTarget)*100 / NbTotTrials)

    riemann_template = {}
    riemann_template['mu_Epoch_T'] = ERP_Template_Target
    print('ERP_Template_Target',ERP_Template_Target.shape)
    riemann_template['mu_Epoch_NT'] = ERP_Template_NoTarget
    print('ERP_Template_NoTarget',ERP_Template_NoTarget.shape)
    riemann_template['var_Epoch_T'] = VarERP_Template_Target
    print('VarERP_Template_Target',VarERP_Template_Target.shape)
    riemann_template['var_Epoch_NT'] = VarERP_Template_NoTarget
    print('VarERP_Template_NoTarget',VarERP_Template_NoTarget.shape)
    riemann_template['mu_MatCov_T'] = mean_MatCov_Target
    print('mean_MatCov_Target',mean_MatCov_Target.shape)
    riemann_template['mu_MatCov_NT'] = mean_MatCov_NoTarget
    print('mean_MatCov_NoTarget',mean_MatCov_NoTarget.shape)
    riemann_template['mu_rTNT_T'] = Mu_rTNT_TrialTarget
    print('Mu_rTNT_TrialTarget',Mu_rTNT_TrialTarget)
    riemann_template['mu_rTNT_NT'] = Mu_rTNT_TrialNoTarget
    print('Mu_rTNT_TrialNoTarget',Mu_rTNT_TrialNoTarget)
    riemann_template['sigma_rTNT_T'] = Var_rTNT_TtrialTarget
    print('Var_rTNT_TtrialTarget',Var_rTNT_TtrialTarget)
    riemann_template['sigma_rTNT_NT'] = Var_rTNT_TrialNoTarget
    print('Var_rTNT_TrialNoTarget',Var_rTNT_TrialNoTarget)
    riemann_template['AccP300'] = AccP300
    print('AccP300',AccP300)

    # np.savetxt("dump/mean_MatCov_Target.txt", mean_MatCov_Target, fmt='%8.1e')
    # np.savetxt("dump/mean_MatCov_NoTarget.txt", mean_MatCov_NoTarget, fmt='%8.1e')

    # np.savetxt("dump/ERP_Template_Target.txt", ERP_Template_Target, fmt='%8.1e')
    # np.savetxt("dump/ERP_Template_NoTarget.txt", ERP_Template_NoTarget, fmt='%8.1e')

    return riemann_template


def marking_target_events(raw_events, sequence_target):
    """This function marks targeted events thanks to a list of index"""

    # calculate the number of flash per sequence
    flash_per_sequence = len(raw_events) / len(sequence_target)

    # browse all events
    # index_event browse event
    # index_target browse target
    index_event, index_target = 0, 0
    for pos, is_target, label in raw_events:

        # set a marker when the target is equal to the event label
        if sequence_target[index_target] == label:
            raw_events[index_event][1] = 1

        # incrementing event counter
        index_event += 1

        # incrementing target counter per sequence
        if index_event % flash_per_sequence == 0:
            index_target += 1

    return raw_events


def get_index_reject_epochs(epochs, rejection_rate):
    """This function removes Epochs from the Mne.Epochs object according a rate"""

    # get raw data from the epochs
    data = epochs.get_data()

    # apply absolute value on data
    epochs_absvalue = np.fabs(data)

    # get maximum value per epochs
    epochs_maxvalue = epochs_absvalue.max(2).max(1)

    # calculate the number of epochs that should be rejected
    nb_keeped_epochs_no_rounded = epochs_maxvalue.size*(1-rejection_rate)
    nb_keeped_epochs = np.fix(nb_keeped_epochs_no_rounded).astype(np.int)

    # sort epochs then get the threshold
    threshold = np.sort(epochs_maxvalue)[nb_keeped_epochs]

    # create list of index who have epochs above threshold
    epochs_to_remove = np.where(epochs_maxvalue > threshold)[0]

    return epochs_to_remove

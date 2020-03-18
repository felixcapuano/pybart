import os.path

import mne
import numpy as np
import scipy.signal

from ..toolbox.covariance import matCov
from ..toolbox.h5file import writeH5FileTemplate
from ..toolbox.riemann import mean_riemann
from ..toolbox.varioustools import compute_rTNT

def riemann_template_learn(file_complete_path, rejection_rate=0.15, l_freq=.5, h_freq=20):
    """This function is generating a riemann template.

    It take one .vhdr path in argument and return
    a dict containing all calibration data.

    Riemann template is use to calibrate the MYB game.

    :param file_complete_path: Path to a ".vhdr" file.
    :type file_complet_path: str
    :param rejection_rate: Determined the rate of epochs rejection. 
    :type rejection_rate: float
    :param l_freq: Low frequency of the pass band.
    :type l_freq: float
    :param h_freq: High frequency of the pass band.
    :type h_freq: float

    """

    # reading the raw brainvison file .vhdr
    raw = mne.io.read_raw_brainvision(file_complete_path, scale=1e6, preload=True, verbose=False)

    # deleting the first market(unused)
    raw.annotations.delete(0)

    # converting annotations from the raw to events for epoching
    raw_events, raw_events_id = mne.events_from_annotations(raw, verbose=False)

    # applying a filter
    raw_filtered = filtering_raw(raw, l_freq, h_freq)

    # epoching
    epochs = mne.Epochs(raw_filtered, raw_events, raw_events_id,
                            tmin=0.000, tmax=0.599,
                            baseline=None,
                            reject_by_annotation=False, 
                            preload=True, verbose=False)

    # setting of the calibration sequence
    calib_target_sequence = [7, 4, 2, 6, 3, 1, 5, 1, 4, 3, 7, 6, 2, 5, 2, 5, 7, 1, 6, 3, 4]

    # marking the targeted events
    raw_events_targeted = marking_target_events(raw_events, calib_target_sequence)

    # get index of epochs above threshold
    epochs_to_remove = get_index_reject_epochs(epochs=epochs, rejection_rate=rejection_rate)

    # removing epochs and events to get thresholded data
    epochs.drop(epochs_to_remove)
    raw_events_thresholded = np.delete(raw_events_targeted, epochs_to_remove, axis=0)


    # browse all epochs
    epochs_T = []
    epochs_NT = []
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
    ERP_Template_NoTarget = np.mean(epochs_NT, axis=0)

    varERP_Template_Target = np.var(epochs_T, axis=0)
    varERP_Template_NoTarget = np.var(epochs_NT, axis=0)

    matCov_TrialTarget = matCov(epochs_T, ERP_Template_Target)
    matCov_TrialNoTarget = matCov(epochs_NT, ERP_Template_Target)

    matCov_TrialTarget = np.array(matCov_TrialTarget)
    matCov_TrialNoTarget = np.array(matCov_TrialNoTarget)

    # TODO check `logm` stability
    mean_MatCov_Target = mean_riemann(matCov_TrialTarget)
    mean_MatCov_NoTarget = mean_riemann(matCov_TrialNoTarget)

    mu_rTNT_TrialTarget,  var_rTNT_TtrialTarget, all_rTNT_TrialTarget = compute_rTNT(matCov_TrialTarget, mean_MatCov_Target, mean_MatCov_NoTarget)
    mu_rTNT_TrialNoTarget, Var_rTNT_TrialNoTarget, all_rTNT_TrialNoTarget = compute_rTNT(matCov_TrialNoTarget, mean_MatCov_Target, mean_MatCov_NoTarget)

    NbGoodTarget = float(np.sum(all_rTNT_TrialTarget < .0))
    NbGoodNoTarget = float(np.sum(all_rTNT_TrialNoTarget > .0))
    NbTotTrials = float(all_rTNT_TrialTarget.shape[0] + all_rTNT_TrialNoTarget.shape[0])

    accP300 = np.float64((NbGoodTarget+NbGoodNoTarget)*100 / NbTotTrials)

    riemann_template = {}
    riemann_template['mu_Epoch_T'] = ERP_Template_Target
    riemann_template['mu_Epoch_NT'] = ERP_Template_NoTarget
    riemann_template['var_Epoch_T'] = varERP_Template_Target
    riemann_template['var_Epoch_NT'] = varERP_Template_NoTarget
    riemann_template['mu_MatCov_T'] = mean_MatCov_Target
    riemann_template['mu_MatCov_NT'] = mean_MatCov_NoTarget
    riemann_template['mu_rTNT_T'] = mu_rTNT_TrialTarget
    riemann_template['mu_rTNT_NT'] = mu_rTNT_TrialNoTarget
    riemann_template['sigma_rTNT_T'] = var_rTNT_TtrialTarget
    riemann_template['sigma_rTNT_NT'] = Var_rTNT_TrialNoTarget
    riemann_template['accP300'] = accP300

    return riemann_template

def filtering_raw(raw, l_freq, h_freq):
    """This function filtering a raw format without using forward-backward method

    :param raw_events: mne tools storing raw data from a BrainVision Recorder
    :type raw_events: mne.io.Raw
    :param l_freq: Low frequency of the pass band.
    :type l_freq: float
    :param h_freq: High frequency of the pass band.
    :type h_freq: float

    """
    raworig_Data = raw._data
    
    Wn = [l_freq/(raw.info['sfreq']/2.), h_freq/(raw.info['sfreq']/2.) ]
    
    b, a = scipy.signal.iirfilter(N=2,
                                    Wn=Wn,
                                    btype='bandpass',
                                    analog=False,
                                    ftype='butter', output='ba')

    raw._data = scipy.signal.lfilter(b, a, raworig_Data, axis = 1, zi = None)

    return raw

def marking_target_events(raw_events, sequence_target):
    """This function marks targeted events thanks to a list of index

    :param raw_events: mne tools storing raw data from a BrainVision Recorder
    :type raw_events: mne.io.Raw
    :param sequence_target: list of target for each round of the calibration 
    :type sequence_target: list(int)
    
    """

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
    """This function removes Epochs from the Mne.Epochs object according a rate
    
    :param epochs: mne tools storing all epochs before rejection
    :type epochs: mne.Epochs
    :param rejection_rate: Determined the rate of epochs rejection. 
    :type rejection_rate: float
    
    """

    # get raw data from the epochs
    data = epochs.get_data()

    # apply absolute value on data
    epochs_absvalue = np.fabs(data)

    # get maximum value per epochs
    epochs_maxvalue = epochs_absvalue.max(2)
    epochs_maxvalue = epochs_maxvalue.max(1)
    
    # calculate the number of epochs that should be rejected
    nb_keeped_epochs_no_rounded = epochs_maxvalue.size*(1-rejection_rate)
    nb_keeped_epochs = np.fix(nb_keeped_epochs_no_rounded).astype(np.int)

    # sort epochs then get the threshold
    threshold = np.sort(epochs_maxvalue)[nb_keeped_epochs]

    # create list of index who have epochs above threshold
    epochs_to_remove = np.where(epochs_maxvalue > threshold)[0]

    return epochs_to_remove
    
def generate_template(raw_file, rejection_rate, l_freq, h_freq):
    """This function generate h5py(.h5) file to store the template de riemann
    
    :param raw_file: mne tools storing raw data from a BrainVision Recorder
    :type raw_file: mne.io.Raw
    :param rejection_rate: Determined the rate of epochs rejection. 
    :type rejection_rate: float
    :param l_freq: Low frequency of the pass band.
    :type l_freq: float
    :param h_freq: High frequency of the pass band.
    :type h_freq: float
 
    """ 
    extension = os.path.splitext(raw_file)[1]
    if extension != '.vhdr':
        raise ValueError("{} file not supported".format(raw_file))

    # gen template
    riemann_template = riemann_template_learn(raw_file, rejection_rate, l_freq, h_freq)

    # get file
    raw_name = os.path.basename(raw_file)
    h5_name = "TemplateRiemann\\Template_{}.h5".format(raw_name)
    writeH5FileTemplate(riemann_template, h5_name)

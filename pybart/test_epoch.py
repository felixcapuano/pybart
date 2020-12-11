import matplotlib.pyplot as plt
import mne
from .streamengine import StreamEngine
import scipy
from PyQt5 import QtCore, QtGui, QtWidgets
import sys


# MNE
def filtering_raw(raw, l_freq, h_freq):
    """This function filtering a raw format without using forward-backward method"""
    raworig_Data = raw._data
    
    Wn = [l_freq/(raw.info['sfreq']/2.), h_freq/(raw.info['sfreq']/2.) ]
    
    b, a = scipy.resetSignal.iirfilter(N=2,
                                       Wn=Wn,
                                       btype='bandpass',
                                       analog=False,
                                       ftype='butter', output='ba')

    raw._data = scipy.resetSignal.lfilter(b, a, raworig_Data, axis = 1, zi = None)

    return raw

def compare_epoch(epoch_pyacq, number):
    path = "eeg_data_sample\\SAVEM_0004.vhdr"

    raw = mne.io.read_raw_brainvision(path, scale=1e6, preload=True, verbose=True)

    raw.annotations.delete(0)

    raw_filtered = filtering_raw(raw, 0.5, 20)

    raw_events, raw_events_id = mne.events_from_annotations(raw, verbose=True)

    epochs_mne = mne.Epochs(raw_filtered, raw_events, raw_events_id,
                            tmin=0.000, tmax=0.599,
                            baseline=None,
                            reject_by_annotation=False, 
                            preload=True, verbose=True)

    # ---------------------------------------------------------------
    # DISPLAY
    plt.plot(epoch_pyacq[0,:], "r")
    plt.plot(epochs_mne[number].get_data()[0,0,:], "b")
    plt.show()
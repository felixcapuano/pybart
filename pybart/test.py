import mne
import numpy as np


file_complete_path = "C:\\Users\\User\\Documents\\pybart\\eeg_data_sample\\CAPFE_0002.vhdr"

# reading the raw brainvison file .vhdr
raw = mne.io.read_raw_brainvision(file_complete_path, preload=True, verbose=False)

# deleting the first market(unused)
raw.annotations.delete(0)

# converting annotations from the raw to events for epoching
raw_events, raw_events_id = mne.events_from_annotations(raw, verbose=False)

# applying a filter TODO  Need to be approved
# raw_filtered = raw.filter(.5, 20., verbose=False)

# epoching
epochs = mne.Epochs(raw, raw_events, raw_events_id,
                        tmin=-0.001, tmax=0.000,
                        reject_by_annotation=False, 
                        preload=True, verbose=False)

print(".shape", epochs.get_data().shape)

e = epochs[0].info

r = raw.info

print(e)
print(r)

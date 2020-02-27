import mne
import numpy as np

file_complete_path = "C:\\Users\\User\\Documents\\pybart\\eeg_data_sample\\CAPFE_0002.vhdr"

# reading the raw brainvison file .vhdr
raw = mne.io.read_raw_brainvision(file_complete_path, preload=True, verbose=False)
print(raw.info)
# deleting the first market(unused)
raw.annotations.delete(0)

# converting annotations from the raw to events for epoching
raw_events, raw_events_id = mne.events_from_annotations(raw, verbose=False)


# applying a filter TODO  Need to be approved
# raw_filtered = raw.filter(.5, 20., verbose=False)

# epoching
epochs = mne.Epochs(raw, raw_events, raw_events_id,
                        tmin=0, tmax=0.6,
                        baseline=None,
                        reject_by_annotation=False, 
                        preload=True, verbose=False)
print(epochs.info)
print(raw_events.shape)
print(epochs.get_data().shape)


epochs_data = epochs.get_data()
raw_data = raw.get_data()

a1 = epochs_data[0,0,0]
a2=raw_data[0,20354]

print(a1)
print(a2)
for i, index in enumerate(raw_events[:,0]):
    print(raw_data[0,index] == epochs_data[i,0,0])

# data, time = raw.get_data(start=20353,stop=20357, return_times=True)
# print(".raw")
# print(data)
# print(".epoch")
# print(epochs[0].get_data())

# raw.plot(decim=1, block=True)
# epochs.plot( scalings='auto', n_epochs=21, n_channels=16, events=raw_events, decim=1, block=True)

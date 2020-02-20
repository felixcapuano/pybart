import mne
import numpy as np
import os
import time

vhdrPath = 'C:\\Users\\User\\Documents\\InterLabex\\CAPFE_0002.vhdr'
vhdrPathBis = 'C:\\Users\\User\\Documents\\InterLabex\\regen-000002.ahdr'
vmrkPath = 'C:\\Users\\User\\Documents\\InterLabex\\CAPFE_0002.vmrk'

raw = mne.io.read_raw_brainvision(vhdrPath)
try:
    print(raw.info['lol'])
except KeyError:
    print('femjf')
# b = np.transpose(raw.get_data()) * 1000000 / 0.0488281
# print(b[:,0])

# buffer = np.transpose(raw.get_data())
# chan = 0
# for sensor in raw.info['chs']:
#     buffer[:,chan] /= sensor['cal']*1000000
#     chan +=1

# print(buffer[:,0])
# print(raw.info['chs'][1]['cal'])

# start, stop = 166080,166086

# period = raw.get_data(start=start,stop=stop)

# for i in range(stop-start):
#     p = period[:,i]*1000000/0.0488281 # gain de tes morts

#     # if -126837 == p.astype(int)[0]:
#     #     print(i+start, p.astype(int))
    
#     print(i+start, p.astype(int))

# events_orig = mne.events_from_annotations(raw, event_id='auto')[0] 
# events = np.copy(events_orig)    
# ind = np.where(events_orig[:,2]==99999)[0]
# events = np.delete(events_orig,ind, axis=0)

# print(events)

# pathF = 'C:\\Users\\User\\Documents\\InterLabex'
# f_raw_out = os.path.join(pathF, 'CAPFE.raw.fif')
# f_eve_out = os.path.join(pathF, 'CAPFE.raw-eve.fif')

# raw.save(f_raw_out, overwrite=True)
# mne.write_events(f_eve_out,events)

# rawFif = mne.io.read_raw_fif(f_raw_out)
# eventsFif = mne.read_events(f_eve_out)

# epochs = mne.Epochs(rawFif, eventsFif, 1, )

# event_id, tmin, tmax = 2, -0.001, 0.002

# epochs = mne.Epochs(rawFif, eventsFif, event_id, tmin, tmax, baseline=(0, 0), preload=True)
# data = epochs.get_data()
# print(data[0,:,:])

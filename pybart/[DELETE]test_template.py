from pipeline.templatecalibration import riemann_template_learn
import h5py
import numpy as np
import matplotlib.pyplot as plt

def init_Template_Riemann( Template_H5Filename):
        f = h5py.File(Template_H5Filename, 'r')

        template_riemann = {}
        for element in f:
            groupe = f[element]

            for element in groupe:
                template_riemann[element] = groupe[element]

        return template_riemann

# print('------------------------------------------')
# print('New calibration template generating')
# print('------------------------------------------')
# path_vhdr = "C:\\Users\\User\\Documents\\pybart\\eeg_data_sample\\CAPFE_0002.vhdr"
# rt_vhdr = riemann_template_learn(path_vhdr)
# print('')
print('------------------------------------------')
print('reading old file .h5')
print('------------------------------------------')
path_h5 = "C:\\Users\\User\\Documents\\pybart\\TemplateRiemann\\Template_CAPFE_0002.vhdr.h5"

rt_h5 = init_Template_Riemann(path_h5)

# print data
for key, item in rt_h5.items():
    if item.shape == np.shape([0]):
        print(key, item[0])
    else:
        print(key, item.shape)

# # plot epoch
# plt.plot(rt_h5['mu_Epoch_NT'][1,:], 'r')
# # plt.plot(mean_templ_NT[1,:], 'b')
# plt.show()
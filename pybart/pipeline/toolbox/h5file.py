import h5py


def writeH5FileTemplate(TemplateRiemann, H5filename):
    Template = h5py.File(H5filename, 'w')
    # RECUPERE LES DIMENSIONS des futurs datasets
    shape_mu_Epoch_T = TemplateRiemann['mu_Epoch_T'].shape
    shape_mu_MatCov = TemplateRiemann['mu_MatCov_T'].shape

    # CREATION et REMPLISSAGE des DATASETS, du fichier _Template.h5

    # CREATION du GROUPE pour le fichier
    gr_Template = Template.create_group('Template')

    # mu_Epoch_T = Moyenne des Epochs T
    ds_mu_Epoch_T = gr_Template.create_dataset("mu_Epoch_T", (shape_mu_Epoch_T),
                                               dtype='float64')  # 1 est la dimension du dataset
    ds_mu_Epoch_T[...] = TemplateRiemann['mu_Epoch_T'][...]

    # mu_Epoch_NT = Moyenne des Epochs NT
    ds_mu_Epoch_NT = gr_Template.create_dataset("mu_Epoch_NT", (shape_mu_Epoch_T),
                                                dtype='float64')  # 1 est la dimension du dataset
    ds_mu_Epoch_NT[...] = TemplateRiemann['mu_Epoch_NT'][...]

    # var_Epoch_T = Variance des Epochs T
    ds_var_Epoch_T = gr_Template.create_dataset("var_Epoch_T", (shape_mu_Epoch_T),
                                                dtype='float64')  # 1 est la dimension du dataset
    ds_var_Epoch_T[...] = TemplateRiemann['var_Epoch_T'][...]

    # var_Epoch_NT = Variance des Epochs NT
    ds_var_Epoch_NT = gr_Template.create_dataset("var_Epoch_NT", (shape_mu_Epoch_T),
                                                 dtype='float64')  # 1 est la dimension du dataset
    ds_var_Epoch_NT[...] = TemplateRiemann['var_Epoch_NT'][...]

    # mu_MatCov_T
    ds_mu_MatCov_T = gr_Template.create_dataset("mu_MatCov_T", (shape_mu_MatCov),
                                                dtype='float64')  # 1 est la dimension du dataset
    ds_mu_MatCov_T[...] = TemplateRiemann['mu_MatCov_T'][...]

    # mu_MatCov_NT
    ds_mu_MatCov_NT = gr_Template.create_dataset("mu_MatCov_NT", (shape_mu_MatCov),
                                                 dtype='float64')  # 1 est la dimension du dataset
    ds_mu_MatCov_NT[...] = TemplateRiemann['mu_MatCov_NT'][...]

    # mu_rTNT_T
    ds_mu_rTNT_T = gr_Template.create_dataset("mu_rTNT_T", (1,), dtype='float64')  # 1 est la dimension du dataset
    ds_mu_rTNT_T[...] = TemplateRiemann['mu_rTNT_T'][...]

    # mu_rTNT_NT
    ds_mu_rTNT_NT = gr_Template.create_dataset("mu_rTNT_NT", (1,), dtype='float64')  # 1 est la dimension du dataset
    ds_mu_rTNT_NT[...] = TemplateRiemann['mu_rTNT_NT'][...]

    # sigma_rTNT_T
    ds_sigma_rTNT_T = gr_Template.create_dataset("sigma_rTNT_T", (1,), dtype='float64')  # 1 est la dimension du dataset
    ds_sigma_rTNT_T[...] = TemplateRiemann['sigma_rTNT_T'][...]

    # sigma_rTNT_NT
    ds_sigma_rTNT_NT = gr_Template.create_dataset("sigma_rTNT_NT", (1,),
                                                  dtype='float64')  # 1 est la dimension du dataset
    ds_sigma_rTNT_NT[...] = TemplateRiemann['sigma_rTNT_NT'][...]

    # AccP300
    ds_AccP300 = gr_Template.create_dataset("AccP300", (1,), dtype='float64')  # 1 est la dimension du dataset
    ds_AccP300[...] = TemplateRiemann['AccP300'][...]

    # On referme le fichier HDF5
    Template.close()
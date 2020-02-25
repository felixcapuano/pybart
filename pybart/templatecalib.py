import numpy as np
import scipy
from pyriemann.utils.mean import mean_riemann
import mne

def riemann_template_learn(file_complete_path):
    raw = mne.io.read_raw_brainvision(file_complete_path, preload=True)
    raw.annotations.delete(0)
    raw_events, raw_events_id = mne.events_from_annotations(raw)

    raw_filtered = raw.filter(.5, 20.)

    epochs = mne.Epochs(raw_filtered, raw_events, raw_events_id, tmin=-0.001, tmax=0.598, reject_by_annotation = False, preload=True) # TODO Weird value tmin tmax

    # print(".shape event", raw_events.shape)
    print(".shape data epochs", epochs.get_data().shape)
    
    calib_target_sequence = [7,4,2,6,3,1,5,1,4,3,7,6,2,5,2,5,7,1,6,3,4]
    # -------------------------------------------------------------------------------------------------
    # event_code_target: (event_code_indexes, event_code_labels, bool_target)
    # event_code_target = list()
    # for index_target, target in enumerate(calib_target_sequence[0]):
    #     flashes_sequence_per_target = range(index_target*nombre_repetitions*nombre_colonnes, (index_target+1)*nombre_repetitions*nombre_colonnes)
    #     try:
    #         event_code_target.append(np.column_stack((events_positions[flashes_sequence_per_target], events_positions[flashes_sequence_per_target, 1] == target)))
    #     except IndexError:
    #         print('not enough data to process parameters')
    # event_code_target = np.array(event_code_target)
    # event_code_target = event_code_target.reshape((event_code_target.shape[0]*event_code_target.shape[1], event_code_target.shape[2]))
    # -------------------------------------------------------------------------------------------------
    
    column_nb = 7
    iterate_nb = epochs.get_data().shape[0] / (column_nb * len(calib_target_sequence))


    epochs_index = list()
    for index_target, target in enumerate(calib_target_sequence):
        nb_flash_per_sequence = iterate_nb * column_nb

        index_start_sequence = index_target * nb_flash_per_sequence
        index_stop_sequence = (index_target + 1) * nb_flash_per_sequence

        flashes_per_sequence = range(index_start_sequence, index_stop_sequence)

        # TODO add all event en mark target ones



    epochs_above_threshold = index_to_reject(data=epochs.get_data(), rejection_rate=0.1)

    # epochs_index_thresholded = np.delete(epochs_index, epochs_above_threshold, axis=0)      
    # print(".", epochs_index_thresholded)


def index_to_reject(data, rejection_rate):
    epochs_absvalue = np.fabs(data)
    # print(".epochs absolute value", epochs_absvalue)

    epochs_maxvalue = epochs_absvalue.max(2).max(1)
    # print(".epochs max value", epochs_maxvalue)

    nb_keeped_epochs_no_rounded = epochs_maxvalue.size*(1-rejection_rate)
    nb_keeped_epochs = np.fix(nb_keeped_epochs_no_rounded).astype(np.int)
    # print(".nb keeped epochs", nb_keeped_epochs)

    threshold = np.sort(epochs_maxvalue)[nb_keeped_epochs]
    # print(".keeped epochs", threshold)

    epochs_to_remove = np.where(epochs_maxvalue > threshold)[0]
    # print(".epoch index to remove", epochs_to_remove)

    return epochs_to_remove




path = "C:\\Users\\User\\Documents\\pybart\\eeg_data_sample\\CAPFE_0002.vhdr"
riemann_template_learn(path)


def riemann_template_learn(file_complete_path,  analysis_time_window_sec=1, threshold_rejection=0.1):

    #ouvre un fichier .vhrd (brainproducts)
    nom_de_code_du_sujet = file_complete_path.split('/')[-1].split('.vhdr')[0]
    nom_de_code_du_sujet = nom_de_code_du_sujet.split('-')[0] #si on choisi le fichier manuellement il faut supprimer la date dans le nom de fichier
    
    modif_date = pyrte.utils.get_modification_date(file_complete_path)
    print('opening file *** ', file_complete_path.split('/')[-1], 'modified on', modif_date)
    
    
    
    print('reading vhdr file')
    data = pyrte.utils.read_brainampfile(file_complete_path)    
    
    
    data['eventarray_indexes'] = np.rint(data['eventarray_indexes']) #etre certain de ne pas avoir d'erreur d'arrondi
    data['eventarray_indexes'] = data['eventarray_indexes'] - 1
    
    
    
    
    data['analog_signals'] = pyrte.algorithms.preprocessing_bandpassfilter(
                                                                    signal_channels=data['analog_signals'], 
                                                                    sampling_rate=data['sampling_rate'], 
                                                                    filter_order=2, 
                                                                    low_freq_cutoff=.5, 
                                                                    hi_freq_cutoff=20)
                                                                    
    #    scipy.io.savemat('C:\_MANU\_U821\Stage\Raphaelle\POS.mat', mdict={'POS': data['eventarray_indexes'] })
    #    scipy.io.savemat('C:\_MANU\_U821\Stage\Raphaelle\DataPy.mat',mdict={'DataPy': data['analog_signals']})
    
    calib_target_sequence = [[7,4,2,6,3,1,5,1,4,3,7,6,2,5,2,5,7,1,6,3,4]]
    
    
    
    sampling_frequency = data['sampling_rate']
    
    
    Offset = 0 #ms
    Offset = np.fix(Offset * sampling_frequency/ 1000 )    
    print('Offset',Offset)    
    number_of_channels, samples_per_channels = data['analog_signals'].shape
    nb_samples_analysis_time_window = (int)(analysis_time_window_sec * sampling_frequency)
    print('nb_samples_analysis_time_window',nb_samples_analysis_time_window)
    nombre_colonnes = 7
    number_of_events = data['eventarray_indexes'].shape[0]
    
    nombre_repetitions = number_of_events/(nombre_colonnes*21)
    
    #    print('index',data['eventarray_indexes'])
    
    data['eventarray_indexes'] = data['eventarray_indexes'] + Offset#ici
    events_positions = np.column_stack((data['eventarray_indexes'], data['eventarray_labels']))
    pos_events_P300_mask = (data['eventarray_labels'] > 0) & (data['eventarray_labels'] < 8)
    events_positions = events_positions[pos_events_P300_mask] #Suppression of non-events P300 stimulations
    print('P300 stimulations number =', events_positions.shape[0])

    #verifier si assez de triggers dans le fichier de donnees et comparer avec la sequence de target du stimulateur
    if events_positions.shape[0] != (len(calib_target_sequence[0]) * nombre_repetitions * nombre_colonnes):
        #np.unique(events_positions[:, 1]) # to see the event code labels
        raise Exception('data do not match parameters: needs {} trials but found {} trials in saved data'.format(len(calib_target_sequence[0]), events_positions.shape[0]/(nombre_repetitions * nombre_colonnes)))
    else:
        print('***', file_complete_path.split('/')[-1], 'contains', events_positions.shape[0] / (nombre_repetitions * nombre_colonnes), 'targets with', nombre_repetitions, 'flashes')

    #event_code_target: (event_code_indexes, event_code_labels, bool_target)
    event_code_target = list()
    for index_target, target in enumerate(calib_target_sequence[0]):
        flashes_sequence_per_target = range(
                                        index_target*nombre_repetitions*nombre_colonnes,
                                        (index_target+1)*nombre_repetitions*nombre_colonnes)
        try:
            event_code_target.append(np.column_stack((events_positions[flashes_sequence_per_target], events_positions[flashes_sequence_per_target, 1] == target)))
        except IndexError:
            print('not enough data to process parameters')
    event_code_target = np.array(event_code_target)
    event_code_target = event_code_target.reshape((event_code_target.shape[0]*event_code_target.shape[1], event_code_target.shape[2]))

    
    epochs_all_data_channels = pyrte.algorithms.rte_Epoching(data['analog_signals'], event_code_target[:, 0], nb_samples_analysis_time_window)
    #custom_print_in_blue('epochs_all_data_channels',epochs_all_data_channels[0,0, 0:200])    # chan *trials * sample                                                       
    #scipy.io.savemat('\\10.69.111.22\dycog\Jeremie\MindYourBrain\Dev\epoch1.mat', mdict={'Epoch1': epochs_all_data_channels[0,0, :]})
    #scipy.io.savemat('D:\Dycog\Dev_Python\epoch1.mat', mdict={'Epoch1': epochs_all_data_channels[0,0, :]})
#    scipy.io.savemat('C:\_MANU\_U821\Stage\Raphaelle\event_code_target.mat', mdict={'event_code_target': event_code_target[:, 0] })
#    scipy.io.savemat('C:\_MANU\_U821\Stage\Raphaelle\epoch1.mat', mdict={'Epoch1': epochs_all_data_channels[0,0, :]})
    scipy.io.savemat('D:\Dycog\wip\epochs_all_data_channels.mat', mdict={'epochs_all_data_channels': epochs_all_data_channels})
    
#    epochs_maxvalue = epochs_all_data_channels.max(2).max(0)
    absepochs_maxvalue = np.fabs(epochs_all_data_channels)
    epochs_maxvalue = absepochs_maxvalue.max(2).max(0)

    if (threshold_rejection>0):
        reject_above_threshold = np.sort(epochs_maxvalue)[np.fix(epochs_maxvalue.size*(1-threshold_rejection)).astype(np.int)]
        epochs_to_remove_indexes = np.where(epochs_maxvalue > reject_above_threshold)[0]
        event_code_target_with_threshold_rejection = np.delete(event_code_target, epochs_to_remove_indexes, axis=0)
        print('applying', epochs_to_remove_indexes.size, 'threshold rejections over', reject_above_threshold, 'uV')

    else:
        epochs_to_remove_indexes = []
        event_code_target_with_threshold_rejection = event_code_target
    
	
    epochs_data_channels_clean = pyrte.algorithms.rte_Epoching(data['analog_signals'], event_code_target_with_threshold_rejection[:, 0], nb_samples_analysis_time_window)
    Epochs_T = []
    Epochs_NT = []
  
  
    for i in range(epochs_data_channels_clean.shape[1]):
        epoch = epochs_data_channels_clean[:,i,:]
        if event_code_target_with_threshold_rejection[i,2] == 1:
            Epochs_T.append(epoch)
        else:
            Epochs_NT.append(epoch)
  
        	
	
 
    Epochs_T = np.array(Epochs_T)
    Epochs_NT = np.array(Epochs_NT)


    		
    ERP_Template_Target = np.mean(Epochs_T, axis = 0)
    ERP_Template_NoTarget = np.mean(Epochs_NT, axis = 0)
	
    VarERP_Template_Target = np.var(Epochs_T, axis = 0)
    VarERP_Template_NoTarget = np.var(Epochs_NT, axis = 0)
    
    # voir email
    MatCov_TrialTarget = pyrte.utils.matCov(Epochs_T, ERP_Template_Target)
    MatCov_TrialNoTarget = pyrte.utils.matCov(Epochs_NT, ERP_Template_Target)
    

    MatCov_TrialTarget=np.array(MatCov_TrialTarget)
    MatCov_TrialNoTarget=np.array(MatCov_TrialNoTarget)
    
    scipy.io.savemat('D:\Dycog\wip\MatCov_TrialTarget.mat', mdict={'MatCov_TrialTarget': MatCov_TrialTarget})
    scipy.io.savemat('D:\Dycog\wip\MatCov_TrialNoTarget.mat', mdict={'MatCov_TrialNoTarget': MatCov_TrialNoTarget})
    
    mean_MatCov_Target = mean_riemann(MatCov_TrialTarget)
    mean_MatCov_NoTarget = mean_riemann(MatCov_TrialNoTarget)
    scipy.io.savemat('D:\Dycog\wip\mean_MatCov_Target.mat', mdict={'mean_MatCov_Target': mean_MatCov_Target})
    scipy.io.savemat('D:\Dycog\wip\mean_MatCov_NoTarget.mat', mdict={'mean_MatCov_NoTarget': mean_MatCov_NoTarget})

    Mu_rTNT_TrialTarget,  Var_rTNT_TtrialTarget, All_rTNT_TrialTarget   = pyrte.utils.compute_rTNT(MatCov_TrialTarget,mean_MatCov_Target,mean_MatCov_NoTarget)
    Mu_rTNT_TrialNoTarget,Var_rTNT_TrialNoTarget,All_rTNT_TrialNoTarget = pyrte.utils.compute_rTNT(MatCov_TrialNoTarget,mean_MatCov_Target,mean_MatCov_NoTarget)
    
    NbGoodTarget = float(np.sum(All_rTNT_TrialTarget < .0))
    NbGoodNoTarget = float(np.sum(All_rTNT_TrialNoTarget > .0))
    NbTotTrials = float(All_rTNT_TrialTarget.shape[0]+All_rTNT_TrialNoTarget.shape[0])  
    AccP300 =  np.float64((NbGoodTarget+NbGoodNoTarget)*100 /NbTotTrials)
    
    TemplateRiemann = {}
    TemplateRiemann['mu_Epoch_T'] = ERP_Template_Target
    TemplateRiemann['mu_Epoch_NT'] = ERP_Template_NoTarget
    TemplateRiemann['var_Epoch_T'] = VarERP_Template_Target
    TemplateRiemann['var_Epoch_NT'] = VarERP_Template_NoTarget	
    TemplateRiemann['mu_MatCov_T'] = mean_MatCov_Target
    TemplateRiemann['mu_MatCov_NT'] = mean_MatCov_NoTarget
    TemplateRiemann['mu_rTNT_T'] = Mu_rTNT_TrialTarget
    TemplateRiemann['mu_rTNT_NT'] = Mu_rTNT_TrialNoTarget
    TemplateRiemann['sigma_rTNT_T'] = Var_rTNT_TtrialTarget      
    TemplateRiemann['sigma_rTNT_NT'] = Var_rTNT_TrialNoTarget      
    TemplateRiemann['AccP300'] = AccP300

    return (TemplateRiemann)
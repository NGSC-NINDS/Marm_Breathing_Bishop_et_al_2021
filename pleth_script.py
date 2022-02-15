import numpy as np
import neo
import pandas as pd
import neurokit2 as nk
from matplotlib import pyplot as plt
from neo.io import Spike2IO
import scipy
import matplotlib.mlab as mlab
from scipy import stats
import os
import time
from config import *


#Most of the relevant parameters are contained within the config file. 
# For most analyses, simply changing the config and then running this script in terminal will suffice


def rsp_process(raw_sig, samp_rate):
    plt.rcParams["figure.figsize"] = (20,10)
    """Processing pipeline for plethysmography signal.
    
    Parameters
    ----------
    raw_sig: numpy array
        Raw respiratory signal, input from NEOIO
    
    samp_rate: int
        Sampling rate in Hz.
        
    Returns
    -------
    signals: Pandas Dataframe
        Dataframe full of features extracted from raw signal.
    """

    if start_plot is not None:
        raw_sig = raw_sig[int(start_plot*samp_rate):int(end_plot*samp_rate)]

    # Neurokit2 functions for cleaning raw signal and finding peaks
    sig_detrended = nk.signal_detrend(raw_sig)
    sig_filtered = nk.signal_filter(sig_detrended, lowcut=.05, highcut=5, sampling_rate=samp_rate)
    peak_signal, info = nk.rsp_peaks(sig_filtered,sampling_rate=samp_rate, amplitude_min=.05)

    # Get additional parameters
    phase = nk.rsp_phase(peak_signal, desired_length=len(raw_sig))
    amplitude = nk.rsp_amplitude(sig_filtered, peak_signal)
    rate = nk.signal_rate(peak_signal, sampling_rate=samp_rate, desired_length=len(raw_sig))


    # Prepare output
    signals = pd.DataFrame({"RSP_Raw": raw_sig,
                            "RSP_Clean": sig_filtered,
                            "RSP_Amplitude": amplitude,
                            "RSP_Rate": rate})
    signals = pd.concat([signals, phase, peak_signal], axis=1)
    variability = nk.rsp_rrv(signals,sampling_rate=samp_rate)

    if plot == True:
        print('Plotting...')
        print(nk.rsp_plot(signals, sampling_rate=samp_rate))

    return signals, variability

def remove_outliers(signal):
    """Filters out artifact rows in signal dataframe
    based on Rate and Amplitude values.
    
    Parameters
    ----------
    signal: pandas dataframe
        Dataframe returned by rsp_process, should include RSP_Rate and RSP_Amplitude columns. 
        
    Returns
    -------
    cleaned_signal: pandas dataframe
        Dataframe with rows removed that contain outlier Rate or Amplitude Values
    """
    signal = signal[signal.RSP_Rate < 200]
    signal = signal[signal.RSP_Rate > 0]
    signal = signal[signal.RSP_Amplitude > 0]
    cleaned_signal = signal[signal.RSP_Amplitude < 1]
    return cleaned_signal

def find_breaths(rsp, samp_rate, max_bpm=150):
    '''Finds time and number of peaks of apnea and sniffing breathing.
    
    Parameters
    ----------
    rsp: pandas dataframe
        Dataframe returned by rsp_process
    
    Returns
    -------    
    apnea_counts: int
        number of peaks spent in apnea
    
    apnea_time: float
        time spent in apnea breathing
        
    sniff_counts: int
        number of peaks spent in sniff
    
    sniff_time: float
        time spent in sniff breathing
    
    '''
    
    # Remove interpolated values for counting breaths
    peaks_only = rsp.groupby('RSP_Peaks').get_group(1)
    min_bpm = peaks_only.RSP_Rate.mean() / 3 
    # find rate of apneas per second, then multiply for rate/hour
    apnea_rate = 3600 * len(peaks_only[peaks_only.RSP_Rate < min_bpm])/(len(rsp)/samp_rate)
    
    # Use interpolated values for time calculations
    apnea_time = len(rsp[rsp.RSP_Rate < min_bpm])/samp_rate
    
    # same for sniffing
    sniff_rate = 3600*len(peaks_only[(peaks_only.RSP_Rate > max_bpm) & (peaks_only.RSP_Amplitude < 1)])/(len(rsp)/samp_rate)
    sniff_time = len(rsp[rsp.RSP_Rate > max_bpm])/samp_rate
    
    return apnea_rate, apnea_time, sniff_rate, sniff_time
    
    

def file_processor(filename, events_dict, info_df, baseline_df, pre_interval, post_interval, epoch_length, plot, debug = False):
    """
    Processes csv pleth files
    
    Parameters
    ----------
    filename: str
        name of the csv file 
    
    events_dict: dict
        dictionary of different events and their empty dictionaries
    
    info_df: pandas dataframe
        dataframe from excel file that contains info about each animal
        
    samp_rate: int
        Rate in Hz of sampling
    
    epoch_len: int
        length of epochs in seconds that the file is chopped into
    
    plot: bool
        If True, calls Neurokit's plot function on the entire event. Defaults to False
        
    baseline_df: pandas dataframe
        Used for comparison to baseline during challenge to produce % change
        
    last_five: if True then only analyzes after 5 mins of each event
        
    Returns
    -------
    None
    """
    if '.smrx' in filename:
        info_row = info_df[(info_df.ID.str.match(filename[0:-5]))]
    elif '.smr' in filename:
        info_row = info_df[(info_df.ID.str.match(filename[0:-4]))]
    else:
        raise NameError('No smr or smrx detected in filename!')
    print('Detected ID: ', info_row.ID.values[0])
    # Read in raw files
    reader = Spike2IO(filename)
    # Open block to select segment to be read
    block = reader.read(lazy=False)[0]
    raw_signal_vals = np.asarray(block.segments[0].analogsignals[0])
    flat_sig = raw_signal_vals[:,0]
    sampling_rate = block.segments[0].analogsignals[0].sampling_rate.item()
    print('The sampling rate is',sampling_rate, 'Hz')
    print('Please wait, this might take a while...')
    # Process whole signal 
    signals, sig_var = rsp_process(flat_sig, samp_rate=sampling_rate)
    signals['Amp_norm'] = signals.RSP_Amplitude/info_row.weight.values[0]
    for event, dictionary in events_dict.items():
        
        # chop up signals df with values from info_df
        event_start = int(info_row[event+'_start']) * sampling_rate
        event_end = int(info_row[event+'_end']) * sampling_rate
        event_signals = signals.loc[event_start:event_end, :]
        
        if event == 'challenge':
            print('Current event processing: Challenge')
            pre_signals = signals.loc[event_start - 60*pre_interval*sampling_rate:event_start, :]
            post_signals = signals.loc[event_end:event_end+60*post_interval*sampling_rate]
            sig_list = [pre_signals, event_signals, post_signals]
            epoch_len = epoch_length
        else:
            print('Current event processing: ',event)
            pre_signals = signals.loc[event_start-60*pre_interval*sampling_rate:event_start, :]
            sig_list = [pre_signals,event_signals]
            epoch_len = None
        
        sig_counter = 0
        for key, item in dictionary.items():
            sub_sig = sig_list[sig_counter]
            sig_counter += 1

            # Calculate augmented breath measures
            apnea_rate, apnea_time, sniff_rate, sniff_time = find_breaths(sub_sig.reset_index(drop=True), samp_rate=sampling_rate)
            interval_df = nk.rsp_intervalrelated(sub_sig, sampling_rate = sampling_rate)

            # Put them into the appropriate df
            item['Animal'].append(filename[:5])
            item['RSP_Rate_Mean'].append(sub_sig.RSP_Rate.mean())
            item['RSP_Amplitude_Mean'].append(sub_sig.RSP_Amplitude.mean())
            item['Ti'].append(interval_df.RSP_Phase_Duration_Inspiration.values[0])
            item['Te'].append(interval_df.RSP_Phase_Duration_Expiration.values[0])
            item['Ti-Te_Ratio'].append(interval_df.RSP_Phase_Duration_Ratio.values[0])
            item['Resp_Drive'].append(sub_sig.Amp_norm.mean()/interval_df.RSP_Phase_Duration_Inspiration.values[0])
            item['Amp_Norm'].append(sub_sig.Amp_norm.mean())
            item['Ve'].append(sub_sig.Amp_norm.mean() * sub_sig.RSP_Rate.mean())
            item['Apnea_time'].append(apnea_time)
            item['Apnea_rate'].append(apnea_rate)
            item['Sniff_time'].append(sniff_time)
            item['Sniff_rate'].append(sniff_rate)
            item['RRV_SD1'].append(sig_var.RRV_SD1.loc[0])
            item['RRV_SD2'].append(sig_var.RRV_SD2.loc[0])
            
            if epoch_len is not None:
                # Epoch the challenge signal
                epochs = nk.epochs_create(sub_sig, sampling_rate=sampling_rate, epochs_end=epoch_len)
       #         clean_epochs = {key:remove_outliers(epoch) for key,epoch in epochs.items()} 
                epoch_df = nk.rsp_intervalrelated(epochs, sampling_rate=sampling_rate)
                if baseline_df is not None:
                    epoch_df = find_percentchange(epoch_df, baseline_df, animal = filename[9:13])
                # Normalize amp to weight and calc Ve
                epoch_df['Amp_Norm'] = epoch_df.RSP_Amplitude_Mean / info_row.weight.values[0]
                epoch_df['Ve'] = epoch_df.Amp_Norm * epoch_df.RSP_Rate_Mean
                epoch_df['Resp_drive'] = epoch_df.Amp_Norm / epoch_df.RSP_Phase_Duration_Inspiration
                sheet_name = str(info_row.Condition.values[0])+info_row.sex.values[0]+filename[:5]+key+'epochs'
                print('Generated sheet_name: ',sheet_name)
                global writer
                epoch_df.to_excel(writer, sheet_name=sheet_name)
            
            if debug == True:
                return signals   

    
def find_percentchange(epoch_df, baseline_df, animal):
    # animal name is file[9:13]
    measures=[i for i in baseline_df.columns if 'Mean' in i or 'SD' in i]
    animal_row = baseline_df.loc[animal==baseline_df['Animal']]
    for x in measures: 
        base_val = float(animal_row.loc[:,x])
        epoch_df[x+'_percent_change']= 100*(epoch_df[x] - base_val)/base_val
    return epoch_df

    
    
def load_files(folder):
    # Load baseline and challenge files
    os.chdir(folder)
    file_list = sorted([i for i in os.listdir(folder) if 'smr' in i])
    return file_list


def file_writer(output_dir, suffix):
    # Make file writer
    timestr = time.strftime("%Y%m%d-") 
    master_filename = timestr + 'resp_bx' + '.xlsx' 
    global writer
    writer = pd.ExcelWriter(output_dir+'/'+master_filename, engine='xlsxwriter')
    return writer, master_filename
            
    
def events(events_dict):
    for event, dictionary in events_dict.items():
    # instantiate dictionaries that will be filled by file_processor
        events_dict[event]['pre_'+str(event)] = {key:[] for key in cols}
        events_dict[event][event] = {key:[] for key in cols}
        if event == 'challenge': 
            events_dict[event]['post'+event] = {key:[] for key in cols}
    return events_dict
        
    
def process(info_dir, sheet_name, folder, output_dir, suffix, cols, events_dict, baseline_df, pre_interval, post_interval, epoch_length, plot, start_plot, end_plot):
    file_list = load_files(folder)
    events_dict = events(events_dict)
    writer, master_filename = file_writer(output_dir, suffix)
    info_df = pd.read_excel(info_dir, sheet_name)
    for file in file_list:
        print("Processing file: ", file)
        file_processor(file, events_dict, info_df, baseline_df, pre_interval, post_interval, epoch_length, plot)
    print('Writing to excel')
    for key, item in events_dict.items():
        for key2, item2 in item.items():
            df = pd.DataFrame(item2)
            df.to_excel(writer, sheet_name = key2)
        writer.save()
        
        print(master_filename, ' Saved!')


process(info_dir, sheet_name, folder, output_dir, suffix, cols, events_dict, baseline_df, pre_interval, post_interval, epoch_length, plot, start_plot, end_plot)


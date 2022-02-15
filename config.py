import os
"""
The first step in the process is creating a time sync file (excel file), 
    which contains the information for identifying the animals and specifying where the events occur
Typically, the time_sync file has columns: 'ID', 'weight', event_start, event_end, 
    replace 'event' with the 'event' name, for example 'challenge' for 'challenge_start' and 'challenge_end'
        For multiple events, include empty dictionaries in events_dict and include a start and end time for each
        The pipeline typically looks ten minutes before the event to establish a baseline, as well as during the event
    The ID values correspond to the SMR file name (ignoring the filetype, such as .smr)
        this is how the program recognizes unique files
    Weight is used to generate a normalized amplitude, and should be in grams

If the event is a challenge ('challenge'), the pipeline will also look 10 minutes after the event
    For the challenge event, also specify a 'sex' and 'Condition' column in the time sync file
    Challenge events will generate more data, including splitting before, after, and during the event into a number of user-defined epochs

"""

#this is where the time sync file is located. Default is in a folder located in the current directory
#Please ensure that this folder (as well as all others) exist
info_dir = os.path.join(os.path.abspath(os.path.curdir), 'info_dir', 'time_sync.xlsx' ) 

#Specify the excel sheet (bottom of window) the program should use
sheet_name = 'Sheet1'

#this is where the smr files are located
folder = os.path.join(os.path.abspath(os.path.curdir), 'smr_files') 

#This is where the output for the processing will go 
output_dir  = os.path.join(os.path.abspath(os.path.curdir), 'output') 

#If analyzing different signals besides respiration behaviors, can change the suffix to reflect different trials
suffix = 'resp_bx'


#If there are different events, can add additional empty dictionaries to reflect them
events_dict = { 
    'challenge':{} }


#Columns represent the features. If you change these you should also change the corresponding code 
cols = ['Animal','RSP_Rate_Mean','RSP_Amplitude_Mean',
        'Ti', 'Te', 'Ti-Te_Ratio','Resp_Drive','Ve', 'Amp_Norm',
        'Apnea_time','Apnea_rate','Sniff_time','Sniff_rate',
        'RRV_SD1','RRV_SD2']

'''
Features:
---------
Animal: Each animal's unique ID, from the time_sync file and in the form of a string

RSP_Rate_Mean: The average of respiration rate across the event

RSP_Amplitude_Mean: The average of respiration amplitdue across the event

Ti: Duration of inspiration: time passed between trough and subsequent peak

Te: Duration of expiration: time passed between peak and subsequent trough

Ti-Te_Ratio: Ratio of durations of inspiration to expiration

Amp_Norm: Normalized amplitude: amplitude values divided by the animal's weight

Resp_Drive: Ratio of normalized amplitude to duration of inspiration

Ve: Minute ventilation: the product of normalized amplitude and breathing rate

Apnea_time: Time spent in apnea breathing over the interval

Apnea_rate: Rate of apnea per hour over the interval

Sniff_time: Time in sniff breathing over the interval

Sniff_rate: Rate of sniffs per hour over the interval

RRV_SD1, RRV_SD2: Measures of short and long term variability in respiration rate


'''


#A pandas dataframe that can be used for comparison to baseline during challenge to produce % change
baseline_df = None

#The user can specify the amount of time to look before (and after, if a challenge) each event
pre_interval = 5 #min
post_interval = 5 #min, only looks after event if challenge

#specify the number of seconds each epoch will be (only applies to challenge events)
epoch_length = 20 #int in seconds

#If True, calls Neurokit's plot function on the entire event
plot = False

'''
Once the plot is generated for an animal you need to close the image window before the analysis can continue
Generates one plot of the raw and cleaned signals with peaks and troughs, one plot for the breathing rate, 
and another for breathing amplitude

If you want to visualize a specific time period of the event, (say, second 1000 to 1010), 
change plot to True and change start_plot and end_plot values from None
The plot then outputs the breathing signals from start_plot time to end_plot time
If start_plot and end_plot are not None, the full analysis will not run 
    and the figure will only be generated for the first animal in the list

'''

start_plot = None #seconds

end_plot =  None #seconds





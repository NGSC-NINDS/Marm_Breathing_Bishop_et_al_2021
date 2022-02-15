# [Installation: How to install the Python environment]
From the GitHub page, Download the Zip file (or use Git clone) to a desired directory

Ensure that Anaconda or Miniconda is installed (https://docs.conda.io/projects/conda/en/latest/user-guide/install/download.html)

In Terminal (Mac) or Anaconda Prompt (Windows), navigate to the directory where pleth_environ.yaml is located. Then, type:

`conda env create -f pleth_environ.yml`   to create the Python environment.

Once the packages are installed, type   `conda activate pleth` to activate the environment. 

Typing `conda deactivate` will deactivate the current environment and return to the base environment. From the base environment, you can now use `conda activate pleth` to return to the script environment, with all dedicated packages installed.

Now that all the packages are installed, you can move onto using the script!

# [Setting up the Time Sync file]

First, open  the `time_sync.xlsx` file located in the `info_dir` directory.

This file already has the information for the sample file, but for your own experiments you should change the data in the columns (keep the column titles the same).

The script can analyze as many SMR files as you want, just match the ID in the time_sync file with the filename (except the extension, so for example the filename 'mouse12.smr' would have the ID: 'mouse12'

The 'sex' and 'Condition' columns are chiefly used to append a prefix on to the challenge information. The 'weight' column is used to calculate a normalized amplitude of breathing, and is measured in grams., The 'event_start' and 'event_end' columns demarcate the region of interest. If the event is labled 'challenge' (corrsponding to 'challenge_start' and 'challenge_end' in the time_sync file, then the script will analyze a length of time after the event (In addition to time before and during the event, which occurs regardless of what the event is labled), as well as split the pre-, post-, and during- time periods into a number of epochs for more in-depth analysis. 

The script can likewise analyze a number of separate events, they just need to be specified with a start and end time (such as 'event1_start', 'event1_end', 'event2_start', 'event2_end')

Once the time_sync file is edited, you can move to the `config.py` file. 

# [Editing the Config]

This is where most of the user-changes take place. The paths to the info_dir, output, and smr_files directories are set to the default, but can be changed to any particular path. The sheet_name is the default excel sheet name, but for analyzing different sheets of the same file name this can likewise be changed.

Changing the suffix appends a different ending to the output filename, and can be used to demarcate different behaviors.

The events dictionary corresponds to all the events in an SMR file the script will look at. Please make sure that every event listed has a corresponding 'event_start' and 'event_end' in the time_sync file. 

Non-challenge events will have the breathing data calculated and averaged for a pre-interval period, as well as during the event itself. 

If the event is labled 'challenge', the script will additionally analyze a post-interval period, and will subdivide the pre-, post-, and challenge- intervals into epochs across which the breathing data is averaged. 

Please consult the config file for more information on what the specific Features of the analysis are. 

If the user wishes to input a pandas DataFrame object as a baseline to produce a percent change, simply input the path to the object for `baseline_df`

`pre-interval` and `post-interval` allow the user to specify the period before the event (and after, if for a challenge) the script should analyze. The default is 5 minutes. Please ensure that the file has enough time before (and after) the event. 

`epoch_length` is only used if the event is 'challenge', and corresponds to the number of seconds of each epoch. Please keep the epoch length to approximately greater than 20 seconds to allow NeuroKit enough data for analysis. 

Finally, changing `plot` to True generates a plot of the breathing data (raw and cleaned signals, breathing rate, and breathing amplitude), while `start_plot` and `end_plot` specifies the region of interest for the plot itself. Changing `plot` to True will typically not perform the full analysis in the excel file. 

#[Running the Script]

With the Python environment activated, type `python pleth_script.py` (Some Python versions require typing `python3 pleth_script.py`) and hit enter. 

The script will automatically run, and will sequentially go through each one of the SMR files, generating an excel spreadsheet in the `output` directory when analysis is finished. Length videos may take a few minutes to get through, but they will still be quite expedited compared to manual analysis.

Happy analyzing! 

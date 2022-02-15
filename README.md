# [Installation: How to install the Python environment]
From the GitHub page, Download the Zip file (or use Git clone) to a desired directory

Ensure that Anaconda or Miniconda is installed (https://docs.conda.io/projects/conda/en/latest/user-guide/install/download.html)

In Terminal (Mac) or Anaconda Prompt (Windows), navigate to the directory where pleth_environ.yaml is located. Then, type:

`conda env create -f pleth_environ.yml`   to create the Python environment.

Once the packages are installed, type   `conda activate pleth` to activate the environment. 

Typing `conda deactivate` will deactivate the current environment and return to the base environment. From the base environment, you can now use `conda activate pleth` to return to the script environment, with all dedicated packages installed.

Now that all the packages are installed, you can move onto using the script!

# [Using the Script]

First, open  the `time_sync.xlsx` file located in the `info_dir` directory.

This file already has the information for the sample file, but for your own experiments you should change the data in the columns (keep the column titles the same).

The script can analyze as many smr files as you want, just match the ID in the time_sync file with the filename (except the extension, so for example the filename 'mouse12.smr' would have the ID: 'mouse12'

The 'sex' and 'Condition' columns are chiefly used to append a prefix on to the challenge information. The 'weight' column is used to calculate a normalized amplitude of breathing, and is measured in grams., The 'challenge_start' and 'challenge_end' columns demarcate the region of interest. If the event is labled 'challenge' (corrsponding to 'challenge_start' and 'challenge_end' in the time_sync file, then the script will analyze a length of time after the event (In addition to time before and during the event, which occurs regardless of what the event is labled), as well as split the pre-, post-, and during- time periods into a number of epochs for more in-depth analysis. 

The script can likewise analyze a number of separate events, they just need to be specified with a start and end time (such as 'event1_start', 'event1_end', 'event2_start', 'event2_end')

Once the time_sync file is edited, you can move to the `config.py` file. 

This 


With the Python environment activated, type `python pleth_script.py` (Some Python versions require typing `python3 pleth_script.py`)

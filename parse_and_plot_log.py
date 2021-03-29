# Import libraries
import os
import numpy as np
import pandas as pd
import ipywidgets as widgets
from ipywidgets import HBox, VBox, Layout, Box
import matplotlib.pyplot as plt
import datetime

# Obs: the widget magic assumes you have installed NodeJS and 
# @jupyter-widgets/jupyterlab-manager jupyter extension
# 
# To do that, run commands:
# > conda install nodejs
# > jupyter labextension install @jupyter-widgets/jupyterlab-manager
# Then restart jupyter notebook to correctly display plots

# TODO: 2.00E-2 is the default reading value of P1 (maxigauge CH1) when it is turned off. First column of the maxigauge data is 0 when the sensor is turned off

# Parsing functions

def log_parsing(log_folder, data_type):
    '''
    This function reads the log files stored in log_folder and returns a pandas dataframe.
    data_type ('maxigauge', 'Status', 'Flowmeter', 'Temperature'): states which type of data
    is to be read from the log files.
    '''
    
    log_folder = log_folder.strip()
    if log_folder[-1] != '/':
        log_folder += '/'
    
    # Get list of dates registered in log_folder. 
    list_folders_log = os.listdir(log_folder)
    list_date_log = []

    # Filter the valid folders
    for folder in list_folders_log:
        try:
            folder_timestamp = pd.to_datetime(folder, format = "%y-%m-%d")
            list_date_log.append({'str': folder, 
                                  'ts': folder_timestamp})
        except:
            continue

    # Sort valid entries by date. This is important to later identify
    # in which periods of time there's no entry.
    list_date_log.sort(key = lambda x: x['ts'])
    
    if data_type == 'maxigauge':
        
        column_names = ['CH1', 'CH2', 'CH3', 'CH4', 'CH5', 'CH6']
        date_col = []
        CH_col = [[], [], [], [], [], []]
        
        is_first_log = True   
        for date_log in list_date_log:
            log_name = log_folder + date_log['str'] + '/maxigauge ' + date_log['str'] + '.log'
            
            # Check whether file exists
            if not os.path.isfile(log_name):
                continue
                
            with open(log_name, 'r') as log_file:
                log_lines = log_file.readlines()
                
                # Collect a column of data for each registered instant
                for line in log_lines:
                    line = line.split(',')
                    
                    # Fill date column
                    date = line[0].replace(' ','') + ' ' + line[1].replace(' ','')
                    date_col.append(pd.to_datetime(date, format = "%d-%m-%y %H:%M:%S"))
                    
                    # Fill each channel's data column. Note that CH1 signal corresponds to CH_col[0]
                    CH_col[0].append(float(line[5]))
                    CH_col[1].append(float(line[11]))
                    CH_col[2].append(float(line[17]))
                    CH_col[3].append(float(line[23]))
                    CH_col[4].append(float(line[29]))
                    CH_col[5].append(float(line[35]))
                    
                    # Fill a line with NaN's if non-logged period is larger than 5 minutes
                    if is_first_log:
                        is_first_log = False
                        continue

                    if (pd.Timedelta(date_col[-1] - date_col[-2]).seconds)/60.0 > 5:
                        non_logged = pd.date_range(start = date_col[-2], end = date_col[-1], periods = 3)[1]
                        date_col.append(non_logged)
                        CH_col[0].append(np.nan)
                        CH_col[1].append(np.nan)
                        CH_col[2].append(np.nan)
                        CH_col[3].append(np.nan)
                        CH_col[4].append(np.nan)
                        CH_col[5].append(np.nan)
                    
        data_dict = {column_names[i]: CH_col[i] for i in range(len(column_names))}
        index = pd.DatetimeIndex(date_col)
        
        return pd.DataFrame(data = data_dict, index = index).sort_index()
    
    if data_type == 'Status':
        
        column_names = ['nxdsf', 'nxdsct', 'nxdst', 'nxdsbs', 'nxdstrs', 'tc400errorcode', 'tc400ovtempelec', 
                        'tc400ovtemppump', 'tc400setspdatt', 'tc400pumpaccel', 'tc400commerr', 'ctrl_pres', 
                        'cpastate', 'cparun', 'cpawarn', 'cpaerr', 'cpatempwi', 'cpatempwo', 'cpatempo', 'cpatemph', 
                        'cpalp', 'cpalpa', 'cpahp', 'cpahpa', 'cpadp', 'cpacurrent', 'cpahours', 'cpapscale', 
                        'cpatscale', 'cpasn', 'cpamodel']    
        date_col = []
        ST_col = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
        is_first_log = True   
        for date_log in list_date_log:
            log_name = log_folder + date_log['str'] + '/Status_' + date_log['str'] + '.log'
            
            # Check whether file exists
            if not os.path.isfile(log_name):
                continue
                
            with open(log_name, 'r') as log_file:
                log_lines = log_file.readlines()
                
                # Collect a column of data for each registered instant
                for line in log_lines:
                    line = line.replace('\n', '').split(',')
                    
                    # Fill date column
                    date = line[0].replace(' ','') + ' ' + line[1].replace(' ','')
                    
                    if not len(line) == 64:
                        print('Status data missing/incomplete ::: ', date)
                        continue
                        
                    date_col.append(pd.to_datetime(date, format = "%d-%m-%y %H:%M:%S"))
                    
                    # Fill each variable's data column.
                    for i in range(len(column_names)):
                        ST_col[i].append(float(line[3 + 2*i]))
                    
                    # Fill a line with NaN's if non-logged period is larger than 5 minutes
                    if is_first_log:
                        is_first_log = False
                        continue

                    if (pd.Timedelta(date_col[-1] - date_col[-2]).seconds)/60.0 > 5:
                        non_logged = pd.date_range(start = date_col[-2], end = date_col[-1], periods = 3)[1]
                        date_col.append(non_logged)
                        for i in range(len(column_names)):
                            ST_col[i].append(np.nan)
                    
        data_dict = {column_names[i]: ST_col[i] for i in range(len(column_names))}
        index = pd.DatetimeIndex(date_col)
        
        return pd.DataFrame(data = data_dict, index = index).sort_index() 
    
    
    if data_type == 'Flowmeter':
        
        date_col = []
        FL_col = []
        
        is_first_log = True   
        for date_log in list_date_log:
            log_name = log_folder + date_log['str'] + '/Flowmeter ' + date_log['str'] + '.log'
            
            # Check whether file exists
            if not os.path.isfile(log_name):
                continue
                
            with open(log_name, 'r') as log_file:
                log_lines = log_file.readlines()
                
                # Collect a column of data for each registered instant
                for line in log_lines:
                    line = line.split(',')
                    
                    # Fill date column
                    date = line[0].replace(' ','') + ' ' + line[1].replace(' ','')
                    date_col.append(pd.to_datetime(date, format = "%d-%m-%y %H:%M:%S"))
                    
                    # Fill each flowmeter`s data column
                    FL_col.append(float(line[2].replace('\n', '')))
                    
                    # Fill a line with NaN's if non-logged period is larger than 5 minutes
                    if is_first_log:
                        is_first_log = False
                        continue

                    if (pd.Timedelta(date_col[-1] - date_col[-2]).seconds)/60.0 > 5:
                        non_logged = pd.date_range(start = date_col[-2], end = date_col[-1], periods = 3)[1]
                        date_col.append(non_logged)
                        FL_col.append(np.nan)

        return pd.DataFrame(data = {'Flowmeter': FL_col}, index = pd.DatetimeIndex(date_col)).sort_index() 
        
    if data_type == 'Temperature':
        
        column_names = ['CH1', 'CH2', 'CH5', 'CH6']
        date_col = [[], [], [], []]
        CH_col = [[], [], [], []]
        
        for indx, variable in enumerate(column_names):
            
            is_first_log = True
            
            for date_log in list_date_log:
                log_name = log_folder + '/log-data/192.168.109.188/' + date_log['str'] + '/%s T ' % variable + date_log['str'] + '.log'
                
                # Check whether file exists
                if not os.path.isfile(log_name):
                    continue
                
                with open(log_name, 'r') as log_file:
                    
                    log_lines = log_file.readlines()
                    
                    # Collect a line of data for each logged instant
                    for line in log_lines:
                        line = line.replace('\n', '')
                        line = line.split(',')
                        
                        # Fill date column
                        date = pd.to_datetime(line[0].replace(' ','') + ' ' + line[1].replace(' ',''), format = "%d-%m-%y %H:%M:%S")
                        date_col[indx].append(date)
                        
                        # Fill the channel's data column.
                        CH_col[indx].append(float(line[2]))
                        
                        # Fill a line with NaN's if non-logged period is larger than 5 minutes
                        if is_first_log:
                            is_first_log = False
                            continue
                            
                        if (pd.Timedelta(date_col[indx][-1] - date_col[indx][-2]).seconds)/60.0 > 5:
                            non_logged = pd.date_range(start = date_col[indx][-2], end = date_col[indx][-1], periods = 3)[1]
                            date_col[indx].append(non_logged)
                            CH_col[indx].append(np.nan)
                    
        data_dict = {column_names[i]: CH_col[i] for i in range(len(column_names))}

        return [pd.DataFrame(CH_col[i], 
                             index = pd.DatetimeIndex(date_col[i]), 
                             columns = [column_names[i]]).sort_index()
                for i in range(4)]


def slice_timeseries(df, date_list, comparison_span = 3):
    '''
    This function slices a time-indexed timeseries df into multiple output timeseries 
    starting at given dates for a defined period of time.
    
    df: time-indexed single-column pandas dataframe.
    date_list: list of datetime objects describing where each df slice should start.
    comparison_span: time range of the data slice in hours.
    '''
    
    out_df_number = len(date_list)
    out_df = []
    
    for indx, start_date in enumerate(date_list):
        end_date = start_date + datetime.timedelta(hours = comparison_span)
        sliced_df = df[start_date:end_date]
        reset_time_index = [x - sliced_df.index[0] for x in sliced_df.index]
        out_df.append(pd.DataFrame(list(sliced_df), index = reset_time_index, columns = [sliced_df.name + '_%d' % indx]))
        
    return out_df


# Plots

def plot_data(log_folder = 'log/'):
    
    fig, ax = plt.subplots()
    ax.grid(True)
    
    stored_data = {}
    '''
    {
        maxigauge: {
            CH1:
            ...
            CH6:
        }
        Temperature: {
            CH1:
            CH2:
            CH5:
            CH6:
        }
        Flowmeter: 
    }
    '''
    
    def df_slices(start_daytime, data_type, comparison_span):
        
        # Identify specific data to be plotted
        channel = ''
        split_data_type = data_type.split(' ')
        if len(split_data_type) > 1:
            channel = split_data_type[1]
            data_type = split_data_type[0]
        
        # Convert start_daytime to date_list
        date_list = []
        for date in start_daytime.replace('\n', '').split(','):
            try:
                date_list.append(pd.to_datetime(date.strip(), format = "%d-%m-%y %H:%M:%S"))
            except:
                continue
                
        # If desired dataframe has not been ingested already, ingest, sort and store it
        if not data_type in stored_data.keys():
            df_all = log_parsing(log_folder, data_type)
            
            if data_type == 'Temperature':
                stored_data[data_type] = {}
                for i, ch in enumerate(['CH1', 'CH2', 'CH5', 'CH6']):
                    stored_data[data_type][ch] = df_all[i].sort_index()[ch]
                    
            if data_type == 'maxigauge':
                stored_data[data_type] = {}
                for i, ch in enumerate(['CH1', 'CH2', 'CH3', 'CH4', 'CH5', 'CH6']):
                    stored_data[data_type][ch] = df_all.sort_index()[ch]
                    
            if data_type == 'Flowmeter':
                stored_data[data_type] = df_all.sort_index()
        
        # Retrieve only desired data for use
        if channel:
            df = stored_data[data_type][channel]
        else:
            df = stored_data[data_type]
        
        # Timeslice the data
        sliced_df_list = slice_timeseries(df, date_list, comparison_span = comparison_span)
        
        # Prepare for plot
        out_df_list = []
        for i, df_slice in enumerate(sliced_df_list):
            try:
                out_df_list.append((df_slice.index.total_seconds(), 
                                    list(df_slice.iloc[:,0]), 
                                    date_list[i]))
            except:
                continue
                
        return out_df_list
    
    def format_timedelta_ticks(x, pos):                                                                                                                                                                                                                                                         
        d = datetime.timedelta(seconds=x)  
        return str(d).split(', ')[-1].strip() + '$_{+%s}$' % str(d.days)
    
    wd = widgets.IntText(value = 3,
                         description = 'Timespan (h):',
                          style = {'description_width': 'initial'},
                         disabled = False)
    
    dt = widgets.Textarea(value = '01-01-00 00:00:00',
                          description = 'Starting time',
                          style = {'description_width': 'initial'},
                          disabled = False)
    
    ty = widgets.Dropdown(options=['Flowmeter',
                                   'maxigauge CH1', 
                                   'maxigauge CH2', 
                                   'maxigauge CH3', 
                                   'maxigauge CH4', 
                                   'maxigauge CH5', 
                                   'maxigauge CH6', 
                                   'Temperature CH1',
                                   'Temperature CH2',
                                   'Temperature CH5',
                                   'Temperature CH6'],
                          value = 'maxigauge CH5',
                          description = 'Data type',
                          style = {'description_width': 'initial'},
                          #layout=Layout(width='50%', height='80px'),
                          disabled = False)
    
    sc = widgets.Checkbox(value = False,
                          description = 'Log scale',
                          disabled = False,
                          style = {'description_width': 'initial'},
                          indent = False)
    

    
    @widgets.interact(start_daytime = dt, comparison_span = wd, data_type = ty, log_scale = sc)
    def update_plot(start_daytime, data_type, comparison_span, log_scale):
        
        ax.cla()
        ax.grid(True)
        ax.set_title(data_type)
        
        out_df_list = df_slices(start_daytime, data_type, comparison_span)
        for out_df in out_df_list:
            ax.plot(out_df[0], out_df[1], label = out_df[2].strftime("%d-%m-%y %H:%M:%S"))
            
        ax.legend()
        ax.xaxis.set_major_formatter(plt.FuncFormatter(format_timedelta_ticks))
        ax.tick_params(axis='x', labelrotation = 25)
        ax.set_yscale('log' if log_scale else 'linear')
        ax.autoscale_view()
        fig.tight_layout()
        
        return

    return
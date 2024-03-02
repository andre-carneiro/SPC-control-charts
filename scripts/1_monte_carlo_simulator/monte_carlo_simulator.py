#data manipulation
import pandas as pd
import numpy as np
from tqdm import tqdm
import argparse

#path configuration
import os
import sys

#import input path and file and output path
sys.path.insert(-2, '../..')
from config import *
path_input = os.path.join(path_raw_data, r"db_original.xlsx")
path_output = path_indicators_processed

#functions from the app
from functions_body import *
from functions_indexes import *

np.random.seed(123) #generate random seed

#função principal:
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Parâmetros de execução da simulação")
    
    parser.add_argument("--sheet_name",
                        dest = "sheet_name",
                        type = str, 
                        default = "reference", 
                        help = "Aba da planilha a ser lida (default = 'reference')")
    
    parser.add_argument("--n_sim",
                        dest = "n_sim",
                        type = int, 
                        default = 10000, 
                        help = "Numero de simulacoes(default = 10,000)")    
    
    parser.add_argument("--deadline",
                        dest = "deadline",
                        type = int, 
                        default = 320, 
                        help = "Deadline da simulacao (default = 320)")  
    
    parser.add_argument("--range_time",
                        dest = "range_time",
                        type = int, 
                        default = 330, 
                        help = "Range da simulacao (default = 330)")
    
    args = parser.parse_args()
    
    #change args variables to variables
    sheet_name = args.sheet_name
    n_sim = args.n_sim
    deadline = args.deadline
    range_time = args.range_time
    
    print ("\nImport e criação dos dataframes auxiliares... ", end = "")
    
    #import and adjust dataframe
    df = import_df(path_input, sheet_name) #import dataframe
    df = adjust_df(df) #adjust initial dataframe
    df = planned_act_columns(df) #create planned column with start and end of activities
    
    if args.range_time == None:
        range_time = int(df.act_dur_plan_end.max()*1.1)
    
    #create empty dataframes
    df_result = create_result_output(n_sim) #create the dataframe that contain simulation, total duration, late project e total cost
    df_cpi = create_index_output(range_time, n_sim)
    df_spi = create_index_output(range_time, n_sim)
    df_tpi = create_index_output(range_time, n_sim)
    df_dpi = create_index_output(range_time, n_sim)
    list_indexes = [df_cpi, df_spi, df_tpi, df_dpi]
    name_indexes = ["cpi", "spi", "tpi", "dpi"]

    #calculate first indexes
    df_pv_tpd = calculate_PV_TPD (df, range_time = range_time) #calculate the planned ant TPD value arrays

    print ("OK", end = "\n\n")
    
    print(f'''Parâmetros da simulação:
        1) Planilha de referência: {sheet_name},
        2) Número de simulações: {n_sim},
        3) Período de deadline: {deadline},
        4) Dias de análise: {range_time}''', 
          end = "\n\n")

    
    for sim in tqdm(range(1, n_sim + 1), desc = "Execução da simulação"):

        # create auxiliary columns
        df = activity_duration (df) #create real duration column
        df = activity_cost (df) #create real cost column
        df = real_act_columns(df) #create real duration start and end of activities

        #update the result dataframe
        df_result = update_results(df_result, df, sim, deadline) 

        #adjust indexes
        df_ac_ev_ted = calculate_AC_EV_TED(df, range_time = range_time) #calculate the other three indexes
        df_index = concatenate_dataframes(df_pv_tpd, df_ac_ev_ted) #concatenate indexes

        #calculate indexes
        df_index = calculate_CPI_SPI(df_index)
        df_index = calculate_ES_TPI (df_index, range_time = range_time)
        df_index = calculate_ED_DPI (df_index, range_time = range_time)

        #concatenate and write obtained values for indexes
        for index, name in zip(list_indexes, name_indexes):
            index[f"sim_{sim}"] = df_index[name]
            
    print ("\nSalvando arquivos... ", end = "")
    
    export_df(list_indexes, df_result, name_indexes, path_output, sheet_name)
    
    print ("OK", end = "\n\n")
    
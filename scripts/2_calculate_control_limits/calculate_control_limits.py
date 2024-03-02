#data manipulation
import pandas as pd
import numpy as np
import argparse

#path configuration
import os
import sys

#import input and output paths
sys.path.insert(-2, '../..')
from config import *

#import input path
path_input = path_indicators_processed

#import output path
path_output_new_indexes = path_indicators_processed
path_output_control_limits = path_control_limits

#functions to the app
from functions_control_limits import *

#função principal:
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Parâmetros de execução da simulação")
    
    parser.add_argument("--include",
                        dest = "include",
                        type = str, 
                        default = "time", 
                        help = "Construção dos indicadores, baseado apenas nos de tempo (time) ou tempo e custo (cost) (default = 'time')")

    parser.add_argument("--scenario",
                        dest = "scenario",
                        type = str, 
                        default = "reference", 
                        help = "Cenário de input (reference ou sce1, ..., sce5) (default = 'reference')")

    parser.add_argument("--generate_control_limits",
                        dest = "generate_control_limits",
                        type = bool, 
                        default = False, 
                        help = "Cálculo do dataframe dos limites de controle (default = False)")

    parser.add_argument("--alpha",
                        dest = "alpha",
                        type = float, 
                        default = 0.05, 
                        help = "Parâmetro de erro alpha (default = 0.05)")

    args = parser.parse_args()

    #change args variables to variables
    scenario = args.scenario
    include = args.include
    generate_control_limits = args.generate_control_limits #caso não queira criar, irá apenas ajustar o df e criar os novos
    alpha = args.alpha

    print ("\nExecutando simulação... ", end = "\n\n")

    #import all input dataframes for the scenario
    df_result, df_cpi, df_spi, df_tpi, df_dpi = import_inputs(path_input, scenario)

    #treat and export tpi and dpi
    df_tpi, df_dpi = treat_export_tpi_dpi(df_tpi, df_dpi, scenario, path_output_new_indexes)

    #if one chooses to include time or cost into the new indexes and control limits 
    if include == "time":
        
        #create new indexes
        df_pdt_t, df_min_t, df_max_t, df_avg_t, df_med_t, df_amp_t, df_std_t, df_var_t = create_new_indexes(df_cpi, df_spi, df_tpi, df_dpi, include)
        
        # create auxiliary lists
        list_indexes_dfs = [df_pdt_t, df_min_t, df_max_t, df_avg_t, df_med_t, df_amp_t, df_std_t, df_var_t]
        list_indexes_names = ["pdt_t", "min_t", "max_t", "avg_t", "med_t", "amp_t", "std_t", "var_t"]

        #export new indexes
        export_new_indexes(list_indexes_dfs, list_indexes_names, scenario, path_output_new_indexes, include)

        if generate_control_limits == True:
            #create auxiliary lists with all indexes data
            list_indexes_all_dfs = [df_cpi, df_spi, df_tpi, df_dpi] + list_indexes_dfs
            list_indexes_all_names = ["cpi", "spi", "tpi", "dpi"] + list_indexes_names

            #create data frame for control limits
            df_control_limits = calculate_control_limits (list_indexes_all_dfs, list_indexes_all_names, include, alpha)

            #export control limits dataframe
            export_control_limits(df_control_limits, include, path_output_control_limits)

    elif include == "cost":
        
        #create new indexes
        df_pdt_c, df_min_c, df_max_c, df_avg_c, df_med_c, df_amp_c, df_std_c, df_var_c = create_new_indexes(df_cpi, df_spi, df_tpi, df_dpi, include)
        
        #create auxiliary lists
        list_indexes_dfs = [df_pdt_c, df_min_c, df_max_c, df_avg_c, df_med_c, df_amp_c, df_std_c, df_var_c]
        list_indexes_names = ["pdt_c", "min_c", "max_c", "avg_c", "med_c", "amp_c", "std_c", "var_c"]

        #export new indexes
        export_new_indexes(list_indexes_dfs, list_indexes_names, scenario, path_output_new_indexes, include)

        if generate_control_limits == True:
            #create auxiliary lists with all indexes data
            list_indexes_all_dfs = [df_cpi, df_spi, df_tpi, df_dpi] + list_indexes_dfs
            list_indexes_all_names = ["cpi", "spi", "tpi", "dpi"] + list_indexes_names

            #create data frame for control limits
            df_control_limits = calculate_control_limits (list_indexes_all_dfs, list_indexes_all_names, include, alpha)

            #export control limits dataframe
            export_control_limits(df_control_limits, include, path_output_control_limits)

    print ("Simulação concluida", end = "\n\n")
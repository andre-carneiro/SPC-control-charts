#data manipulation
import pandas as pd
import numpy as np
from tqdm import tqdm

#path configuration
import os
import sys

#import config to obtain paths
sys.path.insert(-2, '../..')
from config import *

#import input path
path_input_confusion_matrix = path_confusion_matrices

#import output path
path_output = path_performance_indicators

#functions to the app
from functions_performance_metrics import *

"""-------------------------- LIST OF FUNCTIONS ------------------ """
#função principal:
if __name__ == "__main__":

    for scenario in ["sce1", "sce2", "sce3", "sce4", "sce5"]:
        
        print (f"Executando simulação para o cenário {scenario}... ", end = "")

        #Import dos dataframes do cenário
        df_cpi, df_spi, df_tpi, df_dpi, df_min, df_max, df_pdt, df_avg, df_med, df_amp, df_std, df_var = import_confusion_matrix(path_input_confusion_matrix, scenario)
        
        #Criação das listas auxiliares
        list_df = [df_cpi, df_spi, df_tpi, df_dpi, df_min, df_max, df_pdt, df_avg, df_med, df_amp, df_std, df_var]
        list_name = ["cpi", "spi", "tpi", "dpi", "min_t", "max_t", "pdt_t", "avg_t", "med_t", "amp_t", "std_t", "var_t"]

        for df, indicator_name in zip(list_df, list_name):
    
            #slice the df from 20 to 20 review periods
            df = slice_df_20(df)
            
            #create temporary dataframes with performance metrics
            tmp_project_level = calculate_project_level_metrics(df)
            tmp_period_level = calculate_period_level_metrics(df)

            #concatenate and adjust dataframes
            tmp = concatenate_adjust_df(tmp_project_level, tmp_period_level, scenario, indicator_name)
            
            #concatenate all 
            if (indicator_name == "cpi") and (scenario == "sce1"):
                df_final = tmp.copy()
            else:
                df_final = pd.concat([df_final, tmp]).copy()

        print("OK\n\n")    
        
    print ("Simulação concluida")

    export_performance_metrics(df_final, path_output)
#data manipulation
import pandas as pd
import numpy as np
from tqdm import tqdm
import argparse

#path configuration
import os
import sys

#import config to obtain paths
sys.path.insert(-2, '../..')
from config import *

#import input path
path_input_indicators = path_indicators_processed
path_input_control_limits = path_control_limits

#import output path
path_output = path_confusion_matrices

#functions to the app
from functions_confusion_matrix import *

"""-------------------------- LIST OF FUNCTIONS ------------------ """
#função principal:
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Parâmetros de execução da simulação")
    
    parser.add_argument("--include",
                        dest = "include",
                        type = str, 
                        default = "time", 
                        help = "Se as analises englobam tanto indicador de custo ou não (default = 'time')")
    
    parser.add_argument("--scenario",
                        dest = "scenario",
                        type = str, 
                        default = "sce1", 
                        help = "Cenário em que deseja-se criar a simulação (default = 'sce1')")    

    
    args = parser.parse_args()
    
    #change args variables to variables
    include = args.include
    scenario = args.scenario
    
    print (f"\nExecutando simulação para o cenário {scenario}...", end = "\n\n")

    #import dos dataframes e de controle de limite
    df_result, df_cpi, df_spi, df_tpi, df_dpi, df_min, df_max, df_pdt, df_avg, df_med, df_amp, df_std, df_var = import_indicators(path_input_indicators, scenario, include = "time")
    df_control_limits = import_control_limits(path_input_control_limits, include = "time")

    #criação de listas auxiliares
    list_df = [df_cpi, df_spi, df_tpi, df_dpi, df_min, df_max, df_pdt, df_avg, df_med, df_amp, df_std, df_var]
    list_name = ["cpi", "spi", "tpi", "dpi", "min_t", "max_t", "pdt_t", "avg_t", "med_t", "amp_t", "std_t", "var_t"]

    #iteração para criação e export da matriz de confusão
    for df_index, name_col in zip(list_df, list_name):
        df_confusion_matrix =  create_confusion_matrix (df_result, df_index, df_control_limits, name_col).copy()
        export_confusion_matrix (df_confusion_matrix, name_col, path_output, scenario, include)

    print ("Simulação concluida", end = "\n\n")
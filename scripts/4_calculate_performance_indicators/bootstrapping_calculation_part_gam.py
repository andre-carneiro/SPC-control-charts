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
from functions_bootstrapping_part import *

np.random.seed(122) #generate random seed

"""-------------------------- LIST OF FUNCTIONS ------------------ """
#função principal:
if __name__ == "__main__":

    for distribution in ["_gamma"]: 
    
        if distribution == "":
            distribution_name = "Triangular"
        if distribution == "_gamma":
            distribution_name = "Gamma"
        if distribution == "_cmpoisson":
            distribution_name = "CMP"

        for scenario in ["sce1", "sce2", "sce3", "sce4", "sce5"]:
            
            print (f"Executando simulação para a distribuição {distribution_name} e cenário {scenario}... ")

            #Import dos dataframes do cenário
            df_spi, df_tpi, df_dpi, df_min, df_max, df_pdt, df_avg, df_med = import_confusion_matrix(path_input_confusion_matrix, scenario, distribution)
            
            #Criação das listas auxiliares
            list_df = [df_spi, df_tpi, df_dpi, df_min, df_max, df_pdt, df_avg, df_med]
            list_name = ["spi", "tpi", "dpi", "min_t", "max_t", "pdt_t", "avg_t", "med_t"]

            for df, indicator_name in zip(list_df, list_name):
        
                #slice the df from 20 to 20 review periods
                df_sliced = slice_df_20(df)

                #criação do resampling:
                for index_boots in tqdm(range (300), desc = f"distribution: {distribution_name} | scenario: {scenario} | indicator {indicator_name}"):

                    #resampling
                    df_sampled = df_sliced.sample(frac = 1.0, axis = 1, random_state = index_boots, replace = True)
                    df_sampled.columns = np.arange(0,10000,1)
                
                    #create temporary dataframes with performance metrics
                    tmp_project_level = calculate_project_level_metrics(df_sampled)
                    tmp_period_level = calculate_period_level_metrics(df_sampled)

                    #concatenate and adjust dataframes
                    tmp = concatenate_adjust_df(tmp_project_level, tmp_period_level, scenario, indicator_name, distribution_name, index_boots)
                    
                    #concatenate all 
                    if (indicator_name == "spi") and (scenario == "sce1") and (distribution_name == distribution_name) and (index_boots == 0):
                        df_final = tmp.copy()
                    else:
                        df_final = pd.concat([df_final, tmp])

            print("\n")    
            
    print ("Simulação concluida")

    export_performance_metrics(df_final, path_output, distribution_name)
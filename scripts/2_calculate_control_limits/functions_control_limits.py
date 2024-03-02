#data manipulation
import pandas as pd
import numpy as np

#path configuration
import os
import sys

#import input and output paths
sys.path.insert(-2, '../..')
from config import *

"""-------------------------- LIST OF FUNCTIONS ------------------ """

def import_inputs(path_input, scenario):
    """
    Função que importa todos os dados de input de um determinaro cenário
    """
    #import input dataframes (results and indexes of the simulation)
    df_result = pd.read_pickle(os.path.join(path_input, r"{}_result_cmpoisson.pkl".format(scenario)))
    df_cpi = pd.read_pickle(os.path.join(path_input, r"{}_cpi_cmpoisson.pkl".format(scenario)))
    df_spi = pd.read_pickle(os.path.join(path_input, r"{}_spi_cmpoisson.pkl".format(scenario)))
    df_tpi = pd.read_pickle(os.path.join(path_input, r"{}_tpi_cmpoisson.pkl".format(scenario)))
    df_dpi = pd.read_pickle( os.path.join(path_input, r"{}_dpi_cmpoisson.pkl".format(scenario)))

    return (df_result, df_cpi, df_spi, df_tpi, df_dpi)


def treat_export_tpi_dpi(df_tpi, df_dpi, scenario, path_output_new_indexes):
    """
    função que remove os valores ausentes de tpi e dpi do dataframe e exporta os novos resultados 
    """    
    df_tpi.fillna(method = "ffill", inplace = True)
    df_tpi.to_pickle(os.path.join(path_output_new_indexes, r"{}_tpi_cmpoisson.pkl".format(scenario)))
    
    df_dpi.fillna(method = "ffill", inplace = True)
    df_dpi.to_pickle(os.path.join(path_output_new_indexes, r"{}_dpi_cmpoisson.pkl".format(scenario)))

    return df_tpi, df_dpi

def create_new_indexes(df_cpi, df_spi, df_tpi, df_dpi, include = "time"):
    """
    Função que cria os dataframes com a combinação dos novos indices.

    Input: os 4 dataframes padrões de indicadores e se deseja que a combinação seja apenas com tempo se deve ter custo
    """

    if include == "time":
        #create dataframe that is only time indexes
        df_concat = pd.concat([df_spi, df_tpi, df_dpi])
        df_pdt = df_spi*df_tpi*df_dpi #multiplies each of the columns
    
    if include == "cost":
        #create dataframe that includes cost index
        df_concat = pd.concat([df_cpi, df_spi, df_tpi, df_dpi])
        df_pdt = df_cpi*df_spi*df_tpi*df_dpi #deveria preencher ou deixar que o percentil pegue os valores existentes, como nos demais?

    #min and max
    df_min = df_concat.groupby(df_concat.index).min()
    df_max = df_concat.groupby(df_concat.index).max()

    #centrality
    df_avg = df_concat.groupby(df_concat.index).mean()
    df_med = df_concat.groupby(df_concat.index).median()

    #variability
    df_amp = df_max - df_min
    df_std = df_concat.groupby(df_concat.index).std()
    df_var = df_concat.groupby(df_concat.index).var()

    return (df_pdt, df_min, df_max, df_avg, df_med, df_amp, df_std, df_var)

def export_new_indexes (list_indexes_dfs, list_indexes_names, scenario, path_output, include = "time"):
    """
    Função que exporta os novos indicadores
    """ 
    for df, name in zip(list_indexes_dfs, list_indexes_names):
        df.to_pickle(os.path.join(path_output, r"{}_{}_cmpoisson.pkl".format(scenario, name)))
    
    return

def calculate_control_limits(list_indexes_all_dfs, list_indexes_all_names, include = "time", alpha = 0.05):
    """
    Função que cria os limites de controle de acordo com o include 
    """
    #create the control limits dataframe
    df_control_limits = pd.DataFrame()

    if include == "time":
        for df, col_name in zip(list_indexes_all_dfs, list_indexes_all_names):
            df_control_limits[col_name] = df.quantile(q = alpha, axis = 1)

    if include == "cost":
        for df, col_name in zip(list_indexes_all_dfs, list_indexes_all_names):
            df_control_limits[col_name] = df.quantile(q = alpha, axis = 1)

    return df_control_limits

def export_control_limits(df_control_limits, include, path_output):
    """
    Função que exporta o dataframe de limites de controle
    """ 
    if include == "time":
        df_control_limits.to_pickle(os.path.join(path_output, r"df_control_limits_t_cmpoisson.pkl"))
    if include == "cost":
        df_control_limits.to_pickle(os.path.join(path_output, r"df_control_limits_c_cmpoisson.pkl"))
    return
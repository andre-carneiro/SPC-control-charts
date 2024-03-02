#data manipulation
import pandas as pd
import numpy as np
from tqdm import tqdm

#path configuration
import os


"""-------------------------- LIST OF FUNCTIONS ------------------ """

def import_indicators(path_input_indicators, scenario, include = "time"):
    """
    Função que importa todas as matrizes de indicadores de um determinado cenário
    """
    if include == "time":
        #import input dataframes (results and indexes of the simulation)
        df_result = pd.read_pickle(os.path.join(path_input_indicators, r"{}_result_cmpoisson.pkl".format(scenario)))
        df_cpi = pd.read_pickle(os.path.join(path_input_indicators, r"{}_cpi_cmpoisson.pkl".format(scenario)))
        df_spi = pd.read_pickle(os.path.join(path_input_indicators, r"{}_spi_cmpoisson.pkl".format(scenario)))
        df_tpi = pd.read_pickle(os.path.join(path_input_indicators, r"{}_tpi_cmpoisson.pkl".format(scenario)))
        df_dpi = pd.read_pickle(os.path.join(path_input_indicators, r"{}_dpi_cmpoisson.pkl".format(scenario)))
        df_min = pd.read_pickle(os.path.join(path_input_indicators, r"{}_min_t_cmpoisson.pkl".format(scenario)))
        df_max = pd.read_pickle(os.path.join(path_input_indicators, r"{}_max_t_cmpoisson.pkl".format(scenario)))
        df_pdt = pd.read_pickle(os.path.join(path_input_indicators, r"{}_pdt_t_cmpoisson.pkl".format(scenario)))
        df_avg = pd.read_pickle(os.path.join(path_input_indicators, r"{}_avg_t_cmpoisson.pkl".format(scenario)))
        df_med = pd.read_pickle(os.path.join(path_input_indicators, r"{}_med_t_cmpoisson.pkl".format(scenario)))
        df_amp = pd.read_pickle(os.path.join(path_input_indicators, r"{}_amp_t_cmpoisson.pkl".format(scenario)))
        df_std = pd.read_pickle(os.path.join(path_input_indicators, r"{}_std_t_cmpoisson.pkl".format(scenario)))
        df_var = pd.read_pickle(os.path.join(path_input_indicators, r"{}_var_t_cmpoisson.pkl".format(scenario)))
    
    elif include == "cost":
        #import input dataframes (results and indexes of the simulation)
        df_result = pd.read_pickle(os.path.join(path_input_indicators, r"{}_result.pkl".format(scenario)))
        df_cpi = pd.read_pickle(os.path.join(path_input_indicators, r"{}_cpi.pkl".format(scenario)))
        df_spi = pd.read_pickle(os.path.join(path_input_indicators, r"{}_spi.pkl".format(scenario)))
        df_tpi = pd.read_pickle(os.path.join(path_input_indicators, r"{}_tpi.pkl".format(scenario)))
        df_dpi = pd.read_pickle(os.path.join(path_input_indicators, r"{}_dpi.pkl".format(scenario)))
        df_min = pd.read_pickle(os.path.join(path_input_indicators, r"{}_min_c.pkl".format(scenario)))
        df_max = pd.read_pickle(os.path.join(path_input_indicators, r"{}_max_c.pkl".format(scenario)))
        df_pdt = pd.read_pickle(os.path.join(path_input_indicators, r"{}_pdt_c.pkl".format(scenario)))
        df_avg = pd.read_pickle(os.path.join(path_input_indicators, r"{}_avg_c.pkl".format(scenario)))
        df_med = pd.read_pickle(os.path.join(path_input_indicators, r"{}_med_c.pkl".format(scenario)))
        df_amp = pd.read_pickle(os.path.join(path_input_indicators, r"{}_amp_c.pkl".format(scenario)))
        df_std = pd.read_pickle(os.path.join(path_input_indicators, r"{}_std_c.pkl".format(scenario)))
        df_var = pd.read_pickle(os.path.join(path_input_indicators, r"{}_var_c.pkl".format(scenario)))
    
    return (df_result, df_cpi, df_spi, df_tpi, df_dpi, df_min, df_max, df_pdt, df_avg, df_med, df_amp, df_std, df_var)

#import control limit
def import_control_limits(path_input_control_limits, include = "time"):
    """
    Função que importa o df de limite de controle
    """
    if include == "time":
        df_control_limits = pd.read_pickle(os.path.join(path_input_control_limits, "df_control_limits_t_cmpoisson.pkl"))

    elif include == "cost":
        df_control_limits = pd.read_pickle(os.path.join(path_input_control_limits, "df_control_limits_c.pkl"))

    return df_control_limits

def create_confusion_matrix (df_result, df_index, df_control_limits, name_col_control_limits):
    """
    Função que cria a matriz de confusão para um indicador especificado
    """
    #obtenção da quantidade de colunas (numero de simulações) e de linhas (range da simulação)
    n_sim = len(df_index.columns)
    n_range = len(df_index)
    
    #criação do df da matriz de confusão
    df_confusion_matrix = pd.DataFrame(data = np.nan,
                                       index=list(range(1, n_range + 1)),
                                       columns = ["sim_" + str(int) for int in list(range(1,n_sim + 1))])

    #iterate over the columns
    for index_col in tqdm(range (1,n_sim + 1), desc = f"Criação da matriz de confusão do indicador: {name_col_control_limits}"): #percorre index da coluna do 1 ao 10k
        #col of analysis
        col = f"sim_{index_col}"
        #conditional for the signal
        cond_signal_false = df_index[col] >= df_control_limits[name_col_control_limits] #LC obs >= LC ref - observado acima da referencia (esta em dia)
        cond_signal_true = df_index[col] < df_control_limits[name_col_control_limits] #LC obs < LC ref - observado abaixo da referencia (esta atrasado)
        
        if df_result.loc[index_col - 1, "late_project"] == True: #caso o projeto atrase
            df_confusion_matrix.loc[cond_signal_true, col] = "TP" #sinalizou e atrasou
            df_confusion_matrix.loc[cond_signal_false, col] = "FN" #não sinalizou e atrasou
        
        else: #projeto não atrasou
            df_confusion_matrix.loc[cond_signal_false, col] = "TN" #não sinalizou e não atrasou
            df_confusion_matrix.loc[cond_signal_true, col] = "FP" #sinalizou e não atrasou

    return df_confusion_matrix    
    
def export_confusion_matrix (df_confusion_matrix, name_col_control_limits, path_output, scenario, include = "time"):
    """
    Função que exporta a matriz de confusão
    """
    if include == "time":
        df_confusion_matrix.to_pickle(os.path.join(path_output, r"df_confusion_matrix_{}_{}_cmpoisson.pkl".format(scenario, name_col_control_limits)))
    elif include == "cost":
        df_confusion_matrix.to_pickle(os.path.join(path_output, r"df_confusion_matrix_{}_{}_cmpoisson.pkl".format(scenario, name_col_control_limits)))
    return
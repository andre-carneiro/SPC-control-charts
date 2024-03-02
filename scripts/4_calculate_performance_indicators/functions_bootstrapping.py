#data manipulation
import pandas as pd
import numpy as np
from tqdm import tqdm

#path configuration
import os

"""-------------------------- LIST OF FUNCTIONS ------------------ """

def import_confusion_matrix(path_input_confusion_matrix, scenario, distribution):
    """
    Função que importa todas as matrizes de indicadores de um determinado cenário
    """
    #import input dataframes (results and indexes of the simulation)
    df_spi = pd.read_pickle(os.path.join(path_input_confusion_matrix, r"df_confusion_matrix_{}_spi{}.pkl".format(scenario, distribution)))
    df_tpi = pd.read_pickle(os.path.join(path_input_confusion_matrix, r"df_confusion_matrix_{}_tpi{}.pkl".format(scenario, distribution)))
    df_dpi = pd.read_pickle(os.path.join(path_input_confusion_matrix, r"df_confusion_matrix_{}_dpi{}.pkl".format(scenario, distribution)))
    df_min = pd.read_pickle(os.path.join(path_input_confusion_matrix, r"df_confusion_matrix_{}_min_t{}.pkl".format(scenario, distribution)))
    df_max = pd.read_pickle(os.path.join(path_input_confusion_matrix, r"df_confusion_matrix_{}_max_t{}.pkl".format(scenario, distribution)))
    df_pdt = pd.read_pickle(os.path.join(path_input_confusion_matrix, r"df_confusion_matrix_{}_pdt_t{}.pkl".format(scenario, distribution)))
    df_avg = pd.read_pickle(os.path.join(path_input_confusion_matrix, r"df_confusion_matrix_{}_avg_t{}.pkl".format(scenario, distribution)))
    df_med = pd.read_pickle(os.path.join(path_input_confusion_matrix, r"df_confusion_matrix_{}_med_t{}.pkl".format(scenario, distribution)))
        
    return (df_spi, df_tpi, df_dpi, df_min, df_max, df_pdt, df_avg, df_med)

def slice_df_20 (df):
    
    #slice no df para pegar apenas os valores multiplos de 20
    df = df.loc[range (20,320,20), :].copy()

    return df

def calculate_project_level_metrics(df):
    """
    Função que calcula os indicadores de performance a nível de projeto (apenas se assinala antes do período)
    """
    #substitui todos os valores de não aviso posteriores, por valores de aviso (TP e FP)
    for col in df.columns:
        #reseta a condicional
        cond_all_TP = False
        cond_all_FP = False
        for row in range (20,320,20):
            #ativação da condicional
            if df.loc[row, col] == "TP":
                cond_all_TP = True
            if df.loc[row, col] == "FP":
                cond_all_FP = True
            #substitui os valores se a condicional for satisfeita
            if cond_all_TP == True:
                df.loc[row, col] = "TP"
            if cond_all_FP == True:
                df.loc[row, col] = "FP"
   
    #cria o df de value counts
    tmp_project_level = df.apply(pd.Series.value_counts, axis=1)

    # project caracteristics
    tmp_project_level["total_projects"] = tmp_project_level.sum(axis = 1)
    tmp_project_level["late_projects"] = tmp_project_level["TP"] + tmp_project_level["FN"]
    tmp_project_level["on_time_projects"] = tmp_project_level["TN"] + tmp_project_level["FP"]

    #probability of delaying
    tmp_project_level["probability_late_project"] = tmp_project_level["late_projects"]/tmp_project_level["total_projects"]
    tmp_project_level["probability_on_time_project"] = tmp_project_level["on_time_projects"]/tmp_project_level["total_projects"]

    #probability of, until the time, the project signals (or not)
    tmp_project_level["probability_signal"] = (tmp_project_level["TP"] + tmp_project_level["FP"])/tmp_project_level["total_projects"]
    tmp_project_level["probability_no_signal"] = (tmp_project_level["TN"] + tmp_project_level["FN"])/tmp_project_level["total_projects"]

    #performance metrics
    tmp_project_level["detection_performance"] = tmp_project_level["TP"]/tmp_project_level["late_projects"]
    tmp_project_level["probability_overreaction"] = tmp_project_level["FP"]/tmp_project_level["on_time_projects"]
    tmp_project_level["efficiency"] = tmp_project_level["detection_performance"]*tmp_project_level["probability_late_project"]/tmp_project_level["probability_signal"]
    tmp_project_level["reliability"] = (1-tmp_project_level["probability_overreaction"])*tmp_project_level["probability_on_time_project"]/tmp_project_level["probability_no_signal"]
    tmp_project_level["accuracy"] = (tmp_project_level["TP"] + tmp_project_level["TN"])/tmp_project_level["total_projects"]

    return tmp_project_level[["detection_performance", "probability_overreaction", "efficiency", "reliability", "accuracy"]].copy()

def calculate_period_level_metrics(df):
    """
    Função que calcula os indicadores de performance a nível de período (acumulado/densidade)
    """
    #cria o dataframe de value_counts
    tmp_period_level = df.apply(pd.Series.value_counts, axis=1)

    #cria as colunas de value counts acumulados
    for index in range (20, 320, 20):
        tmp_period_level.loc[index, "TP_acum"] = tmp_period_level.loc[:index, "TP"].sum()
        tmp_period_level.loc[index, "FP_acum"] = tmp_period_level.loc[:index, "FP"].sum()
        tmp_period_level.loc[index, "TN_acum"] = tmp_period_level.loc[:index, "TN"].sum()
        tmp_period_level.loc[index, "FN_acum"] = tmp_period_level.loc[:index, "FN"].sum()

    # project caracteristics
    tmp_period_level["total_projects"] = tmp_period_level[["TP", "FP", "TN", "FN"]].sum(axis = 1)
    tmp_period_level["late_projects"] = tmp_period_level["TP"] + tmp_period_level["FN"]
    tmp_period_level["on_time_projects"] = tmp_period_level["TN"] + tmp_period_level["FP"]

    #performance indicators
    tmp_period_level["signal_density"] = tmp_period_level["TP_acum"]/tmp_period_level["late_projects"]
    tmp_period_level["signal_redundancy"] = tmp_period_level["FP_acum"]/tmp_period_level["on_time_projects"]
    tmp_period_level["signal_efficiency"] = tmp_period_level["TP_acum"]/(tmp_period_level["TP_acum"] + tmp_period_level["FP_acum"])
    tmp_period_level["signal_reliability"] = tmp_period_level["TN_acum"]/(tmp_period_level["TN_acum"] + tmp_period_level["FN_acum"])
    tmp_period_level["signal_accuracy"] = (tmp_period_level["TP_acum"] + tmp_period_level["TN_acum"])/tmp_period_level["total_projects"]

    return tmp_period_level[["signal_density", "signal_redundancy", "signal_efficiency", "signal_reliability", "signal_accuracy"]]


def concatenate_adjust_df(tmp_project_level, tmp_period_level, scenario, indicator_name, distribution, index_boots):
    """
    Função que concatena as metricas de performance e cria as colunas auxiliares
    """
    #concatenate performance metrics
    tmp_melt = pd.concat([tmp_project_level, tmp_period_level], axis = 1)
    
    #auxiliary columns
    tmp_melt["scenario"] = scenario
    tmp_melt["indicator"] = indicator_name
    tmp_melt["time"] = tmp_melt.index
    tmp_melt["distribution"] = distribution
    tmp_melt["bootstrapping"] = index_boots

    #melt df
    tmp_melt = pd.melt(tmp_melt, 
                        id_vars = ["time", "scenario", "indicator", "distribution", "bootstrapping"], 
                        var_name = "performance_metric",
                        value_name = "value")
    return tmp_melt

def export_performance_metrics(df_final, path_output):
    """
    Função que exporta o df de métricas de performance
    """
    df_final.to_pickle(os.path.join(path_output, r"df_performance_metrics_boots.pkl"))
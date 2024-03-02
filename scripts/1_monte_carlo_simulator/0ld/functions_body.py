#data manipulation
import pandas as pd
import numpy as np

#path configuration
import os
import sys

"""-------------------------- LIST OF FUNCTIONS ------------------ """

def import_df (path_input, sheet_name):
    """
    Função que lê o caminho do arquivo e retorna o dataframe de atividades
    """
    df = pd.read_excel(path_input, sheet_name, header = 1, dtype = "str")
    df.drop("Unnamed: 0", axis = 1, inplace = True)
    
    return df.copy()
    
    
def adjust_df (df):
    """
    Função que ajusta o nome das colunas, e a tipologia dos dados
    """
    #adjust columns name
    df.columns = ["activity", "predecessor", "min_time", "avr_time", "max_time", "expectation",
                  "std_dev", "inflection", "intercept", "parameter", "avr_cost"]
    
    #set type as float
    df[df.columns.difference(['predecessor'])] = df[df.columns.difference(['predecessor'])].astype("float")
    
    #set type as str (due to the ,)
    df.loc[:, 'predecessor']= df.loc[:, 'predecessor'].astype("str")

    #transform the column of str into a column of float's list
    df.loc[: ,"predecessor"] = df.predecessor.apply(lambda x: x.split(", "))
    
    #auxiliary column for other functions
    df["index_aux"] = range(0, df.shape[0])
    
    return df.copy()


def planned_act_columns (df):
    """
    Função que cria as colunas de começo e termino teórico das atividades do projeto
    """
    #criação da coluna auxiliar para utilização do loc e do tamanho da lista de predecessores
    df.loc[: , "predecessor_len"] = df.predecessor.apply(lambda x: len(x))
    
    #buscar linha a linha o começo e o fim de cada atividade
    for index, row in df.iterrows():
        #caso a linha do predecessor seja vazia ou ausente, começará no 0
        if (row.predecessor[0] == "nan") or (row.predecessor[0] == 0):
            df.loc[df.index_aux == index, "act_dur_plan_start"] = 0
            df.loc[df.index_aux == index, "act_dur_plan_end"] = df.loc[df.index_aux == index, "act_dur_plan_start"] +\
                                                                df.loc[df.index_aux == index, "avr_time"]
        
        #caso a linha não seja vazia, percorrer as atividades predecessoras e pegar a maior data de término
        else:
            list_max = [] #lista auxiliar para pegar os valores de término anteriores
            for n_pred in range (row.predecessor_len): #percorre o numero da atividade predecessora
                list_max.append(int(df.loc[df.activity == int(row.predecessor[n_pred]), "act_dur_plan_end"])) #armazena o valor do termino da atividade na lista
                            
            df.loc[df.index_aux == index, "act_dur_plan_start"] = max(list_max)
            df.loc[df.index_aux == index, "act_dur_plan_end"] = df.loc[df.index_aux == index, "act_dur_plan_start"] +\
                                                                df.loc[df.index_aux == index, "avr_time"]            

    #drop coluna auxiliar
    df.drop(["predecessor_len"], axis = 1, inplace = True)
    
    return df.copy()


def activity_duration (df, dist = "triangular"):
    """
    Função que cria a coluna de duração da atividade, baseado na distribuição de probabilidade
    """
    if dist == "triangular":
        df["act_dur"] = np.random.triangular(df.min_time, df.avr_time, df.max_time)
        
    return df.copy()


def activity_cost (df, teta = 0.2):
    """
    Função que cria a coluna de custo da atividade, baseado na regressão linear e na distribuição uniforme
    A distribuição uniforme é aplicada apenas para as atividades 10, 11, 12, 13 e 14
    """
    
    df["act_cost"] = df.intercept + df.parameter*df.act_dur 
    
    df["act_cost_uniform"] = np.random.uniform(df.intercept*(1-teta), df.intercept*(1+teta))

    df.loc[(df.activity == 10) | (df.activity == 11) | (df.activity == 12) |
           (df.activity == 13) |(df.activity == 14), "act_cost"] = df.loc[:, "act_cost_uniform"]
    
    df.drop(["act_cost_uniform"], axis = 1, inplace = True)
    
    return df.copy()


def real_act_columns (df):
    """
    Função que cria as colunas de começo e termino real das atividades do projeto
    """
    #criação da coluna auxiliar para utilização do loc e do tamanho da lista de predecessores
    df.loc[: , "predecessor_len"] = df.predecessor.apply(lambda x: len(x))
    
    #buscar linha a linha o começo e o fim de cada atividade
    for index, row in df.iterrows():
        #caso a linha do predecessor seja vazia ou ausente, começará no 0
        if (row.predecessor[0] == "nan") or (row.predecessor[0] == 0):
            df.loc[df.index_aux == index, "act_dur_real_start"] = 0
            df.loc[df.index_aux == index, "act_dur_real_end"] = df.loc[df.index_aux == index, "act_dur_real_start"] +\
                                                                df.loc[df.index_aux == index, "act_dur"]
        
        #caso a linha não seja vazia, percorrer as atividades predecessoras e pegar a maior data de término
        else:
            list_max = [] #lista auxiliar para pegar os valores de término anteriores
            for n_pred in range (row.predecessor_len): #percorre o numero da atividade predecessora
                list_max.append(float(df.loc[df.activity == int(row.predecessor[n_pred]), "act_dur_real_end"])) #armazena o valor do termino da atividade na lista
                            
            df.loc[df.index_aux == index, "act_dur_real_start"] = max(list_max)
            df.loc[df.index_aux == index, "act_dur_real_end"] = df.loc[df.index_aux == index, "act_dur_real_start"] +\
                                                                df.loc[df.index_aux == index, "act_dur"]            

    #drop coluna auxiliar
    df.drop(["predecessor_len"], axis = 1, inplace = True)
    
    return df.copy()

def concatenate_arrays(tuple_arrays, arrays_name):
    """
    Função que concatena as arrays em formato de dataframe
    """
    
    df = pd.DataFrame(np.transpose(np.stack(tuple_arrays, axis = 0)), columns = arrays_name)
    
    return df.copy()

def concatenate_dataframes(df1, df2, drop = True):
    """
    Função que concatena os dataframes e exclui a primeira linha de observação, de valor nulo    
    """
    df = df1.join(df2)
    
    #primeiras arrays possuem valor 0 no índice 0 e precisam ser dropadas
    if drop == True:
        df.drop(0, inplace = True)
    
    return df.copy()

def create_index_output(range_time, n_sim):
    """
    Função que cria o dataframe vazio com o tamanho das linhas (range_time) e o número de simulações (n_sim)
    """
    
    df = pd.DataFrame(index = range(1, range_time+1), columns = [f"sim_{i}" for i in range (1, n_sim+1)])
    
    return df.copy()

def create_result_output(n_sim):
    """
    Função que cria o dataframe vazio com o tamanho das linhas (range_time) e o número de simulações (n_sim)
    """
    
    df = pd.DataFrame(index = range(1, n_sim+1), columns = ["simulation", "total_duration", "late_project", "total_cost"])
    df.simulation = range(1, n_sim+1)
    
    return df.copy()

def update_results(df_result, df, sim, deadline):
    """
    Função que atualiza o dataframe de resultado com a simulação, total duration, late project e total cost
    """
    df_result.loc[df_result.simulation == sim, "total_duration"] = df.act_dur_real_end.max()
    df_result.loc[df_result.simulation == sim, "late_project"] = (df_result.loc[df_result.simulation == sim, "total_duration"] > deadline)
    df_result.loc[df_result.simulation == sim, "total_cost"] = df.act_cost.sum()
    
    return df_result.copy()

def export_df(list_indexes, df_result, name_indexes, path_output, sheet_name):
    """
    Função que exporta o df
    """
    #adiciona o result a ser exportado também
    list_indexes.append(df_result)
    name_indexes.append("result")
    
    #exporta no formato de sce1_cpi ou reference_dpi ou reference_result
    for index, name in enumerate (name_indexes):
        list_indexes[index].to_pickle(os.path.join(path_output,"{}_{}.pkl".format(sheet_name, name))) 
        
    return

def export_df_iteration(list_indexes, df_result, name_indexes, path_output, sheet_name, seed, n_sim):
    """
    Função que exporta o df
    """
    #adiciona o result a ser exportado também
    list_indexes.append(df_result)
    name_indexes.append("result")
    
    #exporta no formato de sce1_cpi ou reference_dpi ou reference_result
    for index, name in enumerate (name_indexes):
        list_indexes[index].to_pickle(os.path.join(path_output,"{}_{}_seed{}_{}.pkl".format(sheet_name, name, seed, n_sim))) 
        
    return
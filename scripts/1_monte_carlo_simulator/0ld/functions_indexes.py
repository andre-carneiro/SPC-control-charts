#data manipulation
import pandas as pd
import numpy as np

#path configuration
import os
import sys

from functions_body import concatenate_arrays, concatenate_dataframes

"""-------------------------- LIST OF FUNCTIONS ------------------ """

def calculate_PV_TPD (df, range_time = None):
    """
    Função que lê o dataframe e as atividades sequenciadas e calcula o PV e o TED.
    Caso o range do cálculo dos indicadores não seja especificado, será calculado para
    10% a mais da data de término planejada
    """    
    if range_time == None:
        range_time = int(df.act_dur_plan_end.max()*1.1)    
    
    n_act = df.shape[0] #n de atividades a serem percorridas
    pv_array = np.zeros(range_time+1) #criação do array float com o tempo de analise
    tpd_array = np.zeros(range_time+1) #array de float do tpd
    
    for time in range(1, range_time + 1): #percorre de 1 a 330
        
        for act in range(n_act): #percorre as atividades do projeto para somar o valor do 
#             print ("time: ", time, "act: ", act)
            
            if float(df.loc[df.index_aux == act, "act_dur_plan_start"]) > time: 
                #quebra o loop caso o inicio da atividade (ex 16) seja maior que o período de analise (15)
                break
            
            elif float(df.loc[df.index_aux == act, "act_dur_plan_end"]) <= time:
                pv_array[time] = pv_array[time] + df.loc[df.index_aux == act, "avr_cost"]
                
                tpd_array[time] = tpd_array[time] + df.loc[df.index_aux == act, "avr_time"]
            
            else:
                pv_array[time] = pv_array[time] + (time - df.loc[df.index_aux == act, "act_dur_plan_start"])/\
                                (df.loc[df.index_aux == act, "act_dur_plan_end"] - df.loc[df.index_aux == act, "act_dur_plan_start"])*\
                                (df.loc[df.index_aux == act, "avr_cost"])
                
                tpd_array[time] = tpd_array[time] + (time - df.loc[df.index_aux == act, "act_dur_plan_start"])/\
                                (df.loc[df.index_aux == act, "act_dur_plan_end"] - df.loc[df.index_aux == act, "act_dur_plan_start"])*\
                                (df.loc[df.index_aux == act, "avr_time"])
#         print ("valor do PV: ", pv_array[time], end = "\n\n")
    
    df_array = concatenate_arrays((pv_array, tpd_array), ["pv", "tpd"])
                
    return df_array.copy()

def calculate_AC_EV_TED (df, range_time = None):
    """
    Função que lê o dataframe e as atividades sequenciadas e calcula os demais parâmetros
    e variáveis que compõe os indicadores
    """
    if range_time == None:
        range_time = int(df.act_dur_plan_end.max()*1.1)
        
    n_act = df.shape[0]
    
    ac_array = np.zeros(range_time+1) #criação do array float com o actual cost
    ev_array = np.zeros(range_time+1) #criação do array float com o earned value
    ted_array = np.zeros(range_time+1) #criação do array float com o ted
    
    for time in range(1, range_time + 1):
        
        for act in range (n_act):
            
            if float(df.loc[df.index_aux == act, "act_dur_real_start"]) > time: 
                #quebra o loop caso o inicio da atividade real (ex: atividade 2 começa no dia 16) e o período de análise é 15 
                break
            
            elif float(df.loc[df.index_aux == act, "act_dur_real_end"]) <= time: #caso o final seja menor ou igual à data de termino da atividade - incorpora o tempo e custo total da atividade
                ac_array[time] = ac_array[time] + df.loc[df.index_aux == act, "act_cost"]
                
                ev_array[time] = ev_array[time] + df.loc[df.index_aux == act, "avr_cost"]
                
                ted_array[time] = ted_array[time] + df.loc[df.index_aux == act, "avr_time"]
            
            else: #caso seja > que o time - faz a interpolação
                ac_array[time] = ac_array[time] + (time - df.loc[df.index_aux == act, "act_dur_real_start"])/\
                                (df.loc[df.index_aux == act, "act_dur_real_end"] - df.loc[df.index_aux == act, "act_dur_real_start"])*\
                                (df.loc[df.index_aux == act, "act_cost"])
                
                ev_array[time] = ev_array[time] + (time - df.loc[df.index_aux == act, "act_dur_real_start"])/\
                                (df.loc[df.index_aux == act, "act_dur_real_end"] - df.loc[df.index_aux == act, "act_dur_real_start"])*\
                                (df.loc[df.index_aux == act, "avr_cost"])
                
                ted_array[time] = ted_array[time] + (time - df.loc[df.index_aux == act, "act_dur_real_start"])/\
                                (df.loc[df.index_aux == act, "act_dur_real_end"] - df.loc[df.index_aux == act, "act_dur_real_start"])*\
                                (df.loc[df.index_aux == act, "avr_time"]) #earned usa o average time e o actual usa o actual time
                
    df_array = concatenate_arrays((ac_array, ev_array, ted_array), ["ac", "ev", "ted"])
                                  
    return df_array.copy()
        
def calculate_CPI_SPI(df):
    """
    Função que calcula os indicadores de CPI e de SPI
    """
    df["cpi"] = df.ev/df.ac
    df["spi"] = df.ev/df.pv

    return df.copy()

def calculate_ES_TPI(df, range_time = None):
    """
    Função que calcula o earned schedule e o time performance index
    """
    
    #cria a coluna de index auxiliar
    df_index = df.reset_index().rename({"index": "index_aux"}, axis = 1)
    
    #monta o valor da iteração, caso não tenha sido fornecida
    if range_time == None:
        range_time = df_index.shape[0]

    #arrays auxiliares
    es_array = np.zeros(range_time+1) #criação do array float com o es
    tpi_array = np.zeros(range_time+1) #criação do array float com o tpi

        
    for time in range(1, 330+1): #percorre de 1 a 330 para encontrar todos os valores do earned value
        ev = float(df_index.loc[df_index.index_aux == time, "ev"])
        
        for time_aux in range (1,330+1): #percorre até encontrar o valor do planned value maior que o do earned value
            pv_plus_one = float(df_index.loc[df_index.index_aux == time_aux, "pv"])
            if pv_plus_one > ev: #pv_plus_one tem que ser sempre maior que o EV. Se o pv for =, dá 0 a conta e está no dia correto           
                # print ("Valor de time(todos de ev): ", time)
                # print ("Valor de time_aux(todos de pv pra encontrar ev): ", time_aux)
                # print("Valor de ev: ", ev)    
                # print("Valor de pv_plus_one: ", pv_plus_one)
                break
        
        try:
            pv = float(df_index.loc[df_index.index_aux == time_aux-1, "pv"])
            # print("Valor de pv: ", pv, end = "\n\n")
            #tem que diminuir o valor do time_aux porque ele identifica o do pv_plus_one, e não do pv
            es_array[time] = time_aux -1 + (ev - pv)/(pv_plus_one - pv) 
            tpi_array[time] = es_array[time]/time

        except:
            #para o es e ed, não existe pv ou tpd = 0, então vamos apenas dividir o valor do ev pelo pv 
            if time_aux == 1:
                es_array[time] = ev/pv_plus_one
                tpi_array[time] = es_array[time]/time

            else:
                es_array[time] = np.nan
                tpi_array[time] = np.nan
    
    #concatenate arrays and merge it with the dataframe - remove o primeiro valor que é nulo
    df_array = concatenate_arrays((es_array, tpi_array), ["es", "tpi"])
    # display("df_array ES TPI: ", df_array)    
    df = concatenate_dataframes(df, df_array, drop = False)
    # display("df ES TPI: ", df)

    return df.copy()


def calculate_ED_DPI(df, range_time = None):
    """
    Função que calcula o earned duration e o duration performance index
    """
    
    #cria a coluna de index auxiliar
    df_index = df.reset_index().rename({"index": "index_aux"}, axis = 1)
    
    #monta o valor da iteração, caso não tenha sido fornecida
    if range_time == None:
        range_time = df_index.shape[0]

    #arrays auxiliares
    ed_array = np.zeros(range_time+1) #criação do array float com o es
    dpi_array = np.zeros(range_time+1) #criação do array float com o tpi

        
    for time in range(1, 330+1): #percorre de 1 a 330 para encontrar todos os valores do earned value
        ted = float(df_index.loc[df_index.index_aux == time, "ted"])
        
        for time_aux in range (1,330+1): #percorre até encontrar o valor do planned value maior que o do earned value
            tpd_plus_one = float(df_index.loc[df_index.index_aux == time_aux, "tpd"])
            if tpd_plus_one > ted:             
                break
        
        try:
            tpd = float(df_index.loc[df_index.index_aux == time_aux-1, "tpd"])
            ed_array[time] = time_aux - 1 + (ted - tpd)/(tpd_plus_one - tpd)
            dpi_array[time] = ed_array[time]/time

        except:
            if time_aux == 1:
                ed_array[time] = ted/tpd_plus_one
                dpi_array[time] = ed_array[time]/time

            else:
                ed_array[time] = np.nan
                dpi_array[time] = np.nan
    
    #concatenate arrays and merge it with the dataframe
    df_array = concatenate_arrays((ed_array, dpi_array), ["ed", "dpi"])
    # display("df_array ED DPI: ", df_array)        
    df = concatenate_dataframes(df, df_array, drop = False)
    # display("df ED DPI: ", df)
    
    return df.copy()
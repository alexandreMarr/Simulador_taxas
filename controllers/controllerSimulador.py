import pandas as pd
import streamlit as st
import utils.conexaoBD as confBD
import controllers.controllerGlobal as ControllerGlobal


# Função para calcular as taxas finais
def calcular_taxas(mcc, adiquirente, spreads, dados_do_banco_de_dados, tipo_taxa, link,antecipacao):
    """
    Calcula as taxas finais para a adquirente especificada.

    Args:
        mcc (int): Código do MCC.
        adiquirente (str): Nome da adquirente (por exemplo, 'Adiq' ou 'Getnet').
        spreads (dict): Dicionário contendo os spreads para cada tipo de parcelamento.
        dados_do_banco_de_dados (DataFrame): DataFrame contendo os dados do banco de dados.
        tipo_taxa (str): Tipo de taxa, usado apenas quando a adquirente não é 'Adiq'.
        link (bool): Indica se a taxa de link de pagamento deve ser adicionada.

    Returns:
        DataFrame: Tabela formatada com as taxas finais.
    """
    config = confBD.carregar_dados_config()
    custo = config.loc[0,'custo']
    custo_valor = config.loc[0,'valor_custo']
    tipo_intercambio = config.loc[0, 'tipo_intercambio']
    taxa_link_adiq = config.loc[0,'taxa_link_pagamento_adiq']
    
    # Filtrar dados do banco de dados pelo MCC
    if adiquirente == 'Adiq':
        dados_filtrados = dados_do_banco_de_dados[dados_do_banco_de_dados['mcc'] == mcc]
        pivot_table = dados_filtrados.pivot_table(index='Parcelamento', columns='Bandeira', values=tipo_intercambio, aggfunc='mean')
    else:
        dados_filtrados = dados_do_banco_de_dados[(dados_do_banco_de_dados['mcc'] == mcc) & (dados_do_banco_de_dados['tipo_taxa'] == tipo_taxa)]
        pivot_table = dados_filtrados.pivot_table(index='Parcelamento', columns='Bandeira', values='intercambio_mediano', aggfunc='mean')
    
    # Adicionar o spread digitado pelo usuário aos valores de intercâmbio mediano
    for tipo_parcelamento in pivot_table.index:
        pivot_table.loc[tipo_parcelamento] += spreads[tipo_parcelamento]
       
    if adiquirente == 'Adiq':
        for tipo_parcelamento in pivot_table.index:
            for bandeira in pivot_table.columns:
                dados_filtrados_atual = dados_filtrados[(dados_filtrados['Bandeira'] == bandeira) & (dados_filtrados['Parcelamento'] == tipo_parcelamento)]
                if not dados_filtrados_atual.empty:
                    pivot_table.loc[tipo_parcelamento, bandeira] += dados_filtrados_atual['plusprice'].values[0]
    
    if custo:
        for tipo_parcelamento in pivot_table.index:
            pivot_table.loc[tipo_parcelamento] += custo_valor             
    
    if link:
        for tipo_parcelamento in pivot_table.index:
            pivot_table.loc[tipo_parcelamento] += taxa_link_adiq
    
    
    # Retorna a tabela pivot formatada
    return ControllerGlobal.formatacao_pivot(pivot_table)

# Função para carregar a tabela de taxas
def carregar_tabela_taxas(adiquirente, dataset, filtros): 
    """
    Carrega a tabela de taxas com base nos filtros especificados.

    Args:
        adiquirente (str): Nome da adquirente (por exemplo, 'Adiq' ou 'Getnet').
        dataset (DataFrame): DataFrame contendo os dados da tabela de taxas.
        filtros (dict): Dicionário contendo os filtros a serem aplicados.

    Returns:
        DataFrame: Tabela formatada com as taxas.
    """
    # Verifica o tipo de adquirente
    if adiquirente == 'Getnet':
        # Aplica filtros específicos para a Getnet
        if filtros['mcc_filtrado']:
            dataset = dataset[dataset['mcc'].isin(filtros['mcc_filtrado'])]                 
       
        if filtros['tipo_taxa']:
            dataset = dataset[dataset['tipo_taxa'].isin(filtros['tipo_taxa'])]
                
    else:
        # Aplica filtros genéricos para outras adquirentes
        if filtros['mcc_filtrado']:
            dataset = dataset[dataset['mcc'].isin(filtros['mcc_filtrado'])]
                        
    if filtros['bandeira_filtrada']:
        dataset = dataset[dataset['Bandeira'].isin(filtros['bandeira_filtrada'])]
        
    if filtros['parcelamento_filtrado']:
        dataset = dataset[dataset['Parcelamento'].isin(filtros['parcelamento_filtrado'])]

    # Função para formatar os elementos da tabela com números seguidos de "%"
    def formatar_percentagem(elemento):
        if isinstance(elemento, (int, float)):
            return f"{elemento:.2f}%"  # Formata os números com duas casas decimais seguidas de "%"
        else:
            return elemento

    # Aplicar a formatação à tabela
    dataset = dataset.applymap(formatar_percentagem)
    
    novo_nome_colunas = {
        'Bandeira': 'Bandeira',
        'produto': 'Produto',
        'mcc': 'MCC',
        'intercambio_mediano': 'Intercâmbio Mediano',
        'Intercambio_medio': 'Intercâmbio Medio',
        'Intercambio_maximo': 'Intercâmbio Maximo',
        'Percentil_60': 'Percentil 60',
        'Percentil_70': 'Percentil 70',
        'Percentil_75': 'Percentil 75',
        'Percentil_80': 'Percentil 80',
        'Percentil_90': 'Percentil 90',
        'plusprice': 'Plus Price',
    }
    
    dataset = dataset.rename(columns=novo_nome_colunas)
    
    return dataset

# Função para carregar a tabela MCC-CNAE
@st.cache_resource
def carregar_tabela_mcc_cnae(dataset, filtro):
    """
    Carrega a tabela MCC-CNAE com base nos filtros especificados.

    Args:
        dataset (DataFrame): DataFrame contendo os dados da tabela MCC-CNAE.
        filtro (dict): Dicionário contendo os filtros a serem aplicados.

    Returns:
        DataFrame: Tabela formatada com os dados da MCC-CNAE.
    """
    if filtro['filtro_cnae']:
        dataset = dataset[dataset['cnae'].isin(filtro['filtro_cnae'])]
       
    if filtro['filtro_mcc']:
        dataset = dataset[dataset['mcc'].isin(filtro['filtro_mcc'])]
    
    if filtro['filtro_grupo']:
        dataset = dataset[dataset['grupo_ramo_atividade'].isin(filtro['filtro_grupo'])]
        
    nome_colunas = {
        'grupo_ramo_atividade': 'Grupo/Ramo de Atividade',
        'cnae': 'CNAE',
        'denominacao_cnae': 'Denominação CNAE',
        'mcc': 'MCC',
        'descricao_mcc': 'Descrição MCC',
    }
    
    dataset = dataset.rename(columns=nome_colunas)

    return dataset

def calcular_taxas_antec(mcc, adiquirente, spreads, dados_do_banco_de_dados, tipo_taxa, link):
    """
    Calcula as taxas finais para a adquirente especificada.

    Args:
        mcc (int): Código do MCC.
        adiquirente (str): Nome da adquirente (por exemplo, 'Adiq' ou 'Getnet').
        spreads (dict): Dicionário contendo os spreads para cada tipo de parcelamento.
        dados_do_banco_de_dados (DataFrame): DataFrame contendo os dados do banco de dados.
        tipo_taxa (str): Tipo de taxa, usado apenas quando a adquirente não é 'Adiq'.

    Returns:
        DataFrame: Tabela formatada com as taxas finais.
    """
    # Carrega os dados de configuração do banco de dados
    config = confBD.carregar_dados_config()
    
    # Obtém as configurações relevantes do banco de dados
    custo = config.loc[0, 'custo']
    custo_valor = config.loc[0, 'valor_custo']
    tipo_intercambio = config.loc[0, 'tipo_intercambio']
    taxa_link_adiq = config.loc[0, 'taxa_link_pagamento_adiq']
    
    # Filtra os dados do banco de dados pelo MCC e pelo tipo de taxa
    if adiquirente == 'Adiq':
        dados_filtrados = dados_do_banco_de_dados[dados_do_banco_de_dados['mcc'] == mcc]
        pivot_table = dados_filtrados.pivot_table(index='Parcelamento', columns='Bandeira', values=tipo_intercambio, aggfunc='mean')
    else:
        dados_filtrados = dados_do_banco_de_dados[(dados_do_banco_de_dados['mcc'] == mcc) & (dados_do_banco_de_dados['tipo_taxa'] == tipo_taxa)]
        pivot_table = dados_filtrados.pivot_table(index='Parcelamento', columns='Bandeira', values='intercambio_mediano', aggfunc='mean')
    
    # Adiciona o spread digitado pelo usuário aos valores de intercâmbio mediano
    for tipo_parcelamento in pivot_table.index:
        pivot_table.loc[tipo_parcelamento] += spreads[tipo_parcelamento]
       
    # Adiciona o valor de plusprice aos valores de intercâmbio mediano, se aplicável
    if adiquirente == 'Adiq':
        for tipo_parcelamento in pivot_table.index:
            for bandeira in pivot_table.columns:
                dados_filtrados_atual = dados_filtrados[(dados_filtrados['Bandeira'] == bandeira) & (dados_filtrados['Parcelamento'] == tipo_parcelamento)]
                if not dados_filtrados_atual.empty:
                    pivot_table.loc[tipo_parcelamento, bandeira] += dados_filtrados_atual['plusprice'].values[0]
    
    # Adiciona o custo fixo, se aplicável
    if custo:
        for tipo_parcelamento in pivot_table.index:
            pivot_table.loc[tipo_parcelamento] += custo_valor             
    
    # Adiciona a taxa de link de pagamento, se aplicável
    if link:
        for tipo_parcelamento in pivot_table.index:
            pivot_table.loc[tipo_parcelamento] += taxa_link_adiq
            
    # Retorna a tabela pivot formatada
    return pivot_table



def calcular_antecipacao(taxas_cartao, taxa_antecipacao, valor_bruto, adiquirente, tipo_taxa):
    """
    Calcula a antecipação de valores de transações de cartão de crédito.

    Parâmetros:
        taxas_cartao (DataFrame): DataFrame contendo as taxas de intercâmbio por bandeira e tipo de parcelamento.
        taxa_antecipacao (float): Taxa de antecipação a ser aplicada sobre o valor bruto da transação.
        valor_bruto (float): Valor bruto da transação.
        adiquirente (str): Nome da adquirente.
        tipo_taxa (str): Tipo de taxa de antecipação.

    Retorna:
        DataFrame: DataFrame contendo os valores antecipados por bandeira e número de parcelas.
    """
    # Mapear cada intervalo de parcelamento para o número de parcelas
    intervalo_para_parcelas = {
        'CRÉDITO': [1],
        '2X a 6X': list(range(2, 7)),
        '7X a 12X': list(range(7, 13))
    }
    tam = 11
    if adiquirente == 'Getnet' and tipo_taxa == 'SEM ANTECIPAÇÃO':
        intervalo_para_parcelas = {
        'CRÉDITO': [1],
        '2X a 6X': list(range(2, 7)),
        '7X a 12X': list(range(7, 13)),
        '13X a 18X': list(range(13, 19))
        }
        tam = 17
    
    # Criar um DataFrame para armazenar os resultados
    antecipacao = pd.DataFrame(index=list(range(1, tam)), columns=taxas_cartao.columns)
    
    # Calcular o valor antecipado para cada tipo de parcelamento e bandeira
    for parcelamento in intervalo_para_parcelas:
        num_parcelas = intervalo_para_parcelas[parcelamento]
        for bandeira in antecipacao.columns:
            for i in num_parcelas:
                # Calcular o valor líquido da parcela
                valor_liquido = round(valor_bruto - (valor_bruto * ((taxas_cartao.loc[parcelamento, bandeira] + taxa_antecipacao) / 100)),2)
                taxa_final = round(taxas_cartao.loc[parcelamento, bandeira] + taxa_antecipacao,2)
                            
                # Armazenar o valor final na tabela de antecipação
                antecipacao.loc[i, bandeira] = f"R${valor_liquido}<br>{taxa_final}%"
    
    return ControllerGlobal.formatacao_pivot_antecipacao(antecipacao)


def calcular_taxas_avançado(mcc, adiquirente, spreads, dados_do_banco_de_dados, tipo_taxa, link, antecipacao):
    config = confBD.carregar_dados_config()
    custo = config.loc[0,'custo']
    custo_valor = config.loc[0,'valor_custo']
    tipo_intercambio = config.loc[0, 'tipo_intercambio']
    taxa_link_adiq = config.loc[0,'taxa_link_pagamento_adiq']
    
    if adiquirente == 'Adiq':
        dados_filtrados = dados_do_banco_de_dados[dados_do_banco_de_dados['mcc'] == mcc]
        pivot_table = dados_filtrados.pivot_table(index='Parcelamento', columns='Bandeira', values=tipo_intercambio, aggfunc='mean')
    else:
        dados_filtrados = dados_do_banco_de_dados[(dados_do_banco_de_dados['mcc'] == mcc) & (dados_do_banco_de_dados['tipo_taxa'] == tipo_taxa)]
        pivot_table = dados_filtrados.pivot_table(index='Parcelamento', columns='Bandeira', values='intercambio_mediano', aggfunc='mean')
    
    for tipo_parcelamento in pivot_table.index:
        for bandeira in pivot_table.columns:
            spread_key = f"{bandeira}_{tipo_parcelamento}_spread"
            pivot_table.loc[tipo_parcelamento, bandeira] += spreads[spread_key]
       
    if adiquirente == 'Adiq':
        for tipo_parcelamento in pivot_table.index:
            for bandeira in pivot_table.columns:
                dados_filtrados_atual = dados_filtrados[(dados_filtrados['Bandeira'] == bandeira) & (dados_filtrados['Parcelamento'] == tipo_parcelamento)]
                if not dados_filtrados_atual.empty:
                    pivot_table.loc[tipo_parcelamento, bandeira] += dados_filtrados_atual['plusprice'].values[0]
    
    if custo:
        for tipo_parcelamento in pivot_table.index:
            pivot_table.loc[tipo_parcelamento] += custo_valor             
    
    if link:
        for tipo_parcelamento in pivot_table.index:
            pivot_table.loc[tipo_parcelamento] += taxa_link_adiq
    
    
    return ControllerGlobal.formatacao_pivot(pivot_table)


def calcular_taxas_executivos(mcc, adiquirente, spreads, dados_do_banco_de_dados, tipo_taxa,antecipacao):
     """
     Calcula as taxas finais para a adquirente especificada.
     Args:
         mcc (int): Código do MCC.
         adiquirente (str): Nome da adquirente (por exemplo, 'Adiq' ou 'Getnet').
         spreads (dict): Dicionário contendo os spreads para cada tipo de parcelamento.
         dados_do_banco_de_dados (DataFrame): DataFrame contendo os dados do banco de dados.
         tipo_taxa (str): Tipo de taxa, usado apenas quando a adquirente não é 'Adiq'.
         link (bool): Indica se a taxa de link de pagamento deve ser adicionada.
     Returns:
         DataFrame: Tabela formatada com as taxas finais.
     """
     config = confBD.carregar_dados_config()
     custo = config.loc[0,'custo']
     custo_valor = config.loc[0,'valor_custo']
     tipo_intercambio = config.loc[0, 'tipo_intercambio']
     taxa_link_adiq = config.loc[0,'taxa_link_pagamento_adiq']
     
     # Carregar os spreads comerciais do banco de dados
     spreads_comercial = confBD.carregar_dados_spread_comercial()
     
     # Filtrar dados do banco de dados pelo MCC
     if adiquirente == 'Adiq':
         dados_filtrados = dados_do_banco_de_dados[dados_do_banco_de_dados['mcc'] == mcc]
         pivot_table = dados_filtrados.pivot_table(index='Parcelamento', columns='Bandeira', values=tipo_intercambio, aggfunc='mean')
     else:
         dados_filtrados = dados_do_banco_de_dados[(dados_do_banco_de_dados['mcc'] == mcc) & (dados_do_banco_de_dados['tipo_taxa'] == tipo_taxa)]
         pivot_table = dados_filtrados.pivot_table(index='Parcelamento', columns='Bandeira', values='intercambio_mediano', aggfunc='mean')
   
     for tipo_parcelamento in pivot_table.index:
        for bandeira in pivot_table.columns:
            spread_key = f"{bandeira}_{tipo_parcelamento}_spreads"
            pivot_table.loc[tipo_parcelamento, bandeira] += spreads[spread_key]
                 
     # Adicionar os spreads comerciais do banco de dados
     for tipo_parcelamento in pivot_table.index:
         for bandeira in pivot_table.columns:
             spread_comercial = spreads_comercial.loc[
                 (spreads_comercial['bandeira'] == bandeira) & (spreads_comercial['parcelamento'] == tipo_parcelamento), 'spread']
             if not spread_comercial.empty:
                 pivot_table.loc[tipo_parcelamento, bandeira] += spread_comercial.values[0]
           
     if adiquirente == 'Adiq':
         for tipo_parcelamento in pivot_table.index:
             for bandeira in pivot_table.columns:
                 dados_filtrados_atual = dados_filtrados[(dados_filtrados['Bandeira'] == bandeira) & (dados_filtrados['Parcelamento'] == tipo_parcelamento)]
                 if not dados_filtrados_atual.empty:
                     pivot_table.loc[tipo_parcelamento, bandeira] += dados_filtrados_atual['plusprice'].values[0]
                   
     if custo:
         for tipo_parcelamento in pivot_table.index:
             pivot_table.loc[tipo_parcelamento] += custo_valor 
             
           
     # Retorna a tabela pivot formatada
     return ControllerGlobal.formatacao_pivot(pivot_table)
import pandas as pd
import psycopg2 
import streamlit as st
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text

# Configurações da página do Streamlit
def config(layout, title):
    """
    Configurações da página do Streamlit.

    Args:
        layout (str): Layout da página ('wide' ou 'centered').
        title (str): Título da página.

    Returns:
        None
    
    """
    if layout:
        layout = layout
    else:
        layout = 'centered'
    st.set_page_config(
        page_title=title,  # Título da página
        page_icon="https://i.ibb.co/SwkjNHJ/Icone-UP.png",  # Ícone da página
        layout=layout,  # Layout centralizado
    )
    # Carrega o arquivo de estilo CSS
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Função para conectar ao banco de dados PostgreSQL
def conectar_banco_de_dados():
    """
    Conecta-se ao banco de dados usando as variáveis de ambiente definidas no arquivo .env.

    Returns:
        conn (psycopg2.extensions.connection): Conexão com o banco de dados.
    
    Raises:
        psycopg2.OperationalError: Se a conexão com o banco de dados falhar.
    """
    load_dotenv()
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),         # Endereço do host do banco de dados
        dbname=os.getenv("DB_DATABASE"),   # Nome do banco de dados
        user=os.getenv("DB_USERNAME"),     # Nome de usuário para autenticação
        password=os.getenv("DB_PASSWORD")  # Senha para autenticação
    )
    return conn

# Função para carregar os dados dos códigos MCC do banco de dados
@st.cache_resource
def carregar_dados_mcc():
    """
    Carrega os dados dos códigos MCC (Merchant Category Code) de um banco de dados.

    Returns:
        DataFrame: DataFrame contendo os dados dos códigos MCC.

    """
    conn = conectar_banco_de_dados()  # Função para conectar ao banco de dados
    query = "SELECT * FROM base_mcc_geral"  # Consulta SQL para selecionar todos os dados da tabela base_mcc_geral
    return pd.read_sql(query, conn)  # Retorna os dados como DataFrame

# Função para carregar os dados da adquirente Adiq do banco de dados
@st.cache_resource
def carregar_dados_adiq():
    """
    Carrega os dados da adquirente Adiq de um banco de dados.

    Returns:
        DataFrame: DataFrame contendo os dados da adquirente Adiq.

    """
    conn = conectar_banco_de_dados()  # Função para conectar ao banco de dados
    query = "SELECT * FROM vw_mdr_adiq_up"  # Consulta SQL para selecionar todos os dados da view vw_mdr_adiq_up
    return pd.read_sql(query, conn)  # Retorna os dados como DataFrame

# Função para carregar os dados da adquirente Getnet do banco de dados
@st.cache_resource
def carregar_dados_getnet():
    """
    Carrega os dados da adquirente Getnet de um banco de dados.

    Returns:
        DataFrame: DataFrame contendo os dados da adquirente Getnet.

    """
    conn = conectar_banco_de_dados()  # Função para conectar ao banco de dados
    query = "SELECT * FROM vw_mdr_getnet_up"  # Consulta SQL para selecionar todos os dados da view vw_mdr_getnet_up
    return pd.read_sql(query, conn)  # Retorna os dados como DataFrame

# Função para carregar os dados da adquirente Adiq do banco de dados
@st.cache_resource
def carregar_dados_adiq_overprice():
    """
    Carrega os dados da adquirente Adiq de um banco de dados.

    Returns:
        DataFrame: DataFrame contendo os dados da adquirente Adiq
    """
    conn = conectar_banco_de_dados()  # Função para conectar ao banco de dados
    query = "SELECT * FROM vw_mdr_adiq_overprice_up"  # Consulta SQL para selecionar todos os dados da view vw_mdr_adiq_up
    return pd.read_sql(query, conn)  # Retorna os dados como DataFrame
# Função para carregar os dados da relação MCC-CNAE do banco de dados
@st.cache_resource
def carregar_dados_mcc_cnae():
    """
    Carrega os dados da relação MCC-CNAE de um banco de dados.

    Returns:
        DataFrame: DataFrame contendo os dados da relação MCC-CNAE.
    """
    conn = conectar_banco_de_dados()  # Conecta ao banco de dados
    query = "SELECT * FROM mcc_cnae"  # Consulta SQL para selecionar todos os dados da tabela mcc_cnae
    return pd.read_sql(query, conn)  # Retorna os dados como DataFrame

# Função para carregar os dados de configuração do banco de dados
@st.cache_resource
def carregar_dados_config():
    """
    Carrega os dados de configuração de um banco de dados.

    Returns:
        DataFrame: DataFrame contendo os dados de configuração.
    """
    conn = conectar_banco_de_dados()  # Conecta ao banco de dados
    query = "SELECT * FROM config"  # Consulta SQL para selecionar todos os dados da tabela config
    return pd.read_sql(query, conn)  # Retorna os dados como DataFrame

# Função para carregar os URLs das imagens das bandeiras de cartão de crédito
@st.cache_resource
def carregar_urls_das_bandeiras():
    """
    Carrega os URLs das imagens das bandeiras de cartão de crédito.

    Returns:
        DataFrame: DataFrame contendo os URLs das imagens das bandeiras.
    """
    # Dicionário contendo os URLs das imagens das bandeiras
    data = {
        'BANDEIRA': ['MASTERCARD', 'VISA','ELO', 'AMEX', 'HIPERCARD'],
        'URL_IMAGEM': [
            'https://i.ibb.co/nRVzTQS/mastercard.png',
            'https://i.ibb.co/HtmwvpD/logo-visa.png',
            'https://i.ibb.co/GMXwsVF/elo.png',
            'https://i.ibb.co/QPYY0K6/amex.png',
            'https://i.ibb.co/N9cxwTD/hiper.png'
        ]
    }
    return pd.DataFrame(data)  # Retorna os dados como DataFrame

# Função para formatar uma tabela pivot
@st.cache_resource
def formatacao_pivot(pivot_table):
    """
    Realiza a formatação de uma tabela pivot.

    Args:
        pivot_table (DataFrame): Tabela pivot a ser formatada.

    Returns:
        DataFrame: Tabela pivot formatada.
    """
    # Certifique-se de que as colunas da tabela pivot são strings
    pivot_table.columns = pivot_table.columns.to_series().astype(str)
    
    # Verifique se as bandeiras na lista ordem_desejada estão presentes nas colunas da tabela pivot
    ordem_desejada = ['MASTERCARD', 'VISA', 'ELO', 'HIPERCARD', 'AMEX']
    ordem_desejada = [bandeira for bandeira in ordem_desejada if bandeira in pivot_table.columns]
    
    # Reordenar as colunas de acordo com a ordem desejada
    pivot_table = pivot_table.reindex(columns=ordem_desejada)
    
    # Ordem das Linhas de Parcelamento
    ordem_desejada_parcelamento = ['DÉBITO', 'CRÉDITO', '2X a 6X', '7X a 12X','13X a 18X']
    ordem_desejada_parcelamento = [parcelamento for parcelamento in ordem_desejada_parcelamento if parcelamento in pivot_table.index]
    
    # Reordenar as linhas de acordo com a ordem desejada
    pivot_table = pivot_table.reindex(ordem_desejada_parcelamento)

    # Deixa oculto a linha 'Parcelamento' da tabela Pivot
    pivot_table.index.name = None
    
    # Função para formatar os elementos da tabela com números seguidos de "%"
    def formatar_percentagem(elemento):
        if isinstance(elemento, (int, float)):
            return f"{elemento:.2f}%"  # Formata os números com duas casas decimais seguidas de "%"
        else:
            return elemento

    # Aplicar a formatação à tabela
    pivot_table_formatada = pivot_table.applymap(formatar_percentagem)

    # Carregar os URLs das imagens das bandeiras
    bandeiras_df = carregar_urls_das_bandeiras()
    
    # Substituir os nomes das bandeiras pelos URLs das imagens na pivot table
    for bandeira in pivot_table_formatada.columns:
        if bandeira in bandeiras_df['BANDEIRA'].values:
            # Obtém o URL da imagem da bandeira atual
            url_imagem = bandeiras_df[bandeiras_df['BANDEIRA'] == bandeira]['URL_IMAGEM'].iloc[0]
            # Substitui o nome da bandeira pelo HTML da imagem na tabela pivot
            pivot_table_formatada.rename(columns={bandeira: f'<img src="{url_imagem}" alt="{bandeira}" style="width:70px;height:40px; text-align: center;">'}, inplace=True)
    
    # Aplicar display: flex ao estilo do DataFrame para melhorar a apresentação
    styles = [
        dict(selector="", props=[("display", "ruby-text"), ("flex-wrap", "wrap"), ("justify-content", "center"), ("border-collapse", "unset")]),
    ]
    pivot_table_formatada = pivot_table_formatada.style.set_table_styles(styles)

    return pivot_table_formatada  # Retorna a tabela pivot formatada

# Função para calcular as taxas finais
def calcular_taxas(mcc, adiquirente, spreads, dados_do_banco_de_dados, tipo_taxa, link):
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
    config = carregar_dados_config()
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
    return formatacao_pivot(pivot_table)

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
        'intercambio_mediano': 'Taxa',
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
    config = carregar_dados_config()
    
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

def formatacao_pivot_antecipacao(pivot_table):
    """
    Realiza a formatação da tabela pivot retornados da base.
   
    Args:
       pivot_table (array:float): Dados finas para retornar na tabela.

    Returns:
        pivot_table_formatada: Tabela formatada com as taxas finais.
    """
    pivot_table.columns = pivot_table.columns.to_series().astype(str)
    ordem_desejada = ['MASTERCARD', 'VISA', 'ELO', 'HIPERCARD', 'AMEX']
    ordem_desejada = [bandeira for bandeira in ordem_desejada if bandeira in pivot_table.columns]
    pivot_table = pivot_table.reindex(columns=ordem_desejada)
    pivot_table.rename(index={1: 'CRÉDITO', 2: '2X', 3: '3X', 4: '4X', 5: '5X', 6: '6X', 7: '7X', 8: '8X', 9: '9X', 10: '10X', 11: '11X', 12: '12X', 13: '13X', 14: '14X', 15: '15X', 16: '16X', 17: '17X', 18: '18X'}, inplace=True)

    def formatar_percentagem(elemento):
        if isinstance(elemento, (int, float)):
            return f"{elemento:.2f}%"  
        else:
            return elemento

    pivot_table_formatada = pivot_table.applymap(formatar_percentagem)

    bandeiras_df = carregar_urls_das_bandeiras()

    for bandeira in pivot_table_formatada.columns:
        if bandeira in bandeiras_df['BANDEIRA'].values:
            url_imagem = bandeiras_df[bandeiras_df['BANDEIRA'] == bandeira]['URL_IMAGEM'].iloc[0]
            pivot_table_formatada.rename(columns={bandeira: f'<img src="{url_imagem}" alt="{bandeira}" style="width:70px;height:40px; text-align: center;">'}, inplace=True)

    return pivot_table_formatada  

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
    
    return formatacao_pivot_antecipacao(antecipacao)

def conectar_banco_de_dados():
    """
    Conecta ao banco de dados PostgreSQL.

    Retorna:
        Engine: Conexão com o banco de dados.
    """
    load_dotenv()
    connection_string = f'postgresql://{os.getenv("DB_USERNAME")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:5432/{os.getenv("DB_DATABASE")}'
    return create_engine(connection_string)

def table_exists(engine, table_name):
    """
    Verifica se uma tabela existe no banco de dados.

    Parâmetros:
        engine (Engine): Conexão com o banco de dados.
        table_name (str): Nome da tabela a ser verificada.

    Retorna:
        bool: True se a tabela existir, False caso contrário.
    """
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def atualizar_tabela_principal(arquivo_excel):
    """
    Atualiza a tabela principal no banco de dados com os dados do arquivo Excel fornecido.

    Parâmetros:
        arquivo_excel (str): Caminho do arquivo Excel contendo os dados a serem atualizados.

    Retorna:
        dict: Relatório contendo informações sobre o processo de atualização.
    """
    # Backup da tabela principal
    engine = conectar_banco_de_dados()
    if table_exists(engine, 'mdr_adiq_up'):
        df_backup = pd.read_sql_query('SELECT * FROM mdr_adiq_up', engine)
        df_backup.to_sql('mdr_adiq_up_bkp', engine, if_exists='replace', index=False)

    # Leitura e preparação dos dados da planilha
    df = pd.read_excel(arquivo_excel, usecols=['Bandeira', 'Produto', 'Tp Parcelado', 'Mcc', 'Intercâmbio Máximo','Intercâmbio Médio','Intercâmbio Mediana','Percentil 60','Percentil 70','Percentil 75','Percentil 80','Percentil 90'])
    df.columns = ['bandeira', 'produto', 'tipo_parcelamento', 'mcc', 'intercambio_maximo','intercambio_medio','intercambio_mediano','Percentil_60','Percentil_70','Percentil_75','Percentil_80','Percentil_90']

    #colunas para transformar em duas casas decimais
    colunas = ['intercambio_maximo', 'intercambio_medio', 'intercambio_mediano', 
           'Percentil_60', 'Percentil_70', 'Percentil_75', 'Percentil_80', 'Percentil_90']

    # Aplicando a transformação para cada coluna
    df[colunas] = df[colunas].apply(lambda x: round(x * 100, 2))  
    
    df['bandeira'] = df['bandeira'].str.upper()
    df['produto'] = df['produto'].str.upper()
    df['tipo_parcelamento'] = df['tipo_parcelamento'].replace({'Débito': 'DÉBITO', 'À VISTA': 'CRÉDITO', '2-6': '2X a 6X', '7-12': '7X a 12X'})
    # Remover espaços extras no início e no final das colunas 'produto', 'bandeira' e 'tipo_parcelamento'
    df['bandeira'] = df['bandeira'].str.strip()
    df['produto'] = df['produto'].str.strip()
    df['tipo_parcelamento'] = df['tipo_parcelamento'].str.strip()

    # Salvando os dados com a coluna mcc como inteiro no banco de dados
    df.to_sql('mdr_adiq_up_temp', engine, if_exists='replace', index=False)

    # Alterando a coluna mcc para VARCHAR após a inserção
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE mdr_adiq_up_temp ALTER COLUMN mcc TYPE VARCHAR(10)"))

    # Relatório de análise
    total_registros_main = pd.read_sql_query('SELECT COUNT(*) FROM mdr_adiq_up', engine)['count'][0]
    total_registros_temp = pd.read_sql_query('SELECT COUNT(*) FROM mdr_adiq_up_temp', engine)['count'][0]
    
    # Montar a query de atualização
    query = f"""
        UPDATE mdr_adiq_up AS main
        SET 
            intercambio_maximo = temp.intercambio_maximo,
            intercambio_medio = temp.intercambio_medio,
            intercambio_mediano = temp.intercambio_mediano,
            "Percentil_60" = temp."Percentil_60",
            "Percentil_70" = temp."Percentil_70",
            "Percentil_75" = temp."Percentil_75",
            "Percentil_80" = temp."Percentil_80",
            "Percentil_90" = temp."Percentil_90"
        FROM mdr_adiq_up_temp AS temp
        WHERE main.bandeira = temp.bandeira
        AND main.tipo_parcelamento = temp.tipo_parcelamento
        AND main.produto = temp.produto
        AND main.mcc = temp.mcc
        RETURNING main.*;
    """
    # Executar a query e contar registros atualizados e adicionados
    with engine.begin() as conn:
        result = conn.execute(text(query))
        updated_rows = len(result.fetchall())
    
        query2 = """
            INSERT INTO mdr_adiq_up (bandeira, tipo_parcelamento, produto, mcc, intercambio_maximo, intercambio_medio, intercambio_mediano, 
           "Percentil_60", "Percentil_70", "Percentil_75", "Percentil_80", "Percentil_90")
            SELECT temp.bandeira, temp.tipo_parcelamento, temp.produto, temp.mcc,temp.intercambio_maximo, temp.intercambio_medio, temp.intercambio_mediano, 
           temp."Percentil_60", temp."Percentil_70", temp."Percentil_75", temp."Percentil_80", temp."Percentil_90"
            FROM mdr_adiq_up_temp AS temp
            WHERE NOT EXISTS (
                SELECT 1
                FROM mdr_adiq_up AS main
                WHERE main.bandeira = temp.bandeira
                AND main.tipo_parcelamento = temp.tipo_parcelamento
                AND main.produto = temp.produto
                AND main.mcc = temp.mcc
            );
        """

    with engine.begin() as conn:
        result2 = conn.execute(text(query2))
        inserted_rows = result2.rowcount
        
        query3 = """
            SELECT *
            FROM mdr_adiq_up_temp
            GROUP BY bandeira, produto, tipo_parcelamento, mcc, intercambio_mediano,  intercambio_maximo, intercambio_medio, intercambio_mediano, 
           "Percentil_60", "Percentil_70", "Percentil_75", "Percentil_80", "Percentil_90"
            HAVING COUNT(*) > 1;
        """

    # Executar a query e contar registros atualizados e adicionados
    with engine.begin() as conn:
        result3 = conn.execute(text(query3))
        reg_duplicados_base = len(result3.fetchall())

    # Relatório de análise
    total_registros_main_pos = pd.read_sql_query('SELECT COUNT(*) FROM mdr_adiq_up', engine)['count'][0]

    registros_adicionados = inserted_rows
    registros_atualizados = updated_rows
    registros_duplicados = reg_duplicados_base
    
    # Excluir tabela temporária
    with engine.begin() as conn:
         conn.execute(text('DROP TABLE IF EXISTS mdr_adiq_up_temp;'))

    relatorio = {
        'Total de registros na base ADIQ Anterior': total_registros_main,
        'Total de registros no arquivo Excel': total_registros_temp,
        'Total de Registros adicionados': registros_adicionados,
        'Total de Registros atualizados': registros_atualizados,
        'Registros duplicados no arquivo Excel': registros_duplicados,
        'Total de Registro atual na base ADIQ': total_registros_main_pos
    }

    return relatorio

def ler_arquivo(arquivo):
    """
    Lê um arquivo Excel contendo dados sobre taxas de intercâmbio de transações de cartão de crédito.

    Parâmetros:
        arquivo (str): Caminho do arquivo Excel a ser lido.

    Retorna:
        list: Lista de dicionários contendo os dados lidos do arquivo Excel.
    """
    # Ler o arquivo Excel
    df = pd.read_excel(arquivo, header=None)

    dados = []
    tipos_parcelamento = df.iloc[0].tolist()
    bandeiras = df.iloc[1].tolist()
    
    # Dicionário para mapear as bandeiras aos índices das colunas
    indice_bandeiras = {
        'MASTERCARD': [1, 4, 9, 14, 19],
        'VISA': [2, 5, 10, 15, 20],
        'ELO': [3, 6, 11, 16, 21],
        'AMEX': [7, 12, 17, 22],
        'HIPERCARD': [8, 13, 18, 23]
    }
    
    # Iterar sobre as linhas do DataFrame, começando da terceira linha
    for index, row in df.iloc[2:].iterrows():
        mcc = row[0]
        for bandeira, indices in indice_bandeiras.items():
            for i in indices:
                taxa = row[i]
                
                # Determinar o tipo de parcelamento
                tipo_parcelamento = ''
                if i >= 1 and i <= 3:
                    tipo_parcelamento = 'DÉBITO'
                elif i >= 4 and i <= 8:
                    tipo_parcelamento = 'CRÉDITO'
                elif i >= 9 and i <= 13:
                    tipo_parcelamento = '2X a 6X'
                elif i >= 14 and i <= 18:
                    tipo_parcelamento = '7X a 12X'
                elif i >= 19:
                    tipo_parcelamento = '13X a 18X'
                
                # Determinar o produto
                produto = 'DÉBITO' if tipo_parcelamento == 'DÉBITO' else 'CRÉDITO'
                
                dados.append({
                    'bandeira': bandeira,
                    'produto': produto,
                    'tipo_parcelamento': tipo_parcelamento,
                    'mcc': mcc,
                    'intercambio_mediano': round(taxa * 100, 2)  # Multiplicar por 100 para converter a porcentagem
                })
    return dados

def salvar_no_banco_de_dados(dados, tabela):
    """
    Salva os dados fornecidos no banco de dados.

    Parâmetros:
        dados (list): Lista de dicionários contendo os dados a serem salvos.
        tabela (str): Nome da tabela no banco de dados onde os dados serão salvos.

    Retorna:
        int: Total de registros atualizados na tabela.
    """
    # Conectar ao banco de dados PostgreSQL
    engine = conectar_banco_de_dados()

    # Criar uma expressão SQL para truncar a tabela
    truncate_statement = text(f'TRUNCATE TABLE {tabela}')

    with engine.begin() as conn:
        conn.execute(truncate_statement)

    # Converter a lista de dicionários em um DataFrame pandas
    df = pd.DataFrame(dados)

    # Salvar os dados no banco de dados PostgreSQL
    df.to_sql(name=tabela, con=engine, index=False, if_exists='append')

    total_registros_atualizados = pd.read_sql_query(f'SELECT COUNT(*) FROM {tabela}', engine)['count'][0]

    return total_registros_atualizados

def atualizar_dados_config(config):
    """
    Atualiza os dados de configuração no banco de dados.

    Parâmetros:
        config (DataFrame): DataFrame contendo os dados de configuração a serem atualizados.

    Retorna:
        None
    """
    # Conectar ao banco de dados PostgreSQL
    engine = conectar_banco_de_dados()

    # Nome da tabela no banco de dados
    tabela = 'config'

    # Atualizar os dados no banco de dados PostgreSQL
    with engine.begin() as conn:
        # Atualizar os valores na tabela 'config'
        config.to_sql(name=tabela, con=engine, index=False, if_exists='replace')


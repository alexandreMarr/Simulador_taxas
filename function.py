import pandas as pd
import psycopg2 
import streamlit as st
import os
from dotenv import load_dotenv


# Configurações da página do Streamlit
def config(layout,title):
    if layout :
        layout = layout
    else:
        layout = 'centered'
    st.set_page_config(
        page_title=title,  # Título da página
        page_icon="https://i.ibb.co/SwkjNHJ/Icone-UP.png",  # Ícone da página
        layout=layout  # Layout centralizado
    
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
        DataFrame: DataFrame contendo os dados da adquirente Adiq.

    """
    conn = conectar_banco_de_dados()  # Função para conectar ao banco de dados
    query = "SELECT * FROM vw_mdr_adiq_overprice_up"  # Consulta SQL para selecionar todos os dados da view vw_mdr_adiq_up
    return pd.read_sql(query, conn)  # Retorna os dados como DataFrame

# Função para carregar os dados da relação MCC-CNAE do banco de dados
@st.cache_resource
def carregar_dados_mcc_cnae():
    """
    Carrega os dados da adquirente Adiq de um banco de dados.

    Returns:
        DataFrame: DataFrame contendo os dados da adquirente Adiq.

    """
    conn = conectar_banco_de_dados()  # Função para conectar ao banco de dados
    query = "SELECT * FROM mcc_cnae"  # Consulta SQL para selecionar todos os dados da view vw_mdr_adiq_up
    return pd.read_sql(query, conn)  # Retorna os dados como DataFrame

# Função para carregar os URLs das imagens das bandeiras de cartão de crédito
@st.cache_resource
def carregar_urls_das_bandeiras():
    """
   Dicionario de imagens em diretorio online publico.
   Esses links estão em um diretorio de imagens pessoal só que em modo publico. ou seja somente quem tem o link consegue acesso.
    Args:
      
    Returns:
        data: dados das imagens

    """

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
    return pd.DataFrame(data)

# Função para formatar uma tabela pivot  
@st.cache_resource
def formatacao_pivot(pivot_table):
    """
    Realiza a formatação da tabela pivot retornados da base.
   
    Args:
       pivot_table (array:float): Dados finas para retornar na tabela.

    Returns:
        pivot_table_formatada: Tabela formatada com as taxas finais.
    """
    # Certifique-se de que as colunas da tabela pivot são strings
    pivot_table.columns = pivot_table.columns.to_series().astype(str)
    # Verifique se as bandeiras na lista ordem_desejada estão presentes nas colunas da tabela pivot
    ordem_desejada = ['MASTERCARD', 'VISA', 'ELO', 'HIPERCARD', 'AMEX']
    ordem_desejada = [bandeira for bandeira in ordem_desejada if bandeira in pivot_table.columns]
    # Reordenar as colunas de acordo com a ordem desejada
    pivot_table = pivot_table.reindex(columns=ordem_desejada)
    
    # Ordem das Linhas de Parcelamento
    ordem_desejada_parcelamento = ['DÉBITO', 'CRÉDITO', '2X a 6X', '7X a 12X']
    ordem_desejada_parcelamento = [parcelamento for parcelamento in ordem_desejada_parcelamento if parcelamento in pivot_table.index]
    # Reordenar as linhas de acordo com a ordem desejada
    pivot_table = pivot_table.reindex(ordem_desejada_parcelamento)

    # Deixa oculto a linha 'Parcelamento' da tabela Pivot
    pivot_table.index.name = None
    
    pivot_table.loc['DÉBITO','AMEX'] = 0.00
    pivot_table.loc['DÉBITO','HIPERCARD'] = 0.00
    
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
def calcular_taxas(mcc, adiquirente, spreads, dados_do_banco_de_dados, tipo_taxa):
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
    # Filtrar dados do banco de dados pelo MCC
    if adiquirente == 'Adiq':
        dados_filtrados = dados_do_banco_de_dados[dados_do_banco_de_dados['mcc'] == mcc]
    else:
        dados_filtrados = dados_do_banco_de_dados[(dados_do_banco_de_dados['mcc'] == mcc) & (dados_do_banco_de_dados['tipo_taxa'] == tipo_taxa)]
    
    # Criar uma pivot table para ter as bandeiras como colunas e tipos de parcelamento como índices
    pivot_table = dados_filtrados.pivot_table(index='Parcelamento', columns='Bandeira', values='intercambio_mediano', aggfunc='mean')
    
    # Adicionar o spread digitado pelo usuário aos valores de intercâmbio mediano
    for tipo_parcelamento in pivot_table.index:
        pivot_table.loc[tipo_parcelamento] += spreads[tipo_parcelamento]
    
    if adiquirente == 'Adiq':
        for tipo_parcelamento in pivot_table.index:
            # Iterar sobre as colunas (bandeiras) da pivot_table
            for bandeira in pivot_table.columns:
                # Filtrar os dados para a bandeira e tipo de parcelamento atual
                dados_filtrados_atual = dados_filtrados[(dados_filtrados['Bandeira'] == bandeira) & (dados_filtrados['Parcelamento'] == tipo_parcelamento)]
                
                # Verificar se há dados filtrados para a bandeira e tipo de parcelamento atual
                if not dados_filtrados_atual.empty:
                    # Adicionar o valor correspondente de plusprice à célula da pivot_table
                    pivot_table.loc[tipo_parcelamento, bandeira] += dados_filtrados_atual['plusprice'].values[0]
    
    
            
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
    if adiquirente == 'Getnet':
        if filtros['mcc_filtrado']:
            dataset = dataset[dataset['mcc'].isin(filtros['mcc_filtrado'])]                 
       
        if filtros['tipo_taxa']:
            dataset = dataset[dataset['tipo_taxa'].isin(filtros['tipo_taxa'])]
                
    else:
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

def calcular_taxas_antec(mcc, adiquirente, spreads, dados_do_banco_de_dados, tipo_taxa):
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
    # Filtrar dados do banco de dados pelo MCC
    if adiquirente == 'Adiq':
        dados_filtrados = dados_do_banco_de_dados[dados_do_banco_de_dados['mcc'] == mcc]
    else:
        dados_filtrados = dados_do_banco_de_dados[(dados_do_banco_de_dados['mcc'] == mcc) & (dados_do_banco_de_dados['tipo_taxa'] == tipo_taxa)]
    
    # Criar uma pivot table para ter as bandeiras como colunas e tipos de parcelamento como índices
    pivot_table = dados_filtrados.pivot_table(index='Parcelamento', columns='Bandeira', values='intercambio_mediano', aggfunc='mean')
    
    # Adicionar o spread digitado pelo usuário aos valores de intercâmbio mediano
    for tipo_parcelamento in pivot_table.index:
        pivot_table.loc[tipo_parcelamento] += spreads[tipo_parcelamento]
    
    if adiquirente == 'Adiq':
        for tipo_parcelamento in pivot_table.index:
            # Iterar sobre as colunas (bandeiras) da pivot_table
            for bandeira in pivot_table.columns:
                # Filtrar os dados para a bandeira e tipo de parcelamento atual
                dados_filtrados_atual = dados_filtrados[(dados_filtrados['Bandeira'] == bandeira) & (dados_filtrados['Parcelamento'] == tipo_parcelamento)]
                
                # Verificar se há dados filtrados para a bandeira e tipo de parcelamento atual
                if not dados_filtrados_atual.empty:
                    # Adicionar o valor correspondente de plusprice à célula da pivot_table
                    pivot_table.loc[tipo_parcelamento, bandeira] += dados_filtrados_atual['plusprice'].values[0]
    
    
            
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
    # Certifique-se de que as colunas da tabela pivot são strings
    pivot_table.columns = pivot_table.columns.to_series().astype(str)
    # Verifique se as bandeiras na lista ordem_desejada estão presentes nas colunas da tabela pivot
    ordem_desejada = ['MASTERCARD', 'VISA', 'ELO', 'HIPERCARD', 'AMEX']
    ordem_desejada = [bandeira for bandeira in ordem_desejada if bandeira in pivot_table.columns]
    # Reordenar as colunas de acordo com a ordem desejada
    pivot_table = pivot_table.reindex(columns=ordem_desejada)
    
    pivot_table.rename(index={0:'DÉBITO', 1:'CRÉDITO', 2:'2X',3:'3X', 4: '4X', 5: '5X', 6: '6X', 7: '7X', 8: '8X', 9: '9X', 10: '10X', 11: '11X', 12: '12X'}, inplace=True)


    
    pivot_table.loc[0,'AMEX'] = 0.00
    pivot_table.loc[0,'HIPERCARD'] = 0.00
    
    # Função para formatar os elementos da tabela com números seguidos de "%"
    def formatar_percentagem(elemento):
        if isinstance(elemento, (int, float)):
            return f"R${elemento:.2f}"  # Formata os números com duas casas decimais seguidas de "%"
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
    # styles = [
    #     dict(selector="", props=[("display", "ruby-text"), ("flex-wrap", "wrap"), ("justify-content", "center"), ("border-collapse", "unset")]),
    # ]
    # pivot_table_formatada = pivot_table_formatada.style.set_table_styles(styles)

    return pivot_table_formatada  # Retorna a tabela pivot formatada

def calcular_antecipacao(taxas_cartao, taxa_antecipacao, valor_bruto):
    # Mapear cada intervalo de parcelamento para o número de parcelas
    intervalo_para_parcelas = {
        'DÉBITO': [0],
        'CRÉDITO': [1],
        '2X a 6X': list(range(2, 7)),
        '7X a 12X': list(range(7, 13))
    }
    
    # Criar um DataFrame para armazenar os resultados
    antecipacao = pd.DataFrame(index=list(range(0, 12)), columns=taxas_cartao.columns)
    
    # Calcular o valor antecipado para cada tipo de parcelamento e bandeira
    for parcelamento in intervalo_para_parcelas:
        num_parcelas = intervalo_para_parcelas[parcelamento]
        for bandeira in antecipacao.columns:
            for i in num_parcelas:
                # Calcular o valor líquido da parcela
                valor_liquido = valor_bruto - (valor_bruto * (taxas_cartao.loc[parcelamento, bandeira] / 100))
                if i == 0:
                    valor_liquido = valor_liquido
                else:
                    valor_liquido = valor_liquido / i
                
               
                # Calcular o valor da antecipação 
                                             
                if i == 1 or i == 0:
                    taxa_antec = (taxa_antecipacao/30) * 29
                else:
                    taxa_antec = (taxa_antecipacao/30) * ((30 * i) - 1)
                  
                
                valor_antecipacao = round((valor_liquido - (valor_liquido *  (taxa_antec/100))), 2)
                valor_antecipacao_total = round(((valor_liquido - (valor_liquido *  (taxa_antec/100))) * i),2)
                
                # geral = f'Parcela: R${valor_antecipacao} \nTotal: R${valor_antecipacao_total}'
                
                # Armazenar o valor final na tabela de antecipação
                antecipacao.loc[i, bandeira] = valor_antecipacao
                antecipacao.loc[0, 'AMEX'] = '0.00'
                antecipacao.loc[0, 'HIPERCARD'] = '0.00'
    
    return formatacao_pivot_antecipacao(antecipacao)

    
def calcular_antecipacao_total(taxas_cartao, taxa_antecipacao, valor_bruto):
    # Mapear cada intervalo de parcelamento para o número de parcelas
    intervalo_para_parcelas = {
        'DÉBITO': [0],
        'CRÉDITO': [1],
        '2X a 6X': list(range(2, 7)),
        '7X a 12X': list(range(7, 13))
    }
    
    # Criar um DataFrame para armazenar os resultados
    antecipacao = pd.DataFrame(index=list(range(0, 12)), columns=taxas_cartao.columns)
    
    # Calcular o valor antecipado para cada tipo de parcelamento e bandeira
    for parcelamento in intervalo_para_parcelas:
        num_parcelas = intervalo_para_parcelas[parcelamento]
        for bandeira in antecipacao.columns:
            for i in num_parcelas:
                # Calcular o valor líquido da parcela
                valor_liquido = valor_bruto - (valor_bruto * (taxas_cartao.loc[parcelamento, bandeira] / 100))
                if i == 0:
                    valor_liquido = valor_liquido
                else:
                    valor_liquido = valor_liquido / i
                
               
                # Calcular o valor da antecipação 
                                             
                if i == 1 or i == 0:
                    taxa_antec = (taxa_antecipacao/30) * 29
                else:
                    taxa_antec = (taxa_antecipacao/30) * ((30 * i) - 1)
                  
                
                valor_antecipacao = round((valor_liquido - (valor_liquido *  (taxa_antec/100))), 2)
                valor_antecipacao_total = round(((valor_liquido - (valor_liquido *  (taxa_antec/100))) * i),2)
                
                # geral = f'Parcela: R${valor_antecipacao} \nTotal: R${valor_antecipacao_total}'
                
                # Armazenar o valor final na valor_antecipacao_total de antecipação
                antecipacao.loc[i, bandeira] = valor_antecipacao_total
                antecipacao.loc[0, 'AMEX'] = '0.00'
                antecipacao.loc[0, 'HIPERCARD'] = '0.00'
                
    # Renomear os índices
    
    
    return formatacao_pivot_antecipacao(antecipacao)

def calcular_sem_antecipacao(taxas_cartao, valor_bruto):
    # Mapear cada intervalo de parcelamento para o número de parcelas
    intervalo_para_parcelas = {
        'DÉBITO': [0],
        'CRÉDITO': [1],
        '2X a 6X': list(range(2, 7)),
        '7X a 12X': list(range(7, 13))
    }
  
    # Criar um DataFrame para armazenar os resultados
    antecipacao = pd.DataFrame(index=list(range(0, 12)), columns=taxas_cartao.columns)
  
    # Calcular o valor antecipado para cada tipo de parcelamento e bandeira
    for parcelamento in intervalo_para_parcelas:
        num_parcelas = intervalo_para_parcelas[parcelamento]
        for bandeira in antecipacao.columns:
            for i in num_parcelas:
                # Calcular o valor líquido da parcela
                valor_liquido = round((valor_bruto - (valor_bruto * (taxas_cartao.loc[parcelamento, bandeira] / 100))),2)
                if i == 0:
                    valor_liquido = valor_liquido
                else:
                    valor_liquido = round((valor_liquido / i),2)
                # Armazenar o valor final na tabela de antecipação
                antecipacao.loc[i, bandeira] = valor_liquido
                antecipacao.loc[0, 'AMEX'] = '0.00'
                antecipacao.loc[0, 'HIPERCARD'] = '0.00'
    return formatacao_pivot_antecipacao(antecipacao)


def calcular_sem_antecipacao_total(taxas_cartao, valor_bruto):
    # Mapear cada intervalo de parcelamento para o número de parcelas
    intervalo_para_parcelas = {
        'DÉBITO': [0],
        'CRÉDITO': [1],
        '2X a 6X': list(range(2, 7)),
        '7X a 12X': list(range(7, 13))
    }
  
    # Criar um DataFrame para armazenar os resultados
    antecipacao = pd.DataFrame(index=list(range(0, 12)), columns=taxas_cartao.columns)
  
    # Calcular o valor antecipado para cada tipo de parcelamento e bandeira
    for parcelamento in intervalo_para_parcelas:
        num_parcelas = intervalo_para_parcelas[parcelamento]
        for bandeira in antecipacao.columns:
            for i in num_parcelas:
                # Calcular o valor líquido da parcela
                valor_liquido = round((valor_bruto - (valor_bruto * (taxas_cartao.loc[parcelamento, bandeira] / 100))),2)
                if i == 0:
                   valor_liquido = valor_liquido
                else:
                   valor_liquido = round((valor_liquido / i),2)
                 
                # Armazenar o valor final na tabela de antecipação
                antecipacao.loc[i, bandeira] = valor_liquido * i
                antecipacao.loc[0, 'AMEX'] = '0.00'
                antecipacao.loc[0, 'HIPERCARD'] = '0.00'
              
    return formatacao_pivot_antecipacao(antecipacao)




from sqlalchemy import create_engine, inspect, text
import sqlalchemy


def conectar_banco_de_dados():
    # Aqui você coloca sua lógica para conectar ao banco de dados e retorna a conexão
    load_dotenv()
    connection_string = f'postgresql://{os.getenv("DB_USERNAME")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:5432/{os.getenv("DB_DATABASE")}'
    return create_engine(connection_string)

def table_exists(engine, table_name):
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def atualizar_tabela_principal(arquivo_excel):
    # Backup da tabela principal
    engine = conectar_banco_de_dados()
    if table_exists(engine, 'mdr_adiq_up'):
        df_backup = pd.read_sql_query('SELECT * FROM mdr_adiq_up', engine)
        df_backup.to_sql('mdr_adiq_up_bkp', engine, if_exists='replace', index=False)

    # Leitura e preparação dos dados da planilha
    df = pd.read_excel(arquivo_excel, usecols=['Bandeira', 'Produto', 'Tp Parcelado', 'Mcc', 'Intercâmbio Mediana'])
    df.columns = ['bandeira', 'produto', 'tipo_parcelamento', 'mcc', 'intercambio_mediano']

    # Padronizar as colunas
    # Verificar se os valores são de tipo string antes de usar o método .str
    if df['intercambio_mediano'].dtype == 'object':
        df['intercambio_mediano'] = df['intercambio_mediano'].str.replace('%', '').str.replace(',', '.').astype(float)
       
    
    df['intercambio_mediano'] = df['intercambio_mediano'] * 100
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
    # Análise e atualização na tabela principal
    query = """
            UPDATE mdr_adiq_up AS main
            SET intercambio_mediano = temp.intercambio_mediano
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
            INSERT INTO mdr_adiq_up (bandeira, tipo_parcelamento, produto, mcc, intercambio_mediano)
            SELECT temp.bandeira, temp.tipo_parcelamento, temp.produto, temp.mcc, temp.intercambio_mediano
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
            GROUP BY bandeira, produto, tipo_parcelamento, mcc, intercambio_mediano
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
    
    # # Excluir tabela temporária
    # with engine.begin() as conn:
    #     conn.execute(text('DROP TABLE IF EXISTS mdr_adiq_up_temp;'))

    relatorio = {
        'Total de registros na base ADIQ Anterior': total_registros_main,
        'Total de registros no arquivo Excel': total_registros_temp,
        'Total de Registros adicionados': registros_adicionados,
        'Total de Registros atualizados': registros_atualizados,
        'Registros duplicados no arquivo Excel': registros_duplicados,
        'Total de Registro atual na base ADIQ': total_registros_main_pos
    }

    return relatorio

from urllib.parse import quote
import pandas as pd
import psycopg2 
import streamlit as st
import os
from dotenv import load_dotenv
import psycopg2 
from sqlalchemy import create_engine, inspect, text

# def conectar_banco_de_dados():
#     """
#     Conecta ao banco de dados PostgreSQL.

#     Retorna:
#         Engine: Conexão com o banco de dados.
#     """
#     load_dotenv()
#     connection_string = f'postgresql://{os.getenv("DB_USERNAME")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:5432/{os.getenv("DB_DATABASE")}'
#     return create_engine(connection_string)

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

def conectar_banco_de_dados_engine():
    """
    Conecta ao banco de dados PostgreSQL e testa a conexão.
    """
    load_dotenv()
    connection_string = f'postgresql://{os.getenv("DB_USERNAME")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:5432/{os.getenv("DB_DATABASE")}'
    engine = create_engine(connection_string)

    # Testar a conexão
    try:
        with engine.connect() as connection_string:
            print("Conexão bem-sucedida!")
    except Exception as e:
        print(f"Erro ao conectar: {e}")
    
    return engine

print(f'Dados Banco de dados',{conectar_banco_de_dados_engine()})

# Função para carregar os dados dos códigos MCC do banco de dados
@st.cache_resource
def carregar_dados_mcc():
    """
    Carrega os dados dos códigos MCC (Merchant Category Code) de um banco de dados.

    Returns:
        DataFrame: DataFrame contendo os dados dos códigos MCC.

    """
    conn = conectar_banco_de_dados_engine()  # Função para conectar ao banco de dados
    query = "SELECT * FROM base_mcc_geral"  # Consulta SQL para selecionar todos os dados da tabela base_mcc_geral
    return pd.read_sql(query, conn)  # Retorna os dados como DataFrame

def carregar_dados_propostas():
    """
    Carrega os dados dos códigos MCC (Merchant Category Code) de um banco de dados.

    Returns:
        DataFrame: DataFrame contendo os dados dos códigos MCC.

    """
    conn = conectar_banco_de_dados_engine()  # Função para conectar ao banco de dados
    query = "SELECT * FROM propostas"  # Consulta SQL para selecionar todos os dados da tabela base_mcc_geral
    return pd.read_sql(query, conn)  # Retorna os dados como DataFrame

def carregar_dados_mdr_propostas():
    """
    Carrega os dados dos códigos MCC (Merchant Category Code) de um banco de dados.

    Returns:
        DataFrame: DataFrame contendo os dados dos códigos MCC.

    """
    conn = conectar_banco_de_dados_engine()  # Função para conectar ao banco de dados
    query = "SELECT * FROM mdr_propostas"  # Consulta SQL para selecionar todos os dados da tabela base_mcc_geral
    return pd.read_sql(query, conn)  # Retorna os dados como DataFrame

# Função para carregar os dados da adquirente Adiq do banco de dados
@st.cache_resource
def carregar_dados_adiq():
    """
    Carrega os dados da adquirente Adiq de um banco de dados.

    Returns:
        DataFrame: DataFrame contendo os dados da adquirente Adiq.

    """
    conn = conectar_banco_de_dados_engine()  # Função para conectar ao banco de dados
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
    conn = conectar_banco_de_dados_engine()  # Função para conectar ao banco de dados
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
    conn = conectar_banco_de_dados_engine()  # Função para conectar ao banco de dados
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
    conn = conectar_banco_de_dados_engine()  # Conecta ao banco de dados
    query = "SELECT * FROM mcc_cnae"  # Consulta SQL para selecionar todos os dados da tabela mcc_cnae
    return pd.read_sql(query, conn)  # Retorna os dados como DataFrame

# Função para carregar os dados de configuração do banco de dados
def carregar_dados_config():
    """
    Carrega os dados de configuração de um banco de dados.

    Returns:
        DataFrame: DataFrame contendo os dados de configuração.
    """
    engine = conectar_banco_de_dados_engine()  # Conecta ao banco de dados usando SQLAlchemy
    query = "SELECT * FROM config"  # Consulta SQL para selecionar todos os dados da tabela config
    return pd.read_sql(query, engine)  # Retorna os dados como DataFrame

def carregar_dados_spread_comercial():
    """
    Carrega os dados de configuração de um banco de dados.

    Returns:
        DataFrame: DataFrame contendo os dados de configuração.
    """
    conn = conectar_banco_de_dados_engine()  # Conecta ao banco de dados
    query = "SELECT * FROM spread_comercial"  # Consulta SQL para selecionar todos os dados da tabela config
    return pd.read_sql(query, conn)  # Retorna os dados como DataFrame


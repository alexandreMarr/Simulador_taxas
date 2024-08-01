import pandas as pd
import streamlit as st
import utils.conexaoBD as confBD
from sqlalchemy import create_engine, inspect, text

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
    engine = confBD.conectar_banco_de_dados()
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
    engine = confBD.conectar_banco_de_dados()

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
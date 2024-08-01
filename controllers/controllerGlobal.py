import pandas as pd
import streamlit as st


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
    pivot_table = pivot_table.fillna(0.0)

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


def exibir_bandeiras_com_inputs(bandeiras, parcelamentos, bandeiras_df, spreads):
    ordem_desejada_bandeira = ['MASTERCARD', 'VISA', 'ELO', 'HIPERCARD', 'AMEX']
    ordem_desejada_parcelamento = ['DÉBITO', 'CRÉDITO', '2X a 6X', '7X a 12X', '13X a 18X']
    bandeiras = [p for p in ordem_desejada_bandeira if p in bandeiras]
    parcelamentos = [p for p in ordem_desejada_parcelamento if p in parcelamentos]
    
    # Inicializar todas as chaves no dicionário spreads com valor padrão
    for bandeira in bandeiras:
        for parcelamento in parcelamentos:
            spread_key = f"{bandeira}_{parcelamento}_spread"
            spreads[spread_key] = 0.0

    cols = st.columns(5)
    col_idx = 0

    for bandeira in bandeiras:
        with cols[col_idx % 5]:
            url_imagem = bandeiras_df[bandeiras_df['BANDEIRA'] == bandeira]['URL_IMAGEM'].iloc[0]
            st.markdown(f'''
            <div style="text-align: center; margin: 10px;">
                <img src="{url_imagem}" alt="{bandeira}" style="width:80px; height:60px; display: block; margin: 0 auto;">
            </div>
            ''', unsafe_allow_html=True)
            
            for parcelamento in parcelamentos:
                # Pular os inputs de HIPERCARD DÉBITO e AMEX DÉBITO
                if (bandeira == 'HIPERCARD' and parcelamento == 'DÉBITO') or (bandeira == 'AMEX' and parcelamento == 'DÉBITO'):
                    continue
                spread_key = f"{bandeira}_{parcelamento}_spread"
                spreads[spread_key] = st.number_input(parcelamento, min_value=0.0, key=spread_key)
        col_idx += 1

    st.write("")


def exibir_bandeiras_com_inputs_executivos(bandeiras, parcelamentos, bandeiras_df, spreads):
    ordem_desejada_bandeira = ['MASTERCARD', 'VISA', 'ELO', 'HIPERCARD', 'AMEX']
    ordem_desejada_parcelamento = ['DÉBITO', 'CRÉDITO', '2X a 6X', '7X a 12X', '13X a 18X']
    bandeiras = [p for p in ordem_desejada_bandeira if p in bandeiras]
    parcelamentos = [p for p in ordem_desejada_parcelamento if p in parcelamentos]
    
    # Inicializar todas as chaves no dicionário spreads com valor padrão
    for bandeira in bandeiras:
        for parcelamento in parcelamentos:
            spread_key = f"{bandeira}_{parcelamento}_spreads"
            spreads[spread_key] = 0.0

    cols = st.columns(5)
    col_idx = 0

    for bandeira in bandeiras:
        with cols[col_idx % 5]:
            url_imagem = bandeiras_df[bandeiras_df['BANDEIRA'] == bandeira]['URL_IMAGEM'].iloc[0]
            st.markdown(f'''
            <div style="text-align: center; margin: 10px;">
                <img src="{url_imagem}" alt="{bandeira}" style="width:80px; height:60px; display: block; margin: 0 auto;">
            </div>
            ''', unsafe_allow_html=True)
            
            for parcelamento in parcelamentos:
                # Pular os inputs de HIPERCARD DÉBITO e AMEX DÉBITO
                if (bandeira == 'HIPERCARD' and parcelamento == 'DÉBITO') or (bandeira == 'AMEX' and parcelamento == 'DÉBITO'):
                    continue
                spread_key = f"{bandeira}_{parcelamento}_spreads"
                spreads[spread_key] = st.number_input(parcelamento, min_value=0.0, key=spread_key)
        col_idx += 1

    st.write("")


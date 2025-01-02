import pandas as pd
import streamlit as st
import utils.conexaoBD as confBD
import os
from dotenv import load_dotenv

# Função para carregar os URLs das imagens das bandeiras de cartão de crédito
def carregar_urls_das_bandeiras():
    load_dotenv()
    """
    Carrega os URLs das imagens das bandeiras de cartão de crédito.

    Returns:
        DataFrame: DataFrame contendo os URLs das imagens das bandeiras.
    """
    # Dicionário contendo os URLs das imagens das bandeiras
    data = {
    'BANDEIRA': ['MASTERCARD', 'VISA','ELO', 'AMEX', 'HIPERCARD'],
    'URL_IMAGEM': [
        f'{os.getenv("URL_SERVER_IMAGENS")}/master.png',
        f'{os.getenv("URL_SERVER_IMAGENS")}/visa.png',
        f'{os.getenv("URL_SERVER_IMAGENS")}/elo.png',
        f'{os.getenv("URL_SERVER_IMAGENS")}/amex.png',
        f'{os.getenv("URL_SERVER_IMAGENS")}/hiper.png'
    ]
    }



    return pd.DataFrame(data)  # Retorna os dados como DataFrame


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
    ordem_desejada_parcelamento = ['DÉBITO', 'CRÉDITO', '2X a 6X', '7X a 12X', '13X a 21X', '22X a 24X']
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

    # Adicionar '*' na célula específica (13X a 21X, HIPERCARD)
    if "13X a 21X" in pivot_table.index and "HIPERCARD" in pivot_table.columns:
        valor_original = pivot_table.at["13X a 21X", "HIPERCARD"]
        pivot_table.at["13X a 21X", "HIPERCARD"] = f"#{valor_original:.2f}%"  # Formata com duas casas decimais e adiciona '#'
    
    # Aplicar a formatação à tabela
    pivot_table_formatada = pivot_table.applymap(formatar_percentagem)
    
    bandeiras_df = carregar_urls_das_bandeiras()
    
    # Substituir os nomes das bandeiras pelos URLs das imagens na pivot table
    for bandeira in pivot_table_formatada.columns:
        if bandeira in bandeiras_df['BANDEIRA'].values:
            # Obtém o URL da imagem da bandeira atual
            url_imagem = bandeiras_df[bandeiras_df['BANDEIRA'] == bandeira]['URL_IMAGEM'].iloc[0]
            # Substitui o nome da bandeira pelo HTML da imagem na tabela pivot
            pivot_table_formatada.rename(columns={bandeira: f'<img src="{url_imagem}" alt="{bandeira}" style="width:70px;height:40px; text-align: center;">'}, inplace=True)

    # Estilo condicional para a célula "13X a 21X" da coluna "HIPERCARD"
    def estilo_condicional(val):
        # Se o valor for uma string começando com '#', colorir de laranja
        if isinstance(val, str) and val.startswith('#'):
            return 'background-color: #ffffff; color: #ff6100;'  # Define fundo laranja para valores formatados
        return ''  # Sem alteração para outros valores

    # Aplicar o estilo à tabela
    pivot_table_formatada = pivot_table_formatada.style.applymap(estilo_condicional)

    # Retornar a tabela formatada
    return pivot_table_formatada


def exibir_bandeiras_com_inputs(bandeiras, parcelamentos, bandeiras_df, spreads):
    ordem_desejada_bandeira = ['MASTERCARD', 'VISA', 'ELO', 'HIPERCARD', 'AMEX']
    ordem_desejada_parcelamento = ['DÉBITO', 'CRÉDITO', '2X a 6X', '7X a 12X', '13X a 21X', '22X a 24X']
    bandeiras = [p for p in ordem_desejada_bandeira if p in bandeiras]
    parcelamentos = [p for p in ordem_desejada_parcelamento if p in parcelamentos]
    
    # Inicializar todas as chaves no dicionário spreads com valor padrão
    for bandeira in bandeiras:
        for parcelamento in parcelamentos:
            spread_key = f"{bandeira}_{parcelamento}_spread"
            spreads.setdefault(spread_key, 0.00)  # Use setdefault para evitar KeyError


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
                is_disabled = (bandeira == 'HIPERCARD' and parcelamento == 'DÉBITO') or \
                              (bandeira == 'AMEX' and parcelamento == 'DÉBITO') or \
                              (bandeira in ['ELO', 'HIPERCARD', 'MASTERCARD'] and parcelamento == '22X a 24X')
                
                if is_disabled:
                    # HTML para tooltip
                    tooltip_html = f"""
                    <div style="position: relative; display: inline-block; margin-bottom: 10px;">
                        <label> {parcelamento} </label>
                        <br>
                        <input type="text" value="Indisponível" disabled 
                            style="width: 100px; text-align: center; cursor: not-allowed; color: #00000066; border-color: #00000000; -webkit-text-stroke-width: medium;">
            
                    </div>
                    """
                    st.markdown(tooltip_html, unsafe_allow_html=True)


                else:
                    spread_key = f"{bandeira}_{parcelamento}_spread"
                    spreads[spread_key] = st.number_input(parcelamento, min_value=0.0, key=spread_key)
        col_idx += 1

    st.write("")
    

def exibir_bandeiras_com_inputs_executivos(bandeiras, parcelamentos, bandeiras_df, spreads, check_desconto):
    ordem_desejada_bandeira = ['MASTERCARD', 'VISA', 'ELO', 'HIPERCARD', 'AMEX']
    ordem_desejada_parcelamento = ['DÉBITO', 'CRÉDITO', '2X a 6X', '7X a 12X', '13X a 21X', '22X a 24X']
    bandeiras = [p for p in ordem_desejada_bandeira if p in bandeiras]
    parcelamentos = [p for p in ordem_desejada_parcelamento if p in parcelamentos]
    config = confBD.carregar_dados_config()
    
    # Inicializar todas as chaves no dicionário spreads com valor padrão
    for bandeira in bandeiras:
        for parcelamento in parcelamentos:
            spread_key = f"{bandeira}_{parcelamento}_spreads"
            spreads.setdefault(spread_key, 0.00)

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
                # Identificar casos desabilitados
                is_disabled = (bandeira == 'HIPERCARD' and parcelamento == 'DÉBITO') or \
                              (bandeira == 'AMEX' and parcelamento == 'DÉBITO') or \
                              (bandeira in ['ELO', 'HIPERCARD', 'MASTERCARD'] and parcelamento == '22X a 24X')
                if is_disabled:
                    # HTML para tooltip
                    tooltip_html = f"""
                    <div style="position: relative; display: inline-block; margin-bottom: 10px;">
                        <label> {parcelamento} </label>
                        <br>
                        <input type="text" value="Indisponível" disabled 
                            style="width: 100px; text-align: center; cursor: not-allowed; color: #00000066; border-color: #00000000; -webkit-text-stroke-width: medium;">
            
                    </div>
                    """
                    st.markdown(tooltip_html, unsafe_allow_html=True)
    
                else:
                    spread_key = f"{bandeira}_{parcelamento}_spreads"
                    if check_desconto:
                        spreads[spread_key] = st.number_input(parcelamento, value=0.0, min_value=-config.loc[0, "desconto"], key=spread_key)
                    else:
                        spreads[spread_key] = st.number_input(parcelamento, value=0.0, min_value=0.00, key=spread_key)
        col_idx += 1

    st.write("")


def exibir_checkboxes_parcelamentos(parcelamentos,  unique_id=""):
    checkboxes = {}
    ordem_desejada_parcelamento = ['DÉBITO', 'CRÉDITO', '2X a 6X', '7X a 12X', '13X a 21X', '22X a 24X']
    parcelamentos = [p for p in ordem_desejada_parcelamento if p in parcelamentos]
    
    cols = st.columns(len(parcelamentos))
    
    for idx, parcelamento in enumerate(parcelamentos):
        with cols[idx]:
            checkboxes[parcelamento] = st.checkbox(parcelamento, value=True, key=f"checkbox_{parcelamento}_{unique_id}")
    
    return checkboxes

def footer():
    footer = """
    <style>
  

    .footer {
        width: 100%;
        background-color: white;
        color: black;
        text-align: center;
        padding: 10px 0;
        position: relative;
    
    }

    
    </style>
    <div class="footer">
    <p>© 2024 <a style='display: inline; text-align: center;' href="https://rovemabank.com.br/" target="_blank">Rovema Bank</a> Todos os direitos reservados.</p>
    </div>
    """

    st.markdown(footer, unsafe_allow_html=True)




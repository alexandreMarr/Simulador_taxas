import streamlit as st
import utils.sidebar as men
import utils.conexaoBD as confBD
import utils.auth as at
import utils.main as main
import controllers.controllerSimulador as ControllerSimulador

def tabela_de_taxas():
    st.header('Tabela de Taxas', divider='blue')
        # Dicionário com links de imagens das adquirentes
    data = {
        'Adiq': 'https://i.ibb.co/0XnDtz7/adiq.png',
        'Getnet': 'https://i.ibb.co/CztNnM8/getnet.png'
    }
    filtros = {}

    # Dividir a tela em três colunas
    col1, col2, col3 = st.columns([3, 2, 5])

    # Primeira coluna para o selectbox da adquirente
    with col1:
        adiquirente_selecionado = st.selectbox("Adiquirente:", list(data.keys()), key="adiquirente_selectbox_taxas")

    # Segunda coluna para exibir a imagem da adquirente selecionada
    with col2:
        if adiquirente_selecionado:
                st.image(data[adiquirente_selecionado], width=100)
        # Carregamento dos dados do banco de dados conforme adquirente selecionada
    if adiquirente_selecionado == "Adiq":
        dados_do_banco_de_dados = confBD.carregar_dados_adiq()
    else:
        dados_do_banco_de_dados = confBD.carregar_dados_getnet()

    # Terceira coluna para os filtros
    with col3:
        # Se a adquirente for 'Getnet', exibe filtros específicos
        if adiquirente_selecionado == 'Getnet':
            col1, col2 = st.columns([1, 1])
            with col1:
                filtros['mcc_filtrado'] = st.multiselect("Filtro MCC:", sorted(dados_do_banco_de_dados['mcc'].unique()), placeholder="MCC", key="mcc_filtrado_getnet")

            with col2:
                filtros['tipo_taxa'] = st.multiselect("Filtro Tipo de Taxa:", sorted(dados_do_banco_de_dados['tipo_taxa'].unique()), placeholder="Tipo de Taxa", key="tipo_taxa_getnet")
        else:
            # Se a adquirente for 'Adiq', exibe apenas filtro de MCC
            mcc_unique = dados_do_banco_de_dados['mcc'].dropna().unique()
            filtros['mcc_filtrado'] = st.multiselect("Filtro MCC:", sorted(mcc_unique), placeholder="MCC", key="mcc_filtrado_adiq")
    # Coluna para filtros de bandeira e tipo de parcelamento
    col1, col2 = st.columns([1, 1])
    with col1:
        filtros['bandeira_filtrada'] = st.multiselect("Filtro Bandeira:", sorted(dados_do_banco_de_dados['Bandeira'].unique()), placeholder="Bandeira", key="bandeira_filtrada")
    with col2:
        filtros['parcelamento_filtrado'] = st.multiselect("Filtro Tipo de Parcelamento:", sorted(dados_do_banco_de_dados['Parcelamento'].unique()), placeholder="Tipo de Parcelamento", key="parcelamento_filtrado")
    # Divisor
    st.divider()

    # Carrega e exibe a tabela de taxas com base nos filtros
    tabela = ControllerSimulador.carregar_tabela_taxas(adiquirente_selecionado, dados_do_banco_de_dados, filtros)
    st.write(tabela)




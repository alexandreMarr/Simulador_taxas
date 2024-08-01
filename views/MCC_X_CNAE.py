import streamlit as st
import utils.sidebar as men
import utils.auth as at
import utils.main as main
import utils.conexaoBD as confDB
import controllers.controllerSimulador as ControllerSimulador

# Função principal
def mcc_x_cnae():
    # Título da página
    st.header('MCC X CNAE', divider='blue')

    # Carrega os dados MCC X CNAE
    dataset = confDB.carregar_dados_mcc_cnae()
    filtro = {}

    # Filtros
    col1, col2 = st.columns([1, 1])
    with col1:
        filtro['filtro_cnae'] = st.multiselect("Filtro CNAE:", sorted(dataset['cnae'].unique()), placeholder="CNAE")

    with col2:
        filtro['filtro_mcc'] = st.multiselect("Filtro MCC:", sorted(dataset['mcc'].unique()), placeholder="MCC")

    filtro['filtro_grupo'] = st.multiselect("Filtro Grupo/Ramo de Atividade:", sorted(dataset['grupo_ramo_atividade'].unique()), placeholder="Grupo/Ramo de Atividade")

    st.divider() 

    # Carrega e exibe a tabela MCC X CNAE com base nos filtros
    tabela = ControllerSimulador.carregar_tabela_mcc_cnae(dataset, filtro)
    st.write(tabela)

    


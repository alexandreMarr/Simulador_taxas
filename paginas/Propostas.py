from datetime import time
import random
import streamlit as st
from controllers import controllerProposta
import utils.sidebar as men
import utils.main as main
from views.Paramentros import paramentros, Parametros_spreed_comercial
from views.Atualização_de_Base import update
from views.Tabela_de_Taxas import tabela_de_taxas
from views.MCC_X_CNAE import mcc_x_cnae
import streamlit_authenticator as stauth
import utils.auth as at
from streamlit_authenticator.utilities.exceptions import LoginError
import utils.conexaoBD as confBD
import time

main.config("wide", "Propostas")
def login(authenticator):
    try:
        nome, authentication_status, username, nivel = authenticator.login(
            'main',
            fields={'form name': 'https://i.ibb.co/R4xBj4V/Rovema-Pay.jpg', 'Username': 'Usuário', 'Password': 'Senha', 'nivel': 'nivel'}
        )
    except LoginError as e:
        st.error(e)
    return nome, authentication_status, username, nivel

def bory(nivel):
    st.header('Propostas', divider='blue')

    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
    filtros = {}
    propostas_db = confBD.carregar_dados_propostas()

    with col1:
        filtros['razao_social'] = st.multiselect("Razão Social:", sorted(propostas_db['razao_social'].unique()), placeholder="Razão Social", key="Razao_social")

    with col2:
        filtros['cnpj'] = st.multiselect("CNPJ:", sorted(propostas_db['cnpj'].unique()), placeholder="cnpj", key="cnpj")

    with col3:
        filtros['nome_executivo'] = st.multiselect("Executivo:", sorted(propostas_db['nome_executivo'].unique()), placeholder="Executivo", key="execuivo")

    with col4:
        filtros['data_geracao'] = st.date_input("Data Geração:",value=None, format='DD/MM/YYYY')

    st.divider()
    
    col1, col2 = st.columns([1,9])

    with col1:
        id = st.selectbox('ID da Proposta',propostas_db['id'], key='selectbox_id')
     
    with col2:
        st.write('')
        st.write('')
        controllerProposta.buscar_dados_pdf(id)
            


    propostas = controllerProposta.carregar_tabela(filtros, propostas_db)

    # Aplicar o estilo ao DataFrame
    tabela_estilizada = controllerProposta.estilo_personalizado(propostas)

    # Exibir a tabela estilizada no Streamlit
    st.dataframe(tabela_estilizada, use_container_width=True)
        # Adiciona uma coluna com botões
 


def main():
    authenticator = at.initialize_session_state()
    nome, authentication_status, username, nivel = login(authenticator)
    men.menu(authenticator)

    if authentication_status:
        bory(nivel)
    elif authentication_status is False:
        st.error('Usuário ou Senha Incorretos')
    elif authentication_status is None:
        st.write("")

at.update_config()

if __name__ == "__main__":
    main()
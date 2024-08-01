from datetime import date
import re
import streamlit as st
from controllers import controllerProposta
import utils.sidebar as men
import utils.main as main
from views.Simulador import simulador, simulador_Avançado
from views.Simulador_executivos import simulador_comercial
from views.Tabela_de_Taxas import tabela_de_taxas
from views.MCC_X_CNAE import mcc_x_cnae
import streamlit_authenticator as stauth
import utils.auth as at
from streamlit_authenticator.utilities.exceptions import LoginError

main.config("wide", "Simulador de Taxas")
def login(authenticator):
    try:
        nome, authentication_status, username, nivel = authenticator.login(
            'main',
            fields={'form name': 'https://i.ibb.co/R4xBj4V/Rovema-Pay.jpg', 'Username': 'Usuário', 'Password': 'Senha', 'nivel': 'nivel'}
        )
    except LoginError as e:
        st.error(e)
    return nome, authentication_status, username, nivel

def inicial_bar(nivel):
    if nivel == "user":
        tab1, tab2 = st.tabs([" **Simulador** ", " **MCC X CNAE** "])
        with tab1:
            simulador_comercial()
        with tab2:
            mcc_x_cnae()
    elif nivel == "admin" or nivel == "admin_master" :
        tab1, tab2, tab3, tab4,tab5 = st.tabs([" **Simulador** ", " **Simulador Avançado** "," **Simulador Executivos** "," **Tabela de Taxas** ", " **MCC X CNAE** "])
        with tab1:
            simulador()
        with tab2:
            simulador_Avançado()
        with tab3:
            simulador_comercial()
        with tab4:
            tabela_de_taxas()
        with tab5:
            mcc_x_cnae()

def main():
    authenticator = at.initialize_session_state()
    nome, authentication_status, username, nivel = login(authenticator)
    men.menu(authenticator)

    if authentication_status:
        inicial_bar(nivel)

    elif authentication_status is False:
        st.error('Usuário ou Senha Incorretos')
    elif authentication_status is None:
        st.write("")

at.update_config()

if __name__ == "__main__":
    main()

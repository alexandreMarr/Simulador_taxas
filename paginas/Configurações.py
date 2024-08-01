import streamlit as st
import utils.sidebar as men
import utils.main as main
from views.Paramentros import paramentros, Parametros_spreed_comercial
from views.Atualização_de_Base import update
from views.Tabela_de_Taxas import tabela_de_taxas
from views.MCC_X_CNAE import mcc_x_cnae
import streamlit_authenticator as stauth
import utils.auth as at
from streamlit_authenticator.utilities.exceptions import LoginError

main.config("", "Configurações")
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
    if nivel == "user":
        st.write()
    elif nivel == "admin_master":
        tab1, tab2,tab3 = st.tabs([" **Parâmentros** ", " **Update Base** ", " **Paramentros Spreed Comercial** "])
        with tab1:
            paramentros()
        with tab2:
            update()
        with tab3:
            Parametros_spreed_comercial()
    elif nivel == "admin":
        tab1, tab2 = st.tabs([" **Parâmentros** "," **Paramentros Spreed Comercial** "])
        with tab1:
            paramentros()
        with tab2:
            Parametros_spreed_comercial()

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

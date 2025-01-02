import streamlit as st
from controllers import controllerGlobal
import utils.sidebar as men
import utils.main as mains
import views.user as user

import streamlit_authenticator as stauth
import utils.auth as at
from streamlit_authenticator.utilities.exceptions import LoginError

def login(authenticator):
    try:
        nome, authentication_status, username, nivel = authenticator.login(
            'main',
            fields={'form name': 'https://i.ibb.co/R4xBj4V/Rovema-Pay.jpg', 'Username': 'Usuário', 'Password': 'Senha', 'nivel': 'nivel'}
        )
    except LoginError as e:
        st.error(e)
    return nome, authentication_status, username, nivel

def bory(nivel,authenticator):
    if nivel == "user":
        user.reset_senha(authenticator)
    elif nivel == "admin_master":
        tab1, tab2, tab3, tab4 = st.tabs([" **Adicionar Usuário** ", " **Alterar Minha Senha** ","**Atualizar Usuário**","**Resetar Senha Usuário**"])
        with tab1:
            user.add_user(authenticator)
        with tab2:
            user.reset_senha(authenticator)
        with tab3:
            user.atualizar_usuario(authenticator)
        with tab4:
            user.esqueci_senha(authenticator)
    elif nivel == "admin":
        tab1, tab2 = st.tabs(["**Alterar Minha Senha**","**Resetar Senha Usuário**"])
        with tab1:
            user.reset_senha(authenticator)
        with tab2:
            user.esqueci_senha(authenticator)


def main():
    mains.config("", "Usuário")
    authenticator = at.initialize_session_state()
    nome, authentication_status, username, nivel = login(authenticator)
    men.menu(authenticator)

    if authentication_status:
        bory(nivel,authenticator)
        controllerGlobal.footer()
    elif authentication_status is False:
        st.error('Usuário ou Senha Incorretos')
    elif authentication_status is None:
        st.write("")

at.update_config()

if __name__ == "__main__":
    main()

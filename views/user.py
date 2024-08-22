
import streamlit as st
from streamlit_authenticator.utilities.exceptions import (CredentialsError,
                                                          ForgotError,
                                                          LoginError,
                                                          RegisterError,
                                                          ResetError,
                                                          UpdateError) 


def reset_senha(authenticator):
    # Creating a password reset widget
    if st.session_state["authentication_status"]:
        try:
            if authenticator.reset_password(st.session_state["username"], fields={'Form name':'Alterar minha Senha', 'Current password':'Senha Antiga',
                      'New password':'Nova Senha','Repeat password':'Confirme Nova Senha',
                      'Reset':'Alterar'}):
                st.success('Senha Alterada com Sucesso!')
        except ResetError as e:
            st.error(e)
        except CredentialsError as e:
            st.error(e)


def add_user(authenticator):
# # Creating a new user registration widget
    try:
        (email_of_registered_user,
        username_of_registered_user,
        name_of_registered_user, nivel) = authenticator.register_user(pre_authorization=False,fields={'Form name': 'Cadastro de Usuário','Email':'Email', 'Username':'Usuário',
                'Password':'Senha', 'Repeat password':'Confirmar Senha',
                'Register':'Cadastrar', 'Nivel':'Nivel'})
        if email_of_registered_user:
            st.success('Usuario cadastrado com sucesso')
    except RegisterError as e:
        st.error(e)

def esqueci_senha(authenticator):
# # Creating a forgot password widget
    try:
        (username_of_forgotten_password,
            email_of_forgotten_password,
            new_random_password) = authenticator.forgot_password(fields={'Form name':'Restaurar Senha Usuário','Username':'Usuário', 'Submit':'Gerar Nova Senha'})
        if username_of_forgotten_password:
            st.success(f'Nova senha gerada com sucesso: {new_random_password}')
            # Random password to be transferred to the user securely
        elif not username_of_forgotten_password:
            st.error('Usuário Não Encontrado')
    except ForgotError as e:
        st.error(e)

def esqueci_usuario(authenticator):
# # Creating a forgot username widget
    try:
        (username_of_forgotten_username,
            email_of_forgotten_username) = authenticator.forgot_username()
        if username_of_forgotten_username:
            st.success('Username sent securely')
            # Username to be transferred to the user securely
        elif not username_of_forgotten_username:
            st.error('Email not found')
    except ForgotError as e:
        st.error(e)

def atualizar_usuario(authenticator):
# # Creating an update user details widget
    if st.session_state["authentication_status"]:
        try:
            if authenticator.update_user_details(st.session_state["username"]):
                st.success('Entries updated successfully')
        except UpdateError as e:
            st.error(e)


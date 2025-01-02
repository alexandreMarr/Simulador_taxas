from st_pages import Page, show_pages, hide_pages
import streamlit as st
import utils.loadLogo as logo


def menu(authenticator):
        logo.view_logo_admin()
        if st.session_state['authentication_status']:
            show_pages(
                [
                    Page("login.py", "Simulador", ":heavy_division_sign:"),
                    Page("paginas/Configurações.py", "Configurações", ":gear:"),
                    Page("paginas/Users.py", "Usuário", ":male-office-worker:"),
                    Page("paginas/Propostas.py", "Propostas", ":page_facing_up:"),
                ]
            )  
            authenticator.logout('Sair', 'sidebar')
        else:
            st.markdown(
                """
            <style>
                [data-testid="stSidebar"] {
                    display: none
                }
            </style>
            """,
                unsafe_allow_html=True,
            )
        
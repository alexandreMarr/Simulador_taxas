import streamlit as st
import utils.auth as at

# Configurações da página do Streamlit
def config(layout, title):
    """
    Configurações da página do Streamlit.

    Args:
        layout (str): Layout da página ('wide' ou 'centered').
        title (str): Título da página.

    Returns:
        None
    
    """
    if layout:
        layout = layout
    else:
        layout = 'centered'
        
    st.set_page_config(
        page_title=title,  # Título da página
        page_icon="https://i.ibb.co/8PXXTHZ/Group-329-Copia.png",  # Ícone da página
        layout=layout,  # Layout centralizado
    )
    # Carrega o arquivo de estilo CSS
    with open("style/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        


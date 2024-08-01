import streamlit as st

def view_logo_admin():
    img_path = "https://i.ibb.co/0VQzxk1/Group-329-Copia-1.png"
    width = "150px"
    height = "80px"
    st.sidebar.markdown(
        f'''
        <div style="display: flex; flex-direction: column;position:fixed; align-items: center; justify-content: center; transform: translateY(-225%); left: 30px;">
            <img src="{img_path}" style="width:{width}; height:{height};" class="cover-glow-img">
            <p style="color: #FFFFFF;">Bem vindo {st.session_state["name"]}</p>
        </div>
        ''',
        unsafe_allow_html=True,
    )
    
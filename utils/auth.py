import streamlit as st
import streamlit_authenticator as stauth
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

mongoUri = os.getenv('URI_MONGO')

def load_config_from_db():
    client = MongoClient(mongoUri)
    db = client.get_database('simulador_streamlit')  # Use `get_database()` para obter o banco de dados
    collection = db['users']
    config_data = collection.find_one({})
    if config_data:
        config_data.pop('_id', None)
    return config_data


config = load_config_from_db()

def update_config():
    client = MongoClient(mongoUri)
    db = client['simulador_streamlit']
    collection = db['users']
    collection.replace_one({}, config, upsert=True)

def initialize_session_state():
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )
    keys = {
        'authentication_status': None,
        'logout': None,
        'name': None,
        'failed_login_attempts': None,
        'username': None,
        'token': None,
        'nivel': None
    }
    for key, value in keys.items():
        if key not in st.session_state:
            st.session_state[key] = value

    return authenticator

import streamlit as st
import pandas as pd
import function as fun
from dotenv import load_dotenv
import os
import streamlit.components.v1 as components

fun.config("","Configurações")

# Título da página
st.title("")
st.header('Parâmetros', divider='green')

def main():
    load_dotenv()
    senha = st.text_input('Digite a senha:', type='password')

    
    if senha == os.getenv("PASSWORD_CONFIG"):
        config = fun.carregar_dados_config()   
        col1, col2, col3 = st.columns([2, 2, 2])
        
        with col1:
                st.header('Geral', divider='gray')
                
                # Obter o valor da coluna 'custo' e 'valor_custo'
                custo = config.loc[0, "custo"]
                valor_custo = config.loc[0, "valor_custo"]

                    
                # Determinar qual opção do botão de rádio deve estar marcada
                opcao_radio = st.toggle("Custo", custo)

                # Se o custo estiver marcado como "Sim", mostrar o campo para inserir o valor
                if opcao_radio == True:
                    valor_custo = st.number_input(f"Valor", value=valor_custo)
            
                # Botão para atualizar os parâmetros no banco de dados
                if st.button("Salvar"):
                    # Atualizar os valores no DataFrame
                    config.loc[0, "custo"] = opcao_radio
                    config.loc[0, "valor_custo"] = valor_custo
                    
                    # Atualizar os parâmetros no banco de dados
                    fun.atualizar_dados_config(config)
                    st.success('Parâmetros atualizados com sucesso!')
        with col2:
            st.header('Adiq', divider='gray')
            
            # Obter o valor da coluna 'custo' e 'valor_custo'
            tipo_intercambio = config.loc[0, "tipo_intercambio"]
            taxa_link_pagamento_adiq = config.loc[0, "taxa_link_pagamento_adiq"]

            tipo_de_taxa = {
                'Intercâmbio Máximo': 'intercambio_maximo',
                'Intercâmbio Médio': 'intercambio_medio',
                'Intercâmbio Mediana': 'intercambio_mediano',
                'Percentil 60': 'Percentil_60',
                'Percentil 70': 'Percentil_70',
                'Percentil 75': 'Percentil_75',
                'Percentil 80': 'Percentil_80',
                'Percentil 90': 'Percentil_90'
            }

            # Determinar qual opção do botão de rádio deve estar marcada
            opcao_selecionada = st.selectbox("Selecione o Tipo de Taxa:", list(tipo_de_taxa.keys()), placeholder="Tipo de Taxa")

            # Obter o valor convertido do dicionário
            valor_convertido = tipo_de_taxa[opcao_selecionada]
            taxa_link_pagamento_adiq = st.number_input(f"Taxa link de Pagamento Adiq", value=taxa_link_pagamento_adiq)
                
            
            # Botão para atualizar os parâmetros no banco de dados
            if st.button("Salvar "):
                # Atualizar os valores no DataFrame
                config.loc[0, "tipo_intercambio"] = valor_convertido
                config.loc[0, "taxa_link_pagamento_adiq"] = taxa_link_pagamento_adiq
                
                # Atualizar os parâmetros no banco de dados
                fun.atualizar_dados_config(config)
                st.success('Parâmetros atualizados com sucesso!')
        

    else:
        st.warning('A liberação para alteração de parametros só pode ser feita mediante a senha correta')
    

if __name__ == '__main__':
    main()

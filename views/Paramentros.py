import streamlit as st
import controllers.controllerConfiguracoes as ControllerConfiguracoes
import controllers.controllerGlobal as controllerGlobal
import pandas as pd
import utils.conexaoBD as confDB


# Função principal
def paramentros():
        st.header('Parâmetros', divider='blue')
        
        config = confDB.carregar_dados_config()
        col1, col2 = st.columns([4, 2])

        with col1:
            st.header('Geral', divider='gray')
            coll1, coll2 = st.columns([1,2])
            with coll1:
                # Obter o valor da coluna 'custo' e 'valor_custo'
                custo = config.loc[0, "custo"]
                valor_custo = config.loc[0, "valor_custo"]
                

                # Determinar qual opção do botão de rádio deve estar marcada
                opcao_radio = st.toggle("Custo", custo)

                # Se o custo estiver marcado como "Sim", mostrar o campo para inserir o valor
                if opcao_radio == True:
                    valor_custo = st.number_input(f"Valor", value=valor_custo)

                # Botão para atualizar os parâmetros no banco de dados
                if st.button("Salvar",type='primary'):
                    # Atualizar os valores no DataFrame
                    config.loc[0, "custo"] = opcao_radio
                    config.loc[0, "valor_custo"] = valor_custo

                    # Atualizar os parâmetros no banco de dados
                    ControllerConfiguracoes.atualizar_dados_config(config)
                    st.success('Parâmetros atualizados com sucesso!')
            
            with coll2:
                check_antec_automatico = config.loc[0, "antec_automatica"]
                valor_antec_automatico = config.loc[0, "valor_antec_automatica"]
                check_antec_manual = config.loc[0, "antec_manual"]
                valor_antec_manual = config.loc[0, "valor_antec_manual"]
                
                
                st.write('Antecipação')
                
                opcao_check_antecipacao = st.toggle("Automatico", check_antec_automatico,key='op_check_01')
                valor_antecipacao = st.number_input(f"Valor", value=valor_antec_automatico,key='vl_check_01')
            
            
                opcao_check_manual = st.toggle("Manual", check_antec_manual,key='op_check_02')
                valor_manual = st.number_input(f"Valor", value=valor_antec_manual,key='vl_check_02')
        
                if st.button("Salvar ",type='primary', key='Salvar_antecipacao'):
                    # Atualizar os valores no DataFrame
                    config.loc[0, "antec_automatica"] = opcao_check_antecipacao
                    config.loc[0, "valor_antec_automatica"] = valor_antecipacao
                    config.loc[0, "antec_manual"] = opcao_check_manual
                    config.loc[0, "valor_antec_manual"] = valor_manual

                    # Atualizar os parâmetros no banco de dados
                    ControllerConfiguracoes.atualizar_dados_config(config)
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

            # Determinar a chave que corresponde ao valor salvo no banco de dados
            chave_selecionada = next((chave for chave, valor in tipo_de_taxa.items() if valor == tipo_intercambio), None)

            # Determinar o índice da chave na lista de opções
            if chave_selecionada is not None:
                indice_selecionado = list(tipo_de_taxa.keys()).index(chave_selecionada)
            else:
                indice_selecionado = 0

            # Determinar qual opção do botão de rádio deve estar marcada
            opcao_selecionada = st.selectbox("Selecione o Tipo de Taxa:", list(tipo_de_taxa.keys()), index=indice_selecionado)

            # Obter o valor convertido do dicionário
            valor_convertido = tipo_de_taxa[opcao_selecionada]
            taxa_link_pagamento_adiq = st.number_input(f"Taxa link de Pagamento Adiq", value=taxa_link_pagamento_adiq)

            # Botão para atualizar os parâmetros no banco de dados
            if st.button("Salvar ",type='primary'):
                # Atualizar os valores no DataFrame
                config.loc[0, "tipo_intercambio"] = valor_convertido
                config.loc[0, "taxa_link_pagamento_adiq"] = taxa_link_pagamento_adiq

                # Atualizar os parâmetros no banco de dados
                ControllerConfiguracoes.atualizar_dados_config(config)
                st.success('Parâmetros atualizados com sucesso!')


def Parametros_spreed_comercial():
    st.header('Parâmetros', divider='blue')
    config = confDB.carregar_dados_config()
    # Carregar dados
    spreads_comercial = confDB.carregar_dados_spread_comercial()
    bandeiras_df = controllerGlobal.carregar_urls_das_bandeiras()
    bandeiras = spreads_comercial['bandeira'].unique()
    parcelamentos = spreads_comercial['parcelamento'].unique()
    spreads = {}

    ordem_desejada_bandeira = ['MASTERCARD', 'VISA', 'ELO', 'HIPERCARD', 'AMEX']
    ordem_desejada_parcelamento = ['DÉBITO', 'CRÉDITO', '2X a 6X', '7X a 12X', '13X a 18X']
    bandeiras = [p for p in ordem_desejada_bandeira if p in bandeiras]
    parcelamentos = [p for p in ordem_desejada_parcelamento if p in parcelamentos]


    cols = st.columns(5)
    col_idx = 0

    for bandeira in bandeiras:
        with cols[col_idx % 5]:
            url_imagem = bandeiras_df[bandeiras_df['BANDEIRA'] == bandeira]['URL_IMAGEM'].iloc[0]
            st.markdown(f'''
            <div style="text-align: center; margin: 10px;">
                <img src="{url_imagem}" alt="{bandeira}" style="width:80px; height:60px; display: block; margin: 0 auto;">
            </div>
            ''', unsafe_allow_html=True)
            
            for parcelamento in parcelamentos:
                # Pular os inputs de HIPERCARD DÉBITO e AMEX DÉBITO
                if (bandeira == 'HIPERCARD' and parcelamento == 'DÉBITO') or (bandeira == 'AMEX' and parcelamento == 'DÉBITO'):
                    continue
                spread_key = f"{bandeira}_{parcelamento}_spread"
                valor_spread = spreads_comercial.loc[
                 (spreads_comercial['bandeira'] == bandeira) & (spreads_comercial['parcelamento'] == parcelamento), 'spread'].item()
                spreads[spread_key] = st.number_input(parcelamento, min_value=0.0, key=spread_key, value=valor_spread)
        col_idx += 1
    valor_db_desconto = config.loc[0, "desconto"]
    desconto = st.number_input(f"Margem de Desconto", value=valor_db_desconto, min_value=0.0, key='vl_margem_desconto')
    config.loc[0, "desconto"] = desconto

    if st.button("Salvar", key='Salvar_spreads',type='primary'):
        # Converter o dicionário spreads para DataFrame
        df_spreads = pd.DataFrame([
            {'parcelamento': key.split('_')[1], 'bandeira': key.split('_')[0], 'spread': value}
            for key, value in spreads.items()
        ])

        # Concatenar com os dados existentes
        spreads_comercial = pd.concat([spreads_comercial, df_spreads], ignore_index=True)

        # Remover duplicatas mantendo o último valor
        spreads_comercial.drop_duplicates(subset=['parcelamento', 'bandeira'], keep='last', inplace=True)

        # Salvar no banco de dados
        ControllerConfiguracoes.salvar_dados_spreed_comercial(spreads_comercial)
        ControllerConfiguracoes.atualizar_dados_config(config)

        st.success("Parâmetros Aplicados com Sucesso!")


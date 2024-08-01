import streamlit as st
import utils.conexaoBD as confBD
import controllers.controllerSimulador as controllerSimulador
import controllers.controllerGlobal as controllerGlobal
import controllers.controllerProposta as controllerProposta
from datetime import date
import re
from datetime import date

def simulador_comercial():
    st.header('Simulador de Taxas', divider='blue')
    dados_do_banco_de_dados = confBD.carregar_dados_getnet()
    dados_mcc = confBD.carregar_dados_mcc()
    config = confBD.carregar_dados_config()

    col1, col2 = st.columns([1,2])

    adiquirente_selecionado = 'Getnet'
    tipo_taxa = 'SEM ANTECIPAÇÃO'
    
    with col1:
        mcc_selecionado = st.selectbox("Selecione o MCC:", dados_mcc['mcc'].unique(), placeholder="MCC")
    with col2:
        col1, col2 = st.columns([1, 1])
        with col1:
            check_antecipacao_automatica = st.checkbox("Antecipação Automática", config.loc[0, "antec_automatica"], key="checkbox_automatica")
            if check_antecipacao_automatica:
                antecipacao_automatica = st.number_input(f"Taxa:", min_value=config.loc[0, "valor_antec_automatica"], key="antecipacao_automatica")
            else:
                antecipacao_automatica = None
        with col2:
            check_antecipacao_manual = st.checkbox("Antecipação Manual", config.loc[0, "antec_manual"], key="checkbox_manual")
            if check_antecipacao_manual:
                antecipacao_manual = st.number_input(f"Taxa:", min_value=config.loc[0, "valor_antec_manual"], key="antecipacao_manual")
            else:
                antecipacao_manual = None
    
        
    antecipacao = [check_antecipacao_automatica, antecipacao_automatica, check_antecipacao_manual, antecipacao_manual]
    descricao_mcc = dados_mcc[dados_mcc['mcc'] == mcc_selecionado]['descricao_mcc'].iloc[0]
    st.write("<b><b/>", descricao_mcc, unsafe_allow_html=True)

    spreads = {}
    bandeiras_df = controllerGlobal.carregar_urls_das_bandeiras()
    bandeiras = dados_do_banco_de_dados['Bandeira'].unique()
    parcelamentos = dados_do_banco_de_dados['Parcelamento'].unique()
      
    controllerGlobal.exibir_bandeiras_com_inputs_executivos(bandeiras, parcelamentos, bandeiras_df, spreads)
    # Calcular as taxas finais
    taxas_finais = controllerSimulador.calcular_taxas_executivos(mcc_selecionado, adiquirente_selecionado, spreads, dados_do_banco_de_dados, tipo_taxa,antecipacao)
   
    # Exibir as taxas finais formatadas em uma tabela HTML
    st.markdown(taxas_finais.to_html(escape=False), unsafe_allow_html=True)
    
    @st.experimental_dialog("Salvar Proposta")
    def modal_controller():
        controllerProposta.salvar(antecipacao, mcc_selecionado, taxas_finais)
    
    if st.button('Gerar Proposta',type='primary', key='simulador_executivos'):
        modal_controller()
        
        

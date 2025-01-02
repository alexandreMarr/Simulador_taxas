import streamlit as st
from controllers import controllerProposta
import utils.conexaoBD as confBD
import controllers.controllerSimulador as controllerSimulador
import controllers.controllerGlobal as controllerGlobal

def simulador():
    st.header('Simulador de Taxas', divider='blue')
    config = confBD.carregar_dados_config()
    dados_mcc = confBD.carregar_dados_mcc()
    desconto = False
    # Dicionário com links de imagens das adquirentes
    data = {
        'Adiq': 'https://i.ibb.co/0XnDtz7/adiq.png',
        'Getnet': 'https://i.ibb.co/CztNnM8/getnet.png'
    }

    # Dividir a tela em duas colunas
    link = False
    col1, col2, col3, col4 = st.columns([1.5,1.2, 3,3])

    # Primeira coluna para o selectbox da adquirente
    with col1:
        adiquirente_selecionado = st.selectbox("Adiquirente:", list(data.keys()), key="adiquirente_selectbox")
        if adiquirente_selecionado:
            st.image(data[adiquirente_selecionado], width=100)

    # Segunda coluna para exibir a imagem da adquirente selecionada
    with col2:
        mcc_selecionado = st.selectbox("Selecione o MCC:", dados_mcc['mcc'].unique(), placeholder="MCC", key="mcc_selectbox")
        
    with col3:    
        st.write('Antecipação:')
        col1, col2 = st.columns([1, 1])
        with col1:
            check_antecipacao_automatica = st.checkbox("Automática", config.loc[0, "antec_automatica"], key="checkbox_automatica_s1")
            if check_antecipacao_automatica:
                antecipacao_automatica = st.number_input(f"Taxa:", min_value=config.loc[0, "valor_antec_automatica"], key="antecipacao_automatica_s1")
            else:
                antecipacao_automatica = None
        with col2:
            check_antecipacao_manual = st.checkbox("Manual", config.loc[0, "antec_manual"], key="checkbox_manual_s1")
            if check_antecipacao_manual:
                antecipacao_manual = st.number_input(f"Taxa:", min_value=config.loc[0, "valor_antec_manual"], key="antecipacao_manual_s1")
            else:
                antecipacao_manual = None
    antecipacao = [check_antecipacao_automatica, antecipacao_automatica, check_antecipacao_manual, antecipacao_manual]

    # Carregar dados MCC

    with col4:
        col1, col2 = st.columns([2, 0.5])
        with col1:
            # Carregar dados do banco de dados conforme adquirente selecionada
            if adiquirente_selecionado == 'Adiq':
                st.write('Link de Pagamento:')
                dados_do_banco_de_dados = confBD.carregar_dados_adiq()
                print(dados_do_banco_de_dados)
                tipo_taxa = ''
                st.write()
                link = st.checkbox("Ativo", False, key="link_pagamento_checkbox")
            else:
                dados_do_banco_de_dados = confBD.carregar_dados_getnet()
                tipo_taxa = st.selectbox("Selecione o Tipo de Taxa:", dados_do_banco_de_dados['tipo_taxa'].unique(), placeholder="Tipo de Taxa", key="tipo_taxa_selectbox")
            

    # Obter a descrição correspondente ao MCC selecionado
    descricao_mcc = dados_mcc[dados_mcc['mcc'] == mcc_selecionado]['descricao_mcc'].iloc[0]
    st.write("<b><b/>", descricao_mcc, unsafe_allow_html=True)

    # Dicionário para armazenar os spreads inseridos pelo usuário
    spreads = {}

    # Colunas para entrada de spreads
    col1, col2 = st.columns(2)
    with col1:
        spreads['DÉBITO'] = st.number_input(f"Digite o spread para DÉBITO:", min_value=0.0, key="debito_spread")
        spreads['2X a 6X'] = st.number_input(f"Digite o spread para 2x a 6x:", min_value=0.0, key="2x_6x_spread")

    with col2:
        spreads['CRÉDITO'] = st.number_input(f"Digite o spread para CRÉDITO:", min_value=0.0, key="credito_spread")
        spreads['7X a 12X'] = st.number_input(f"Digite o spread para 7x a 12x:", min_value=0.0, key="7x_12x_spread")

    if (dados_do_banco_de_dados['Parcelamento'] == '13X a 21X').any():
        with col1:
            spreads['13X a 21X'] = st.number_input(f"Digite o spread para 13x a 21x:", min_value=0.0, key="13x_21x_spread")
        with col2:
            spreads['22X a 24X'] = st.number_input(f"Digite o spread para 22x a 24x:", min_value=0.0, key="22x_24x_spread")
    parcelamentos = dados_do_banco_de_dados['Parcelamento'].unique()
    # Obtenha os parcelamentos selecionados
    parcelamentos_selecionados = [parcelamento for parcelamento, selecionado in controllerGlobal.exibir_checkboxes_parcelamentos(parcelamentos, unique_id="simulador_1").items() if selecionado]

    # Calcular as taxas finais
    taxas_finais = controllerSimulador.calcular_taxas(
        mcc_selecionado, adiquirente_selecionado, spreads, 
        dados_do_banco_de_dados, tipo_taxa, link, antecipacao, 
        parcelamentos_selecionados
    )

    # Exibir as taxas finais formatadas
    st.markdown(taxas_finais.to_html(escape=False), unsafe_allow_html=True)
    st.write()
    @st.experimental_dialog("Salvar Proposta")
    def modal_controller():
        controllerProposta.salvar(antecipacao, mcc_selecionado, taxas_finais, desconto)
    
    st.write(" ")
    
    if st.button('Gerar Proposta',type='primary',key='simulador'):
        modal_controller()

    if tipo_taxa == "SEM ANTECIPAÇÃO" and "13X a 21X" in parcelamentos_selecionados:
        st.warning("#-Aceitamos a bandeira HiperCard com opção de parcelamento em até 20x no crédito.")



def simulador_Avançado():
    st.header('Simulador de Taxas Avançado', divider='blue')
    config = confBD.carregar_dados_config()
    dados_mcc = confBD.carregar_dados_mcc()
    desconto = False
    # Dicionário com links de imagens das adquirentes
    data = {
        'Adiq': 'https://i.ibb.co/0XnDtz7/adiq.png',
        'Getnet': 'https://i.ibb.co/CztNnM8/getnet.png'
    }

    # Dividir a tela em duas colunas
    link = False
    col1, col2, col3, col4 = st.columns([1.5,1.2, 3,3])

    # Primeira coluna para o selectbox da adquirente
    with col1:
        adiquirente_selecionado = st.selectbox("Adiquirente:", list(data.keys()), key="adiquirente_selectbox_s2")
        if adiquirente_selecionado:
            st.image(data[adiquirente_selecionado], width=100)

    # Segunda coluna para exibir a imagem da adquirente selecionada
    with col2:
        mcc_selecionado = st.selectbox("Selecione o MCC:", dados_mcc['mcc'].unique(), placeholder="MCC", key="mcc_selectbox_s2")
        
    with col3:    
        st.write('Antecipação:')
        col1, col2 = st.columns([1, 1])
        with col1:
            check_antecipacao_automatica = st.checkbox("Automática", config.loc[0, "antec_automatica"], key="checkbox_automatica_s2")
            if check_antecipacao_automatica:
                antecipacao_automatica = st.number_input(f"Taxa:", min_value=config.loc[0, "valor_antec_automatica"], key="antecipacao_automatica_s2")
            else:
                antecipacao_automatica = None
        with col2:
            check_antecipacao_manual = st.checkbox("Manual", config.loc[0, "antec_manual"], key="checkbox_manual_s2")
            if check_antecipacao_manual:
                antecipacao_manual = st.number_input(f"Taxa:", min_value=config.loc[0, "valor_antec_manual"], key="antecipacao_manual_s2")
            else:
                antecipacao_manual = None
    antecipacao = [check_antecipacao_automatica, antecipacao_automatica, check_antecipacao_manual, antecipacao_manual]

    # Carregar dados MCC

    with col4:
        col1, col2 = st.columns([2, 0.5])
        with col1:
            # Carregar dados do banco de dados conforme adquirente selecionada
            if adiquirente_selecionado == 'Adiq':
                st.write('Link de Pagamento:')
                dados_do_banco_de_dados = confBD.carregar_dados_adiq()
                tipo_taxa = ''
                st.write()
                link = st.checkbox("Ativo", False, key="link_pagamento_checkbox_s2")
            else:
                dados_do_banco_de_dados = confBD.carregar_dados_getnet()
                tipo_taxa = st.selectbox("Selecione o Tipo de Taxa:", dados_do_banco_de_dados['tipo_taxa'].unique(), placeholder="Tipo de Taxa", key="tipo_taxa_selectbox_s2")
    

    descricao_mcc = dados_mcc[dados_mcc['mcc'] == mcc_selecionado]['descricao_mcc'].iloc[0]
    st.write("<b><b/>", descricao_mcc, unsafe_allow_html=True)

    spreads = {}
    bandeiras_df = controllerGlobal.carregar_urls_das_bandeiras()
    bandeiras = dados_do_banco_de_dados['Bandeira'].unique()
    parcelamentos = dados_do_banco_de_dados['Parcelamento'].unique()
    
     # Exibir checkboxes para cada parcelamento
    checkboxes = controllerGlobal.exibir_checkboxes_parcelamentos(parcelamentos,unique_id="simulador_avançado")

    # Filtrar parcelamentos baseados nos checkboxes selecionados
    parcelamentos_selecionados = [p for p in parcelamentos if checkboxes[p]]
    
    if parcelamentos_selecionados:
        controllerGlobal.exibir_bandeiras_com_inputs(bandeiras, parcelamentos_selecionados, bandeiras_df, spreads)

        taxas_finais = controllerSimulador.calcular_taxas_avançado(mcc_selecionado, adiquirente_selecionado, spreads, dados_do_banco_de_dados, tipo_taxa, link,antecipacao,parcelamentos_selecionados)

        st.markdown(taxas_finais.to_html(escape=False), unsafe_allow_html=True)
        
        @st.experimental_dialog("Salvar Proposta")
        def modal_controller():
            controllerProposta.salvar(antecipacao, mcc_selecionado, taxas_finais,desconto)
        
        st.write(" ")
        if st.button('Gerar Proposta',type='primary', key='simulador_avançados'):
            modal_controller()
        
    else:
        st.warning("Nenhum parcelamento selecionado.") 
    
    if tipo_taxa == "SEM ANTECIPAÇÃO" and "13X a 21X" in parcelamentos_selecionados:
        st.warning("#Aceitamos a bandeira HiperCard com opção de parcelamento em até 20x no crédito.")
 

   

    
       

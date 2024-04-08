import streamlit as st
import function as fun

# Configuração da página
fun.config("","Simulador de Taxas OverPrice")
st.title("")
st.header('Simulador de Taxas OverPrice', divider='green')

def main():
    data = {
        'Adiq': 'https://i.ibb.co/0XnDtz7/adiq.png'
        # 'Getnet': 'https://i.ibb.co/CztNnM8/getnet.png' não existe overprice para a getnet por enquanto
    }

    # Dividir a tela em duas colunas
    col1, col2 = st.columns([1, 1])

    # Primeira coluna para o selectbox
    with col1:
        adiquirente_selecionado = st.selectbox("Adiquirente:", list(data.keys()))

    # Segunda coluna para a imagem
    with col2:
        if adiquirente_selecionado:
            " "
            " "
            st.image(data[adiquirente_selecionado], width=100) 
    
    # Carregar dados do banco de dados
    if adiquirente_selecionado == 'Adiq':
        dados_do_banco_de_dados = fun.carregar_dados_adiq_overprice()
        tipo_taxa = ''
    else: 
        dados_do_banco_de_dados = fun.carregar_dados_getnet()
        tipo_taxa = st.selectbox("Selecione o Tipo de Taxa:", dados_do_banco_de_dados['tipo_taxa'].unique(), placeholder="Tipo de Taxa")
        
    # Selecionar MCC
    mcc_selecionado = st.selectbox("Selecione o MCC:", dados_do_banco_de_dados['mcc'].unique(), placeholder="MCC")
    
    # Obter a descrição correspondente ao MCC selecionado
    descricao_mcc = dados_do_banco_de_dados[dados_do_banco_de_dados['mcc'] == mcc_selecionado]['descricao_mcc'].iloc[0]
    st.write("<b><b/>", descricao_mcc, unsafe_allow_html=True)

    # Definir os spreads
    spreads = {}
    col1, col2 = st.columns(2)
    with col1:
        spreads['DÉBITO'] = st.number_input(f"Digite o spread para DÉBITO:", min_value=0.0) 
        spreads['2X a 6X'] = st.number_input(f"Digite o spread para 2x a 6x:", min_value=0.0) 

    with col2:
        spreads['CRÉDITO'] = st.number_input(f"Digite o spread para CRÉDITO:", min_value=0.0) 
        spreads['7X a 12X'] = st.number_input(f"Digite o spread para 7x a 12x:", min_value=0.0) 
    
    # Calcular as taxas finais
    taxas_finais = fun.calcular_taxas(mcc_selecionado, adiquirente_selecionado, spreads, dados_do_banco_de_dados, tipo_taxa)
    st.markdown(taxas_finais.to_html(escape=False), unsafe_allow_html=True)
    
if __name__ == "__main__":
    main()

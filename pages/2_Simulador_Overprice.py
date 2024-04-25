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
    link = False
    col1, col2, col3 = st.columns([3, 2, 5])

    # Primeira coluna para o selectbox da adquirente
    with col1:
        adiquirente_selecionado = st.selectbox("Adiquirente:", list(data.keys()))
           

    # Segunda coluna para exibir a imagem da adquirente selecionada
    with col2:
        if adiquirente_selecionado:
            " "
            " "
            st.image(data[adiquirente_selecionado], width=100) 
    
    # Carregar dados MCC
    dados_mcc = fun.carregar_dados_mcc()
    
    with col3:
        col1, col2 = st.columns([1,1])
        with col1:    
            # Carregar dados do banco de dados conforme adquirente selecionada
            if adiquirente_selecionado == 'Adiq':
                dados_do_banco_de_dados = fun.carregar_dados_adiq_overprice()
                tipo_taxa = ''
                st.write()
                link = st.toggle("Link de Pagamento",False)
                    
            else: 
                dados_do_banco_de_dados = fun.carregar_dados_getnet()
                tipo_taxa = st.selectbox("Selecione o Tipo de Taxa:", dados_do_banco_de_dados['tipo_taxa'].unique(), placeholder="Tipo de Taxa")
                
        with col2:
            # Selecionar MCC
            mcc_selecionado = st.selectbox("Selecione o MCC:", dados_do_banco_de_dados['mcc'].unique(), placeholder="MCC")
    
    # Obter a descrição correspondente ao MCC selecionado
    descricao_mcc = dados_mcc[dados_mcc['mcc'] == mcc_selecionado]['descricao_mcc'].iloc[0]
    st.write("<b><b/>", descricao_mcc, unsafe_allow_html=True)

    # Dicionário para armazenar os spreads inseridos pelo usuário
    spreads = {}
    
    # Colunas para entrada de spreads
    col1, col2 = st.columns(2)
    with col1:
        spreads['DÉBITO'] = st.number_input(f"Digite o spread para DÉBITO:", min_value=0.0) 
        spreads['2X a 6X'] = st.number_input(f"Digite o spread para 2x a 6x:", min_value=0.0) 

    with col2:
        spreads['CRÉDITO'] = st.number_input(f"Digite o spread para CRÉDITO:", min_value=0.0) 
        spreads['7X a 12X'] = st.number_input(f"Digite o spread para 7x a 12x:", min_value=0.0) 
    
    if (dados_do_banco_de_dados['Parcelamento'] == '13X a 18X').any():
        with col2:
            spreads['13X a 18X'] = st.number_input(f"Digite o spread para 13x a 18x:", min_value=0.0) 
    
    # Calcular as taxas finais
    taxas_finais = fun.calcular_taxas(mcc_selecionado, adiquirente_selecionado, spreads, dados_do_banco_de_dados, tipo_taxa,link)

    # Exibir as taxas finais formatadas em uma tabela HTML
    st.markdown(taxas_finais.to_html(escape=False), unsafe_allow_html=True)

    
if __name__ == "__main__":
    main()

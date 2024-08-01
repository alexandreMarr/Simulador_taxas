import streamlit as st
import controllers.controllerGlobal as ControllerGlobal
import streamlit.components.v1 as components
import utils.sidebar as men
import utils.auth as at
import utils.main as main
import controllers.controllerUpdate as ControllerUpdate
import utils.conexaoBD as confDB

# Função principal
def update():
   
        st.header('Atualizar Base', divider='blue')

        adiquirente = st.selectbox("Selecione a base para atualizar:", ['adiq', 'getnet'], placeholder="adiquirente")
        if adiquirente == 'adiq':
            arquivo_excel = st.file_uploader('Selecione o arquivo Excel', type=['xlsx'])

            # Carrega o arquivo do servidor
            with open('modelo_intercambio_facilitador.xlsx', 'rb') as file:
                arquivo_bytes = file.read()

            # Adiciona um botão para download na interface do Streamlit
            st.download_button(
                label="Baixar Arquivo Modelo",
                data=arquivo_bytes,
                file_name='modelo_intercambio_facilitador.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

            components.html(
                """
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">
                <div class="card" style="width: 50rem;">
                    <div class="card-body">
                        <h2 class="card-title">!!!atenção!!!</h3>
                        <h3 class="card-subtitle mb-2 text-muted">Requisitos Para Atualização</h6>
                        <ol class="card-text">
                            <li>Utilize o arquivo layout fornecido para download no botão acima para atualizar a base de dados.</li>
                            <li>Copie as informações do arquivo original para o modelo sem formatação, apenas texto.</li>
                            <li>Copie a coluna "Intercambio Mediana" do arquivo original e cole-a em um bloco de notas.</li>
                            <li>Copie as taxas do bloco de notas e cole-as no arquivo de layout, mantendo apenas o texto.</li>
                            <li>É importante que as taxas fiquem com duas casas decimais no layout modelo. EX "2,36%".</li>
                            <li>Não deixe as células da coluna "Intercambio Mediana" com mais de duas casas decimais. EX "2,4567553"</li>
                            <li>Salve o arquivo de layout e importe-o usando o botão acima.</li>
                            <li>Aguarde o processamento. Ao final, um relatório será gerado com o total de taxas atualizadas e adicionadas.</li>
                        </ol>
                        <p class="card-text">Pronto, sua base está atualizada!</p>
                    </div>
                </div>
                """, scrolling=True, height=330
            )

            if arquivo_excel is not None:
                # Leitura do arquivo Excel e atualização da tabela principal
                relatorio = ControllerUpdate.atualizar_tabela_principal(arquivo_excel)
                # Exibir relatório de análise
                st.write('**Relatório de Análise:**')
                st.write(relatorio)
        else:
            dados_do_banco_de_dados = confDB.carregar_dados_getnet()
            base = st.selectbox("Selecione a base para atualizar:", dados_do_banco_de_dados['tipo_taxa'].unique(), placeholder="Tipo de Taxa")
            arquivo_excel = st.file_uploader('Selecione o arquivo Excel', type=['xlsx'])

            if base == 'SEM ANTECIPAÇÃO':
                tabela = 'mdr_getnet_sem_antencipacao_up'
            elif base == 'COM ANTECIPAÇÃO':
                tabela = 'mdr_getnet_com_antencipacao_up'
            elif base == 'LINK DE PAGAMENTO':
                tabela = 'mdr_getnet_link_de_pagamento_up'

            if arquivo_excel is not None:
                # Leitura do arquivo Excel e extração dos dados
                dados_extraidos = ControllerUpdate.ler_arquivo(arquivo_excel)
                # Salvar os dados no banco de dados PostgreSQL
                result = ControllerUpdate.salvar_no_banco_de_dados(dados_extraidos, tabela)
                st.success('Os dados foram salvos no banco de dados com sucesso!')
                st.write(result)
    
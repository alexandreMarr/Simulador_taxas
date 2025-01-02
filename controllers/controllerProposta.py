import os
from tkinter.ttk import Frame
import pandas as pd
import streamlit as st
import utils.conexaoBD as confBD
from sqlalchemy.orm import sessionmaker
import controllers.controllerGlobal as ControllerGlobal
from sqlalchemy import Text, create_engine, Table as SQLTable, Column, Integer, String, Float, DateTime, MetaData, ForeignKey, Boolean
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
import io
from PyPDF2 import PdfReader, PdfWriter
import random
import re
import tkinter.font as TkFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from dotenv import load_dotenv

def salvar(antecipacao, mcc_selecionado, taxas_finais, desconto):
            response = ""
            st.write(f"Digite os dados do Cliente")
            col1, col2 = st.columns([1, 1])
            
            with col1:
                razao_social = st.text_input("Razão Social")
            with col2:
                cnpj = st.text_input("CNPJ")
            
            with col1:
                aluguel = st.number_input("Aluguel de POS R$", min_value=0.0)
            with col2:
                pix = st.number_input("Taxa PIX %", min_value=0.0)
            
            with col1:
                data_atual = date.today()
                st.date_input("Data Geração", data_atual, disabled=True, format="DD/MM/YYYY")
            with col2:
                data_validade = st.date_input("Validade da Proposta",format="DD/MM/YYYY")
            
            max_chars = 250
            obs = st.text_area("Observações", max_chars=max_chars)
            
            if len(obs) > max_chars:
                st.warning(f"Atenção: O texto não pode exceder {max_chars} caracteres. Você digitou {len(obs)} caracteres.")
                obs = obs[:max_chars]

            def formatar_cnpj(cnpj):
                cnpj = re.sub(r'\D', '', cnpj)  # Remove caracteres não numéricos
                if len(cnpj) == 14:
                    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
                return cnpj
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Salvar", type='primary', key='Salvar_proposta_preechida'):
                    if not razao_social:
                        st.error("Razão Social é obrigatória")
                    elif not cnpj:
                        st.error("CNPJ é obrigatório")
                    else:
                        cnpj_formatado = formatar_cnpj(cnpj)
                        response = salvar_proposta(razao_social, cnpj_formatado, aluguel, pix, data_atual, data_validade, st.session_state['name'], antecipacao, mcc_selecionado, taxas_finais,col2,obs,desconto)
    
            if response == "":
                st.write()
            else:
                st.success(response)
           
def salvar_proposta(razao_social, cnpj, aluguel, pix, data_atual, data_validade, username, antecipacao, mcc, pivot_table_styler,col2,obs,desconto):
     # Conectar ao banco de dados
     engine = confBD.conectar_banco_de_dados_engine()
     Session = sessionmaker(bind=engine)
     session = Session()
   
     # Definir a tabela propostas
     metadata = MetaData()
     propostas = SQLTable('propostas', metadata,
                       Column('id', Integer, primary_key=True),
                       Column('razao_social', String),
                       Column('cnpj', String),
                       Column('taxa_antecipacao', String),
                       Column('tipo_taxa_antecipacao', String),
                       Column('taxa_pix', Float),
                       Column('taxa_aluguel', Float),
                       Column('data_geracao', String),
                       Column('data_vencimento', String),
                       Column('nome_executivo', String),
                       Column('observacao', Text),
                       Column('desconto', Boolean),
                       Column('mcc', Text))
   
     # Definir a tabela mdr_propostas
     mdr_propostas = SQLTable('mdr_propostas', metadata,
                           Column('id', Integer, primary_key=True),
                           Column('bandeira', String),
                           Column('tipo_parcelamento', String),
                           Column('mcc', String),
                           Column('taxa', Float),
                           Column('id_proposta', Integer, ForeignKey('propostas.id')))
   
     # Criar as tabelas se não existirem
     # metadata.create_all(engine)
   
     # Transformar Styler de volta em DataFrame
     pivot_table = pivot_table_styler.data
   
     # Carregar o DataFrame de bandeiras para mapear URLs de volta para os nomes das bandeiras
     bandeiras_df = pd.DataFrame({
         'BANDEIRA': ['MASTERCARD', 'VISA', 'ELO', 'HIPERCARD', 'AMEX'],
         'URL_IMAGEM': [
             f'{os.getenv("URL_SERVER_IMAGENS")}/master.png',
             f'{os.getenv("URL_SERVER_IMAGENS")}/visa.png',
             f'{os.getenv("URL_SERVER_IMAGENS")}/elo.png',
             f'{os.getenv("URL_SERVER_IMAGENS")}/hiper.png',
             f'{os.getenv("URL_SERVER_IMAGENS")}/amex.png'
         ]
     })
     # Substituir URLs de volta pelos nomes das bandeiras
     colunas_bandeiras = pivot_table.columns
     nome_bandeiras = {}
   
     for bandeira in colunas_bandeiras:
         if bandeira.startswith('<img src='):
             url_imagem = bandeira.split('"')[1]
             bandeira_nome = bandeiras_df[bandeiras_df['URL_IMAGEM'] == url_imagem]['BANDEIRA'].iloc[0]
             nome_bandeiras[bandeira] = bandeira_nome
   
     pivot_table.rename(columns=nome_bandeiras, inplace=True)
   
     def converter_para_float(valor):
         try:
             return float(valor.strip('%')) / 100.0
         except:
             return None
     # Determinar a antecipação
     check_antecipacao_automatica, antecipacao_automatica, check_antecipacao_manual, antecipacao_manual = antecipacao
     if check_antecipacao_automatica:
         taxa_antecipacao = antecipacao_automatica
         tipo_taxa_antecipacao = 'Automática'
     elif check_antecipacao_manual:
         taxa_antecipacao = antecipacao_manual
         tipo_taxa_antecipacao = 'Manual'
     else:
         taxa_antecipacao = 0.00
         tipo_taxa_antecipacao = 'Não Negociado'
   
     try:
         # Inserir os dados na tabela propostas
         nova_proposta = propostas.insert().values(
             razao_social=razao_social,
             cnpj=cnpj,
             taxa_antecipacao=taxa_antecipacao,
             tipo_taxa_antecipacao=tipo_taxa_antecipacao,
             taxa_pix=pix,
             taxa_aluguel=aluguel,
             data_geracao=data_atual,
             data_vencimento=data_validade,
             nome_executivo=username,
             observacao=obs,
             desconto=desconto,
             mcc=mcc
         )
       
         # Executar a inserção e obter o ID da nova proposta
         conn = engine.connect()
         result = conn.execute(nova_proposta)
         id_proposta = result.inserted_primary_key[0]
       
         for tipo_parcelamento in pivot_table.index:
             for bandeira in pivot_table.columns:
                 taxa_percentual = pivot_table.loc[tipo_parcelamento, bandeira]
                 taxa_float = converter_para_float(taxa_percentual)
                 taxa_float = taxa_float * 100
                 nova_mdr_proposta = mdr_propostas.insert().values(
                     bandeira=bandeira,
                     tipo_parcelamento=tipo_parcelamento,
                     mcc=str(mcc),
                     taxa=taxa_float,
                     id_proposta=id_proposta
                 )
                 conn.execute(nova_mdr_proposta)
         # Confirmar as alterações
         conn.commit()
   
   
     except Exception as e:
         print(f"Erro ao salvar proposta: {e}")
         conn.rollback()
   
     finally:
         # Fechar a conexão
         conn.close()
         # Fechar a sessão
         session.close()
   
     dados_cliente = {
             'razao_social': razao_social,
             'cnpj': cnpj,
             'data_geracao': data_atual.strftime('%d/%m/%Y'),
             'data_validade': data_validade.strftime('%d/%m/%Y')
         }
     taxas = {
         'aluguel': aluguel,
         'pix': pix,
         'taxa_antecipacao': taxa_antecipacao,
         'tipo_taxa_antecipacao': tipo_taxa_antecipacao
     }

   # Gere o PDF e obtenha o buffer
     pdf_buffer = gerar_pdf(dados_cliente, taxas, pivot_table,username,obs,desconto,mcc)
    
     with col2:
        # Exiba o PDF no Streamlit
        st.download_button(
            label="Baixar PDF",
            data=pdf_buffer.getvalue(),
            file_name=f"{re.sub(r'[^a-zA-Z0-9\s]', '', razao_social).strip()}_{random.randint(0, 100)}.pdf",
            mime="application/pdf"
        )
   
     return 'Proposta Salva'

from reportlab.platypus import Paragraph, Frame, Table, TableStyle, Image as ReportLabImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
import requests
import random
import re
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors


def gerar_pdf(dados_cliente, taxas, pivot_table, username,obs,desconto, mcc):
    # Carregar o papel timbrado
    papel_timbrado_path = 'Papel Timbrado - Rovema Bank.pdf'
    papel_timbrado = PdfReader(papel_timbrado_path)
    output_pdf = PdfWriter()

    # Cria um buffer para o PDF em memória
    buffer = BytesIO()

    # Define o documento usando ReportLab
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Estilos de texto
    pdfmetrics.registerFont(TTFont('OpenSans', 'fonts/OpenSans-VariableFont_wdth,wght.ttf'))

    # Adiciona informações no PDF
    c.setFont("OpenSans", 12)
    c.drawString(132, height - 161, username)
    c.drawString(117, height - 197.4, dados_cliente['razao_social'])
    c.drawString(108, height - 233, dados_cliente['cnpj'])
    aluguel_str = f"R$ {taxas['aluguel']:.2f}"
    c.drawString(390, height - 231, aluguel_str)
    c.drawString(426, height - 161, mcc)
    if obs:
        # Estilo para o parágrafo de observações
        styles = getSampleStyleSheet()
        style = styles['Normal']
        style.fontName = 'OpenSans'
        style.fontSize = 12
        style.leading = 14  # Espaçamento entre linhas
        style.alignment = 0  # Alinhamento à esquerda

        # Criar parágrafo
        p = Paragraph(obs, style)

        # Criar um frame para o parágrafo
        frame = Frame(80, height - 735, 458, 75, showBoundary=0)

        # Adicionar parágrafo ao frame
        frame.addFromList([p], c)

    # Taxa de antecipação
    if taxas['tipo_taxa_antecipacao'] == "Automática":
        c.drawString(75, height - 290, 'X')
        taxa_antecipacao = f"{taxas['taxa_antecipacao']}%"
        c.drawString(148.4, height - 268, taxa_antecipacao)
    elif taxas['tipo_taxa_antecipacao'] == "Manual":
        c.drawString(182, height - 292, 'X')
        taxa_antecipacao = f"{taxas['taxa_antecipacao']}%"
        c.drawString(148.4, height - 268, taxa_antecipacao)
    else:
        c.drawString(148.4, height - 268, "Não Negociado")

    if taxas['pix'] == 0.0:
        c.drawString(377, height - 292.5, 'X')
    else:
        c.drawString(312.5, height - 292.5, 'X')
        taxa_pix = f"{taxas['pix']:.2f}%"
        c.drawString(337, height - 268, taxa_pix)

    if desconto == True:
        c.setFillColor(colors.rgb2cmyk(255,0,0))
        c.drawString(155, height - 646, 'Desconto exclusivo válido até a data de vencimento da proposta.')
    
    
    
    c.setFillColor(colors.white)
    # Desenhar strings com a cor branca
    c.drawString(389, height - 103, dados_cliente['data_geracao'])
    c.drawString(389, height - 125, dados_cliente['data_validade'])
    # Fechar a página atual para adicionar a próxima
 

     # Mapear bandeiras para URLs de imagem
    bandeira_imagens = {
         'MASTERCARD': f'{os.getenv("URL_SERVER_IMAGENS")}/master.png',
            'VISA': f'{os.getenv("URL_SERVER_IMAGENS")}/visa.png',
            'ELO':   f'{os.getenv("URL_SERVER_IMAGENS")}/elo.png',
            'HIPERCARD':  f'{os.getenv("URL_SERVER_IMAGENS")}/hiper.png',
            'AMEX': f'{os.getenv("URL_SERVER_IMAGENS")}/amex.png'
    }
    
    # Preparar os dados da tabela sem adicionar o cabeçalho textual
    data = pivot_table.reset_index().values.tolist()

    # Inserir as imagens das bandeiras na primeira linha
    bandeira_imgs = [ReportLabImage(BytesIO(requests.get(bandeira_imagens[bandeira]).content), width=50, height=30) for bandeira in bandeira_imagens.keys()]
    data.insert(0, [''] + bandeira_imgs)
    # found = any("13X a 21X" in sublist for sublist in data)
    # if found:
    #     data[5][4] = f"* {data[5][4]}"  # Adiciona '*' na linha 3 (índice 3) e coluna 4 (índice 4)
   
    # Criar a tabela no PDF
    col_count = len(bandeira_imagens) + 1
    table = Table(data, colWidths=[16.8 * 28.35 / col_count] * col_count, hAlign='CENTER')
    
    # Verifica se o data contem o tipo de taxa 13x a 21x
    found = any("13X a 21X" in sublist for sublist in data)
    if found:
        table.setStyle(TableStyle([
            # Define a cor laranja para a taxa hipercard de 13x a 21x
            ('TEXTCOLOR', (4, 5), (4, 5), colors.HexColor('#ff914d')),  # Define a cor do texto como laranja
            ('FONTNAME', (4, 3), (4, 3), 'OpenSans'),
        ]))
        c.setFillColor(colors.HexColor('#ff914d'))
        c.drawString(55, height - 600, '# Aceitamos a bandeira HiperCard com opção de parcelamento em até 20x no crédito.')

    
    # Estilizar a tabela
    table.setStyle(TableStyle([
    # Define a cor de fundo da primeira linha (cabeçalho)
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E5EEFF')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, -1), 'OpenSans'),
    ('FONTSIZE', (0, 0), (-1, -1), 12),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
    
    # Define a borda externa da tabela
    ('GRID', (0, 0), (-1, -1), 2, colors.HexColor('#E5EEFF')),  # Adiciona borda ao redor de todas as células
    
    # Define a cor de fundo da primeira coluna
    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F1F1F1')),
    
    # Outras configurações
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    # Adicionar a tabela ao canvas
    table.wrapOn(c, width, height)
    table.drawOn(c, 60, height - 550)  # Posicione a tabela conforme necessário

    # Salvar e fechar a canvas
    c.save()
    c.showPage()

    # Adiciona o conteúdo ao papel timbrado
    buffer.seek(0)
    pdf_content = PdfReader(BytesIO(buffer.getvalue()))

    num_timbrado_pages = len(papel_timbrado.pages)
    num_content_pages = len(pdf_content.pages)

    for page in range(max(num_timbrado_pages, num_content_pages)):
        if page < num_timbrado_pages:
            timbrado_page = papel_timbrado.pages[page]
            if page < num_content_pages:
                content_page = pdf_content.pages[page]
                timbrado_page.merge_page(content_page)
            output_pdf.add_page(timbrado_page)
        elif page < num_content_pages:
            output_pdf.add_page(pdf_content.pages[page])

    # Save the PDF to the buffer
    final_buffer = BytesIO()
    output_pdf.write(final_buffer)
    final_buffer.seek(0)

    return final_buffer

def carregar_tabela(filtros, dataset, nivel, name):
    """
    Carrega a tabela de propostas com base nos filtros especificados.

    Args:
        filtros (dict): Dicionário contendo os filtros a serem aplicados.
        dataset (DataFrame): DataFrame contendo os dados das propostas.
        nivel (str): Nível do usuário, que define a visibilidade dos dados.
        name (str): Nome do executivo, usado para filtrar os dados se necessário.

    Returns:
        DataFrame: Tabela formatada com as propostas.
    """
    
    # Verifica se o nível é "user" e aplica o filtro por nome_executivo
    if nivel == "user":
        dataset = dataset[dataset['nome_executivo'] == name]

    # Aplica filtros no DataFrame conforme os filtros fornecidos
    if filtros['razao_social']:
        dataset = dataset[dataset['razao_social'].isin(filtros['razao_social'])]

    if filtros['cnpj']:
        dataset = dataset[dataset['cnpj'].isin(filtros['cnpj'])]

    if filtros['nome_executivo']:
        dataset = dataset[dataset['nome_executivo'].isin(filtros['nome_executivo'])]

    # Filtra por intervalo de datas de geração
    if filtros.get('data_inicio') and filtros.get('data_fim'):
        data_inicio_str = filtros['data_inicio'].strftime('%Y-%m-%d')
        data_fim_str = filtros['data_fim'].strftime('%Y-%m-%d')
        dataset = dataset[
            (dataset['data_geracao'] >= data_inicio_str) &
            (dataset['data_geracao'] <= data_fim_str)
        ]
    elif filtros.get('data_inicio'):  # Apenas data de início fornecida
        data_inicio_str = filtros['data_inicio'].strftime('%Y-%m-%d')
        dataset = dataset[dataset['data_geracao'] >= data_inicio_str]
    elif filtros.get('data_fim'):  # Apenas data de fim fornecida
        data_fim_str = filtros['data_fim'].strftime('%Y-%m-%d')
        dataset = dataset[dataset['data_geracao'] <= data_fim_str]


    dataset = dataset.reset_index(drop=True)

    # Formata as colunas de taxas
    dataset['taxa_pix'] = (
        dataset['taxa_pix']
        .astype(float)  # Converte para float
        .apply(lambda x: f"{x:.2f}%")  # Formata cada elemento como string
    )

    dataset['taxa_aluguel'] = (
        dataset['taxa_aluguel']
        .astype(float)  # Converte para float
        .apply(lambda x: f"R$ {x:.2f}")  # Formata cada elemento como string
    )
    
    # Novo nome das colunas
    novo_nome_colunas = {
        'id': 'ID',
        'razao_social': 'Razão Social',
        'cnpj': 'CNPJ',
        'taxa_antecipacao': 'Taxa de Antecipação',
        'tipo_taxa_antecipacao': 'Antecipação',
        'taxa_pix': 'Taxa Pix',
        'taxa_aluguel': 'Aluguel POS',
        'data_geracao': 'Data De Geração',
        'data_vencimento': 'Data de Validade',
        'nome_executivo': 'Executivo',
    }
    
    # Renomeia as colunas do DataFrame
    dataset = dataset.rename(columns=novo_nome_colunas)

    return dataset

def estilo_personalizado(dataframe):
    style = dataframe.style.set_table_styles(
        [
            # Estilo para o cabeçalho
            {
                'selector': 'th',
                'props': [
                    ('background-color', '#E5EEFF'),
                    ('color', 'black'),
                    ('font-family', 'OpenSans'),
                    ('font-size', '12px'),
                    ('text-align', 'center'),
                    ('padding', '12px 0px')
                ]
            },
            # Estilo para o índice
            {
                'selector': 'th.row_heading',
                'props': [
                    ('background-color', '#F1F1F1')
                ]
            },
            # Estilo para os dados
            {
                'selector': 'td',
                'props': [
                    ('background-color', 'white'),
                    ('color', 'black'),
                    ('font-family', 'OpenSans'),
                    ('font-size', '12px'),
                    ('text-align', 'center'),
                    ('vertical-align', 'middle'),
                    ('border', '2px solid #E5EEFF'),
                    ('padding', '12px 0px')
                ]
            },
            # Estilo para a grade da tabela
            {
                'selector': 'table',
                'props': [
                    ('border-collapse', 'collapse'),
                    ('width', '100%'),
                ]
            }
        ]
    )

    return style

def buscar_dados_pdf(id):
    dados_mdr_proposta = confBD.carregar_dados_mdr_propostas()
    dados_proposta = confBD.carregar_dados_propostas()
    

    try:
        # Filtrar a linha do DataFrame com o ID correspondente
        proposta = dados_proposta.loc[dados_proposta['id'] == id]
        mdr_proposta = dados_mdr_proposta.loc[dados_mdr_proposta['id_proposta'] == id]
        
        # Verificar se a proposta foi encontrada
        if not proposta.empty:
            # Criar a tabela pivô
            pivot_table = mdr_proposta.pivot_table(index='tipo_parcelamento', columns='bandeira', values='taxa', aggfunc='mean')
            pivot_table = ControllerGlobal.formatacao_pivot(pivot_table)
            pivot_table = pivot_table.data
            
            
             # Carregar o DataFrame de bandeiras para mapear URLs de volta para os nomes das bandeiras
            bandeiras_df = pd.DataFrame({
                'BANDEIRA': ['MASTERCARD', 'VISA', 'ELO', 'HIPERCARD','AMEX'],
                'URL_IMAGEM': [
                     f'{os.getenv("URL_SERVER_IMAGENS")}/master.png',
                     f'{os.getenv("URL_SERVER_IMAGENS")}/visa.png',
                     f'{os.getenv("URL_SERVER_IMAGENS")}/elo.png',
                     f'{os.getenv("URL_SERVER_IMAGENS")}/hiper.png',
                     f'{os.getenv("URL_SERVER_IMAGENS")}/amex.png'
            ]
            })
            # Substituir URLs de volta pelos nomes das bandeiras
            colunas_bandeiras = pivot_table.columns
            nome_bandeiras = {}
   
            for bandeira in colunas_bandeiras:
                if bandeira.startswith('<img src='):
                    url_imagem = bandeira.split('"')[1]
                    bandeira_nome = bandeiras_df[bandeiras_df['URL_IMAGEM'] == url_imagem]['BANDEIRA'].iloc[0]
                    nome_bandeiras[bandeira] = bandeira_nome
        
            pivot_table.rename(columns=nome_bandeiras, inplace=True)
            # Extrair os dados da proposta
            data_geracao_str = proposta.iloc[0]['data_geracao']
            # Converter para datetime
            data_geracao_date = pd.to_datetime(data_geracao_str)
            # Formatar para DD/MM/YYYY
            data_geracao_formatada = data_geracao_date.strftime('%d/%m/%Y')
            
            data_validade_str = proposta.iloc[0]['data_vencimento']
            # Converter para datetime
            data_validade_date = pd.to_datetime(data_validade_str)
            # Formatar para DD/MM/YYYY
            data_validade_formatada = data_validade_date.strftime('%d/%m/%Y')
            
            desconto = proposta.iloc[0]['desconto']
            # Extrair os dados da proposta
            dados_cliente = {
                'razao_social': proposta.iloc[0]['razao_social'],
                'cnpj': proposta.iloc[0]['cnpj'],
                'data_geracao': data_geracao_formatada,
                'data_validade': data_validade_formatada,
            }
            
            taxas = {
                'aluguel': proposta.iloc[0]['taxa_aluguel'],
                'pix': proposta.iloc[0]['taxa_pix'],
                'taxa_antecipacao': proposta.iloc[0]['taxa_antecipacao'],
                'tipo_taxa_antecipacao': proposta.iloc[0]['tipo_taxa_antecipacao'],
            }
            obs = proposta.iloc[0]['observacao']
            mcc = proposta.iloc[0]['mcc']
            
            # Gerar PDF com dados
            pdf_buffer = gerar_pdf(dados_cliente, taxas, pivot_table, proposta.iloc[0]['nome_executivo'], obs,desconto,mcc)
            
            return st.download_button(
                    label="Baixar PDF",
                    data=pdf_buffer.getvalue(),
                    file_name=f"Proposta_{id}.pdf",
                    mime="application/pdf",
                    type= 'primary'
                )
        else:
            print("Proposta não encontrada!")
            return 'Proposta não encontrada!'

    except KeyError as e:
        print(f"Erro de chave: {e}")
        return e
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        return e
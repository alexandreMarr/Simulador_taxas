import utils.conexaoBD as confBD
from sqlalchemy import create_engine, Table, Column, Integer, String, Float, MetaData
from sqlalchemy.orm import sessionmaker
import psycopg2 
from sqlalchemy import create_engine, inspect, text
from sqlalchemy import MetaData, Table, select, update

def atualizar_dados_config(config):
    """
    Atualiza os dados de configuração no banco de dados.

    Parâmetros:
        config (DataFrame): DataFrame contendo os dados de configuração a serem atualizados.

    Retorna:
        None
    """
    # Conectar ao banco de dados PostgreSQL
    engine = confBD.conectar_banco_de_dados()

    # Nome da tabela no banco de dados
    tabela = 'config'

    # Atualizar os dados no banco de dados PostgreSQL
    with engine.begin() as conn:
        # Atualizar os valores na tabela 'config'
        config.to_sql(name=tabela, con=engine, index=False, if_exists='replace')
        
        

def salvar_dados_spreed_comercial(df):
    engine = confBD.conectar_banco_de_dados()  # Certifique-se de que confBD.conectar_banco_de_dados() retorna uma URL de conexão válida do SQLAlchemy
    metadata = MetaData()

    # Refletir a tabela existente no banco de dados
    spreads_comercial_table = Table('spread_comercial', metadata, autoload_with=engine)

    # Criar sessão
    Session = sessionmaker(bind=engine)
    session = Session()

    # Iterar sobre o DataFrame e atualizar ou inserir registros
    for idx, row in df.iterrows():
        # Verificar se o registro existe
        stmt = spreads_comercial_table.select().where(
            (spreads_comercial_table.c.bandeira == row['bandeira']) &
            (spreads_comercial_table.c.parcelamento == row['parcelamento'])
        )
        registro_existente = session.execute(stmt).fetchone()

        if registro_existente:
            # Atualizar registro existente
            stmt = update(spreads_comercial_table).where(
                (spreads_comercial_table.c.bandeira == row['bandeira']) &
                (spreads_comercial_table.c.parcelamento == row['parcelamento'])
            ).values(spread=row['spread'])
        else:
            # Inserir novo registro
            stmt = spreads_comercial_table.insert().values(
                bandeira=row['bandeira'],
                parcelamento=row['parcelamento'],
                spread=row['spread']
            )

        # Executar o comando SQL
        session.execute(stmt)

    # Confirmar (commit) as mudanças e fechar a sessão
    session.commit()
    session.close()

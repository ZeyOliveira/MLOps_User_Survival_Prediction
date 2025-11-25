"""
Módulo responsável pela ingestão de dados.

Objetivo:
- Conectar ao banco de dados PostgreSQL.
- Extrair a tabela especificada como DataFrame pandas.
- Dividir os dados em treino e teste e salvar em CSVs.

Observações:
- Apenas adiciona comentários e docstrings para explicar o fluxo.
"""
import pandas as pd
import psycopg2
import os
import sys
from src.custom_exception import CustomException
from src.logger import get_logger
from config.paths_config import *
from sklearn.model_selection import train_test_split
from config.database_config import DB_CONFIG


# Logger configurado para registrar mensagens do módulo
logger = get_logger(__name__)


class DataIngestion:
    """
    Classe que encapsula o processo de ingestão de dados.

    Métodos:
    - connect_to_database: cria conexão com o banco PostgreSQL.
    - extract_data: executa query e retorna DataFrame.
    - save_data: divide em treino/teste e salva em disco.
    - run: orquestra todo o processo de ingestão.
    """

    def __init__(self, db_params, output_dir):
        """
        Inicializa o ingestor.

        Parâmetros:
        - db_params: dicionário com parâmetros de conexão (host, port, database, user, password).
        - output_dir: diretório onde os dados serão salvos.
        """
        self.db_params = db_params
        self.output_dir = output_dir

        # Garante que o diretório de saída exista
        os.makedirs(self.output_dir, exist_ok=True)


    def connect_to_database(self):
        """
        Tenta criar e retornar uma conexão psycopg2 com o banco.

        Retorno:
        - conn: objeto de conexão PostgreSQL.

        Lança CustomException em caso de erro na conexão.
        """
        try:
            conn = psycopg2.connect(
                host=self.db_params['host'],
                port=self.db_params['port'],
                database=self.db_params['database'],
                user=self.db_params['user'],
                password=self.db_params['password'],
            )
            # Registro para evidenciar que a conexão foi estabelecida
            logger.info("Database connection established.")
            return conn
        except Exception as e:
            # Erros de conexão são registrados e encapsulados em CustomException
            logger.error(f"Error while connecting to database. {e}")
            raise CustomException(str(e), sys)
        


    def extract_data(self):
        """
        Executa a consulta SQL para obter os dados e retorna um DataFrame.

        Observações:
        - A query atual seleciona tudo de 'public.titanic' (mantida conforme arquivo original).
        - Fecha a conexão após a extração.

        Lança CustomException em caso de erro na extração.
        """
        try:
            conn = self.connect_to_database()
            query = 'SELECT * FROM public.titanic;'
            # Utiliza pandas para executar a query e carregar o resultado em memória
            df = pd.read_sql_query(query, conn)
            conn.close()
            logger.info("Data extraction successful.")
            return df
        except Exception as e:
            logger.error(f"Error while extracting data. {e}")
            raise CustomException(str(e), sys)
        


    def save_data(self, df):
        """
        Recebe um DataFrame, divide em treino e teste e salva em CSV.

        - Usa train_test_split do scikit-learn com random_state fixo para reprodutibilidade.
        - Salva nos caminhos definidos em config.paths_config (TRAIN_PATH, TEST_PATH).

        Lança CustomException em caso de erro ao salvar.
        """
        try:
            train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)

            # Salva os arquivos sem índice para facilitar reuso posterior
            train_df.to_csv(TRAIN_PATH, index=False)
            test_df.to_csv(TEST_PATH, index=False)

            logger.info(f"Data saved successfully at {TRAIN_PATH} and {TEST_PATH}.")
            
        except Exception as e:
            logger.error(f"Error while saving data. {e}")
            raise CustomException(str(e), sys)


    def run(self):
        """
        Ponto de entrada para executar todo o pipeline de ingestão.

        Passos:
        1. Extrai os dados do banco.
        2. Salva dados de treino e teste no disco.

        Lança CustomException se qualquer etapa falhar.
        """
        try:
            logger.info("Starting data ingestion process.")
            df = self.extract_data()
            self.save_data(df)
            logger.info("Data ingestion process completed.")

        except Exception as e:
            logger.error(f"Data ingestion process failed. {e}")
            raise CustomException(str(e), sys)                                                                
    

if __name__ == "__main__":
    # Instancia e executa a ingestão quando o módulo é executado diretamente
    data_ingestion = DataIngestion(DB_CONFIG, RAW_DIR)
    data_ingestion.run()
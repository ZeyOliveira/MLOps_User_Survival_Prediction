"""
Script que orquestra o pipeline de treinamento completo.

Fluxo:
1. Ingestão dos dados do banco para arquivos brutos.
2. Processamento dos dados (pré-processamento, balanceamento, envio para feature store).
3. Treinamento do modelo usando features armazenadas no Redis.

Observação:
Este arquivo apenas executa as etapas em sequência. A lógica de cada etapa
está implementada nos módulos importados.
"""
from src.data_ingestion import DataIngestion
from src.data_processing import DataProcessing
from src.model_training import ModelTraining
from src.feature_store import RedisFeatureStore
from config.paths_config import *
from config.database_config import DB_CONFIG


if __name__=="__main__":
    # Etapa 1: ingestão de dados do banco e gravação em RAW_DIR
    data_ingestion = DataIngestion(DB_CONFIG , RAW_DIR)
    data_ingestion.run()

    # Etapa 2: inicializa feature store e executa processamento (gera TRAIN/TEST e popula Redis)
    feature_store = RedisFeatureStore()
    data_processor = DataProcessing(TRAIN_PATH,TEST_PATH,feature_store)
    data_processor.run()

    # Etapa 3: instancia feature store e executa o treinamento do modelo
    feature_store = RedisFeatureStore()
    model_trainer = ModelTraining(feature_store)
    model_trainer.run()
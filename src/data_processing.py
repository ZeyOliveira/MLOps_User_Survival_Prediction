"""
Módulo responsável pelo processamento e transformação de dados.

Responsabilidades:
- Carregar dados de treino e teste de arquivos CSV.
- Pré-processar dados (preenchimento de valores faltantes, encoding, feature engineering).
- Balancear dados desbalanceados usando SMOTE.
- Armazenar features em Redis.
- Recuperar features do Redis por entity_id.
"""
import pandas as pd
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
from src.feature_store import RedisFeatureStore
from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import *

# Logger para registrar eventos do módulo
logger = get_logger(__name__)


class DataProcessing:
    """
    Classe que orquestra o processamento completo dos dados do Titanic.

    Fluxo:
    1. Carrega dados de treino e teste.
    2. Pré-processa (preenchimento, encoding, feature engineering).
    3. Balanceia dados com SMOTE.
    4. Armazena features em Redis.
    """

    def __init__(self, train_data_path, test_data_path, feature_store: RedisFeatureStore):
        """
        Inicializa o processador de dados.

        Parâmetros:
        - train_data_path: caminho do CSV de treino.
        - test_data_path: caminho do CSV de teste.
        - feature_store: instância de RedisFeatureStore para persistência.
        """
        self.train_data_path = train_data_path
        self.test_data_path = test_data_path
        self.data = None
        self.test_data = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None

        self.X_resampled = None
        self.y_resampled = None

        self.feature_store = feature_store
        logger.info("Your Data Processing is intialized...")
    
    def load_data(self):
        """
        Carrega dados de treino e teste de arquivos CSV.

        - self.data: DataFrame com dados de treino.
        - self.test_data: DataFrame com dados de teste.

        Lança CustomException em caso de erro na leitura.
        """
        try:
            # Lê o arquivo de treino e armazena em self.data
            self.data = pd.read_csv(self.train_data_path)
            # Lê o arquivo de teste e armazena em self.test_data
            self.test_data = pd.read_csv(self.test_data_path)
            logger.info("Read the data sucesfully")
        except Exception as e:
            logger.error(f"Error while reading data {e}")
            raise CustomException(str(e))
    
    def preprocess_data(self):
        """
        Realiza pré-processamento dos dados.

        Etapas:
        1. Preenchimento de valores faltantes (Age, Embarked, Fare).
        2. Encoding de variáveis categóricas (Sex, Embarked).
        3. Feature engineering (Familysize, Isalone, HasCabin, Title, Pclass_Fare, Age_Fare).

        Lança CustomException em caso de erro.
        """
        try:
            # Preenchimento de valores faltantes com mediana (Age, Fare) ou moda (Embarked)
            self.data['Age'] = self.data['Age'].fillna(self.data['Age'].median())
            self.data['Embarked'] = self.data['Embarked'].fillna(self.data['Embarked'].mode()[0])
            self.data['Fare'] = self.data['Fare'].fillna(self.data['Fare'].median())
            
            # Conversão de Sex para numérico (male=0, female=1)
            self.data['Sex'] = self.data['Sex'].map({'male': 0, 'female': 1})
            # Conversão de Embarked para numérico (category codes)
            self.data['Embarked'] = self.data['Embarked'].astype('category').cat.codes

            # Engenharia de features: criação de novas variáveis
            # Tamanho da família (SibSp + Parch + próprio passageiro)
            self.data['Familysize'] = self.data['SibSp'] + self.data['Parch'] + 1

            # Indicador binário: passageiro viaja sozinho
            self.data['Isalone'] = (self.data['Familysize'] == 1).astype(int)

            # Indicador binário: passageiro possui informação de cabine
            self.data['HasCabin'] = self.data['Cabin'].notnull().astype(int)

            # Extração e mapeamento de títulos do nome (Mr, Miss, Mrs, Master, Rare)
            self.data['Title'] = self.data['Name'].str.extract(' ([A-Za-z]+)\.', expand=False).map(
                {'Mr': 0, 'Miss': 1, 'Mrs': 2, 'Master': 3, 'Rare': 4}
            ).fillna(4)

            # Interações entre features
            # Produto de classe de passagem e tarifa
            self.data['Pclass_Fare'] = self.data['Pclass'] * self.data['Fare']
            # Produto de idade e tarifa
            self.data['Age_Fare'] = self.data['Age'] * self.data['Fare']

            logger.info("Data Preprocessing done...")

        except Exception as e:
            logger.error(f"Error while preprocessing data {e}")
            raise CustomException(str(e))
    
    def handle_imbalance_data(self):
        """
        Aplica SMOTE para balancear dados desbalanceados.

        - Extrai features e labels do DataFrame preprocessado.
        - Usa SMOTE com random_state=42 para reprodutibilidade.
        - Armazena dados balanceados em X_resampled e y_resampled.

        Lança CustomException em caso de erro.
        """
        try:
            # Seleciona apenas as colunas de features (variáveis independentes)
            X = self.data[['Pclass', 'Sex', 'Age', 'Fare', 'Embarked', 'Familysize', 'Isalone', 'HasCabin', 'Title', 'Pclass_Fare', 'Age_Fare']]
            # Extrai a coluna de label (variável dependente)
            y = self.data['Survived']

            # Inicializa SMOTE com random_state fixo
            smote = SMOTE(random_state=42)
            # Aplica SMOTE para gerar amostras sintéticas da classe minoritária
            self.X_resampled, self.y_resampled = smote.fit_resample(X, y)

            logger.info("Hanled imbalance data sucesfully...")

        except Exception as e:
            logger.error(f"Error while imabalanced handling data {e}")
            raise CustomException(str(e))
    
    def store_feature_in_redis(self):
        """
        Armazena features de cada passageiro em Redis.

        - Itera sobre cada linha do DataFrame.
        - Cria um dicionário {entity_id: features} com todos os PassengerId.
        - Armazena tudo em lote via feature_store.store_batch_features().

        Lança CustomException em caso de erro.
        """
        try:
            # Constrói um dicionário com features de cada passageiro
            batch_data = {}
            for idx, row in self.data.iterrows():
                # Usa PassengerId como chave (entity_id)
                entity_id = row["PassengerId"]
                # Cria dicionário com todas as features e o label
                features = {
                    "Age": row['Age'],
                    "Fare": row["Fare"],
                    "Pclass": row["Pclass"],
                    "Sex": row["Sex"],
                    "Embarked": row["Embarked"],
                    "Familysize": row["Familysize"],
                    "Isalone": row["Isalone"],
                    "HasCabin": row["HasCabin"],
                    "Title": row["Title"],
                    "Pclass_Fare": row["Pclass_Fare"],
                    "Age_Fare": row["Age_Fare"],
                    "Survived": row["Survived"]
                }
                batch_data[entity_id] = features
            
            # Armazena todo o lote em Redis de uma vez
            self.feature_store.store_batch_features(batch_data)
            logger.info("Data has been feeded into Feature Store..")
        except Exception as e:
            logger.error(f"Error while feature storing data {e}")
            raise CustomException(str(e))
        
    def retrive_feature_redis_store(self, entity_id):
        """
        Recupera features de um passageiro específico do Redis.

        Parâmetros:
        - entity_id: ID do passageiro a recuperar.

        Retorno:
        - Dicionário com features do passageiro ou None se não encontrado.
        """
        # Busca as features usando o entity_id no Redis
        features = self.feature_store.get_features(entity_id)
        # Retorna as features se existirem, senão None
        if features:
            return features
        return None
    
    def run(self):
        """
        Ponto de entrada que executa todo o pipeline de processamento.

        Passos:
        1. load_data(): carrega dados de treino e teste.
        2. preprocess_data(): pré-processa e cria novas features.
        3. handle_imbalance_data(): balanceia com SMOTE.
        4. store_feature_in_redis(): armazena features em Redis.

        Lança CustomException se qualquer etapa falhar.
        """
        try:
            logger.info("Starting our Data Processing Pipleine...")
            # Etapa 1: carregamento
            self.load_data()
            # Etapa 2: pré-processamento
            self.preprocess_data()
            # Etapa 3: balanceamento
            self.handle_imbalance_data()
            # Etapa 4: armazenamento em Redis
            self.store_feature_in_redis()

            logger.info("End of pipeline Data Processing...")

        except Exception as e:
            logger.error(f"Error while Data Processing Pipleine {e}")
            raise CustomException(str(e))
        
if __name__ == "__main__":
    # Instancia o RedisFeatureStore
    feature_store = RedisFeatureStore()

    # Instancia o processador com os caminhos de treino e teste
    data_processor = DataProcessing(TRAIN_PATH, TEST_PATH, feature_store)
    # Executa todo o pipeline
    data_processor.run()

    # Testa recuperação de features de um passageiro específico (id=332)
    print(data_processor.retrive_feature_redis_store(entity_id=332))

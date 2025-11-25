"""
Módulo responsável pelo treinamento de modelo usando features armazenadas no Redis.

Responsabilidades:
- Extrair features do Redis.
- Preparar dataset de treino e teste.
- Buscar melhores hiperparâmetros via RandomizedSearchCV.
- Treinar RandomForest e avaliar acurácia.
- Salvar o modelo treinado em disco.

"""
from src.logger import get_logger
from src.custom_exception import CustomException
import pandas as pd
from src.feature_store import RedisFeatureStore
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
import os
import pickle
from sklearn.metrics import accuracy_score

logger = get_logger(__name__)

class ModelTraining:
    """
    Classe que encapsula todo o pipeline de treinamento.

    Parâmetros principais:
    - feature_store: instância de RedisFeatureStore para leitura de features.
    - model_save_path: diretório onde o modelo será salvo.
    """

    def __init__(self , feature_store:RedisFeatureStore , model_save_path = "artifacts/models/"):
        """
        Inicializa atributos e cria diretório de saída se necessário.
        """
        self.feature_store = feature_store
        self.model_save_path = model_save_path
        self.model = None

        # Garante que o diretório para salvar modelos exista
        os.makedirs(self.model_save_path , exist_ok=True)
        logger.info("Model Training initialized...")

    def load_data_from_redis(self , entity_ids):
        """
        Lê features do Redis para uma lista de entity_ids.

        Retorna:
        - lista de dicionários com as features encontradas.
        """
        try:
            logger.info("Extracting data from Redis")

            data = []
            for entity_id in entity_ids:
                # Busca features de cada entidade no feature store
                features = self.feature_store.get_features(entity_id)
                if features:
                    data.append(features)
                else:
                    # Registra aviso quando feature não encontrada
                    logger.warning("Feature not found")
            return data
        except Exception as e:
            logger.error(f"Error while loading data from Redis {e}")
            raise CustomException(str(e))
        
    def prepare_data(self):
        """
        Prepara os dados para treinamento.

        Passos:
        - Recupera todos os entity_ids do feature store.
        - Divide em listas de treino e teste.
        - Lê features do Redis e converte em DataFrames.
        - Separa X e y para treino e teste.

        Retorna:
        - X_train, X_test, y_train, y_test
        """
        try:
            # Lista de ids armazenados no Redis
            entity_ids = self.feature_store.get_all_entity_ids()

            # Divide ids entre treino e teste
            train_entity_ids , test_entity_ids = train_test_split(entity_ids , test_size=0.2 , random_state=42)

            # Carrega dados correspondentes do Redis
            train_data = self.load_data_from_redis(train_entity_ids)
            test_data = self.load_data_from_redis(test_entity_ids)

            # Converte listas de dicionários para DataFrame pandas
            train_df = pd.DataFrame(train_data)
            test_df = pd.DataFrame(test_data)

            # Separa features (X) e rótulos (y)
            X_train = train_df.drop('Survived',axis=1)
            logger.info(X_train.columns)
            X_test = test_df.drop('Survived',axis=1)
            y_train = train_df["Survived"]
            y_test = test_df["Survived"]

            logger.info("Preparation for Model Training completed")
            return X_train , X_test , y_train, y_test
        
        except Exception as e:
            logger.error(f"Error while preparing data {e}")
            raise CustomException(str(e))
        
    def hyperparamter_tuning(self,X_train,y_train):
        """
        Executa busca aleatória de hiperparâmetros para RandomForest.

        Retorna o melhor estimador encontrado.
        """
        try:
            param_distributions = {
                    'n_estimators': [100, 200, 300],
                    'max_depth': [10, 20, 30],
                    'min_samples_split': [2, 5],
                    'min_samples_leaf': [1, 2]
                }
            
            rf = RandomForestClassifier(random_state=42)
            random_search = RandomizedSearchCV(rf, param_distributions, n_iter=10, cv=3, scoring='accuracy', random_state=42)
            # Ajusta o RandomizedSearchCV com os dados de treino
            random_search.fit(X_train, y_train)

            logger.info(f"Best paramters : {random_search.best_params_}")
            return random_search.best_estimator_
        
        except Exception as e:
            logger.error(f"Error while hyperparamter tuning {e}")
            raise CustomException(str(e))
        
    def train_and_evaluate(self , X_train , y_train , X_test , y_test):
        """
        Treina o modelo com os melhores hiperparâmetros e avalia acurácia.

        Salva o modelo treinado em disco e retorna a acurácia obtida.
        """
        try:
            # Obtém o melhor classificador via tuning
            best_rf = self.hyperparamter_tuning(X_train,y_train)

            # Faz predições no conjunto de teste
            y_pred = best_rf.predict(X_test)

            # Calcula métrica de avaliação (acurácia)
            accuracy = accuracy_score(y_test,y_pred)

            logger.info(f"Accuracy is {accuracy}")

            # Persiste modelo em arquivo
            self.save_model(best_rf)

            return accuracy
        
        except Exception as e:
            logger.error(f"Error while model training {e}")
            raise CustomException(str(e))
    
    def save_model(self , model):
        """
        Salva o objeto do modelo em disco usando pickle.
        """
        try:
            model_filename = f"{self.model_save_path}random_forest_model.pkl"

            with open(model_filename,'wb') as model_file:
                pickle.dump(model , model_file)

            logger.info(f"Model saved at {model_filename}")
        except Exception as e:
            logger.error(f"Error while model saving {e}")
            raise CustomException(str(e))
        
    def run(self):
        """
        Orquestra execução completa do pipeline de treinamento.

        Passos:
        - prepara dados
        - treina e avalia o modelo
        """
        try:
            logger.info("Starting Model Training Pipleine....")
            X_train , X_test , y_train, y_test = self.prepare_data()
            accuracy = self.train_and_evaluate(X_train , y_train, X_test , y_test)

            logger.info("End of Model Training pipeline...")

        except Exception as e:
            logger.error(f"Error while model training pipeline {e}")
            raise CustomException(str(e))
        
if __name__ == "__main__":
    # Instancia o feature store e executa o pipeline quando o módulo é executado direto
    feature_store = RedisFeatureStore()
    model_trainer = ModelTraining(feature_store)
    model_trainer.run()








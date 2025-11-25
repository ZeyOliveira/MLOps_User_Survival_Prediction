"""
Módulo para armazenar e recuperar features em Redis.

Responsabilidades:
- Conectar ao Redis.
- Salvar features de uma entidade (por id).
- Recuperar features de uma entidade.
- Operações em lote para salvar e buscar múltiplas entidades.
- Listar todos os entity_ids armazenados.
"""
import redis
import json


class RedisFeatureStore:
    """
    Cliente simples para um feature store baseado em Redis.

    Usa chaves com o formato 'entity:{entity_id}:features' e serializa
    as features em JSON antes de salvar.
    """

    def __init__(self, host="localhost", port=6379, db=0):
        """
        Inicializa a conexão com o Redis.

        Parâmetros:
        - host: endereço do servidor Redis (padrão: localhost).
        - port: porta do servidor Redis (padrão: 6379).
        - db: banco de dados Redis a usar (padrão: 0).
        """
        # Cria o cliente Redis com decode_responses para trabalhar com strings
        self.client = redis.StrictRedis(
            host=host,
            port=port,
            db=db,
            decode_responses=True
        )

    def store_features(self, entity_id, features):
        """
        Salva as features de uma entidade no Redis.

        Parâmetros:
        - entity_id: identificador único da entidade.
        - features: dicionário com as features a salvar.

        Nota: Serializa o dicionário em JSON antes de armazenar.
        """
        # Monta a chave padrão para armazenamento
        key = f"entity:{entity_id}:features"
        # Serializa o dicionário em JSON e salva no Redis
        self.client.set(key, json.dumps(features))

    def get_features(self, entity_id):
        """
        Recupera as features de uma entidade do Redis.

        Parâmetros:
        - entity_id: identificador único da entidade.

        Retorno:
        - Dicionário com as features se existir, None caso contrário.

        Nota: Desserializa o JSON de volta para objeto Python.
        """
        # Monta a mesma chave usada para salvar
        key = f"entity:{entity_id}:features"
        # Busca o valor JSON no Redis
        features = self.client.get(key)
        # Se encontrou, converte JSON de volta para dicionário
        if features:
            return json.loads(features)
        return None
    
    def store_batch_features(self, batch_data):
        """
        Salva múltiplas features em lote.

        Parâmetros:
        - batch_data: dicionário com {entity_id: features} para cada entidade.

        Nota: Chama store_features iterativamente para cada entidade.
        """
        # Itera sobre cada entidade no lote
        for entity_id, features in batch_data.items():
            # Salva as features de cada entidade
            self.store_features(entity_id, features)

    def get_batch_features(self, entity_ids):
        """
        Recupera features para uma lista de entity_ids.

        Parâmetros:
        - entity_ids: iterável contendo os ids a recuperar.

        Retorno:
        - Dicionário com {entity_id: features} para cada id fornecido.

        Nota: Se um id não existir, seu valor será None.
        """
        # Constrói um dicionário vazio para armazenar resultado
        batch_features = {}
        # Itera sobre cada id solicitado
        for entity_id in entity_ids:
            # Recupera as features de cada entidade
            batch_features[entity_id] = self.get_features(entity_id)
        return batch_features
    
    def get_all_entity_ids(self):
        """
        Lista todos os entity_ids armazenados no Redis.

        Retorno:
        - Lista contendo todos os ids de entidades presentes.

        Nota: Faz busca por padrão 'entity:*:features' e extrai o id.
        """
        # Recupera todas as chaves que seguem o padrão de armazenamento
        keys = self.client.keys('entity:*:features')

        # Extrai o segundo segmento da chave 'entity:{id}:features'
        # Exemplo: 'entity:123:features' -> '123'
        entity_ids = [key.split(':')[1] for key in keys]
        return entity_ids




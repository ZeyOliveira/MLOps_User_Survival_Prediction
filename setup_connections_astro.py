import yaml
from airflow.models import Connection
from airflow.settings import Session
import os

# Caminho para o arquivo config.yml dentro da pasta .astro
CONFIG_PATH = os.path.join(".astro", "config.yml")

def load_connections():
    # Abre o YAML com todas as conexões
    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)

    # Inicia a sessão do Airflow
    session = Session()

    # Itera sobre todas as conexões definidas no YAML
    for conn in config.get('connections', []):
        # Verifica se já existe conexão com mesmo conn_id
        existing_conn = session.query(Connection).filter(Connection.conn_id == conn['conn_id']).first()
        if existing_conn:
            print(f"Conexão '{conn['conn_id']}' já existe. Pulando...")
            continue

        # Cria a conexão
        c = Connection(**conn)
        session.add(c)
        print(f"Conexão '{conn['conn_id']}' criada com sucesso!")

    session.commit()
    session.close()
    print("Todas as conexões foram carregadas!")

if __name__ == "__main__":
    load_connections()

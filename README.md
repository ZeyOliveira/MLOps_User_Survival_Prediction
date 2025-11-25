# 🚀 User Survival Prediction: Um Pipeline MLOps Completo com GCP, Airflow, Redis e Monitoramento! 📊

## Visão Geral do Projeto

Este projeto implementa uma solução de Machine Learning (ML) ponta-a-ponta para prever a sobrevivência de indivíduos no desastre do Titanic. O foco principal é demonstrar um pipeline MLOps robusto, que abrange desde a ingestão de dados em nuvem até o monitoramento contínuo do modelo em produção, garantindo automação, escalabilidade e observabilidade.

Desenvolvido como parte dos meus estudos em Ciência de Dados, com ênfase em Power BI, Excel e SQL, este projeto consolida conhecimentos em engenharia de dados, pré-processamento, treinamento de modelos e as melhores práticas de MLOps.

## �� Destaques MLOps e Tecnológicos

*   **Automação End-to-End:** Orquestração completa do pipeline de ML com Apache Airflow.
*   **Infraestrutura Cloud:** Ingestão de dados a partir do Google Cloud Storage (GCS).
*   **Feature Store:** Utilização do Redis como um Feature Store de baixa latência para features pré-processadas.
*   **Servimento de Modelo:** Aplicação Flask para exposição do modelo via API web e interface de usuário.
*   **Monitoramento Ativo:** Detecção de *Data Drift* em tempo real com Alibi-Detect.
*   **Observabilidade:** Monitoramento de métricas com Prometheus e visualização em dashboards no Grafana.
*   **Versionamento:** Controle de versão de código (Git/GitHub) e dados/artefatos.

## 🧠 Arquitetura do Sistema

A arquitetura do projeto foi projetada para ser modular e extensível, integrando diversas ferramentas em um fluxo de trabalho coeso:

```
                              ┌───────────────────┐
                              │    Google Cloud   │
                              │ (Bucket p/ CSV)   │
                              └───────┬───────────┘
                                      │ Ingestão
                                      ▼
                      ┌───────────────────────────────────────────────┐
                      │             Pipeline MLOps (Airflow DAG)      │
                      │ (Orquestra: Ingestão -> Pré-processamento -> Treinamento) │
                      └──────────────────┬────────────────────────────┘
                                         │
               ┌─────────────────────────┼─────────────────────────┐
               ▼                         ▼                         ▼
    ┌───────────────────────┐   ┌─────────────────┐   ┌──────────────────────┐
    │ DAG Ingestão (Airflow)│   │  Módulo Python  │   │   Módulo Python      │
    │ (GCS -> PostgreSQL)   │   │ (DataIngestion.py) │   │ (DataProcessing.py)  │
    └───────────────────────┘   └─────────────────┘   └──────────────────────┘
               │                          │                       │
               ▼                          ▼                       ▼
    ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
    │    PostgreSQL   │──────►│    CSVs Locais  │──────►│     Redis FS    │
    │ (Tabela Titanic)│       │ (train.csv, test.csv) │   │ (Features Prontas)│
    └─────────────────┘       └─────────────────┘       └─────────────────┘
                                                                 │
                                                                 ▼
                                                        ┌───────────────────┐
                                                        │   Módulo Python   │
                                                        │ (ModelTraining.py) │
                                                        └───────────────────┘
                                                                 │
                                                                 ▼
                                                        ┌───────────────────┐
                                                        │ Modelo Treinado   │
                                                        │ (Salvo em Artefatos) │
                                                        └───────────────────┘
                                                                 │
      ┌──────────────────────────────────────────────────────────┼──────────────────────────────────────────────────┐
      │                                                          │                                                  │
      ▼                                                          ▼                                                  ▼
┌───────────────┐                               ┌───────────────────────────┐                        ┌───────────────────────────┐
│ Aplicação Flask │◀─── Previsões ────────────────│  Alibi-Detect             │                        │ Prometheus & Grafana      │
│ (UI Local)      │                               │ (Detecção de Data Drift)  │                        │ (Monitoramento de Métricas) │
└───────────────┘                               └───────────────────────────┘                        └───────────────────────────┘
```

## 🛠 Tecnologias Utilizadas

*   **Linguagem:** Python (3.12+)
*   **Orquestração:** Apache Airflow (via Astro CLI)
*   **Nuvem:** Google Cloud Platform (GCS para armazenamento de dados brutos)
*   **Banco de Dados:** PostgreSQL (armazenamento intermediário de dados)
*   **Feature Store:** Redis (para acesso de baixa latência às features)
*   **Manipulação de Dados:** Pandas, NumPy
*   **Machine Learning:** Scikit-learn (modelo, pré-processamento), Imblearn (SMOTE para balanceamento)
*   **Detecção de Drift:** Alibi-Detect (KSDrift)
*   **Monitoramento:** Prometheus (coleta de métricas), Grafana (visualização de dashboards)
*   **Desenvolvimento Web:** Flask (API e UI para o modelo)
*   **Controle de Versão:** Git, GitHub
*   **Containerização:** Docker, Docker Compose

## �� Componentes Chave do Pipeline

1.  **`dags/extract_data_from_gcp.py` (DAG de Ingestão de Dados Brutos)**
    *   **Função:** Orquestra a extração do arquivo `Titanic-Dataset.csv` de um bucket no GCS, faz um pré-processamento leve (ETL) e carrega os dados brutos na tabela `titanic` em um banco de dados PostgreSQL local rodando num conteiner Docker.
    *   **Tecnologias:** Apache Airflow, `apache-airflow-providers-google`, `apache-airflow-providers-postgres`.

2.  **`src/data_ingestion.py` (Script de Preparação Inicial de Dados)**
    *   **Função:** Conecta ao PostgreSQL, extrai a tabela `titanic` como DataFrame, divide-a em conjuntos de treino (80%) e teste (20%) com `random_state=42`, e salva-os como arquivos CSV (`train.csv`, `test.csv`) no disco local.
    *   **Tecnologias:** Pandas, `psycopg2`, Scikit-learn.

3.  **`src/feature_store.py` (Módulo de Feature Store com Redis)**
    *   **Função:** Atua como um *Feature Store* simples, fornecendo métodos para conectar ao Redis, serializar features (JSON) de entidades e armazená-las/recuperá-las de forma individual ou em lote. Projetado para baixa latência.
    *   **Tecnologias:** Redis rodando dentro do Docker.

4.  **`src/data_processing.py` (Módulo de Pré-processamento, Balanceamento, Feature Engineering, Encoding e Armazenamento de Features)**
    *   **Função:** Carrega os CSVs de treino e teste, executa limpeza de dados, preenchimento de valores ausentes, codificação de variáveis categóricas, engenharia de novas features (`Familysize`, `HasCabin`, `Title`, `Pclass_Fare`, `Age_Fare`), tratamento de desbalanceamento usando SMOTE nos dados de treino, e finalmente armazena as features processadas no Redis Feature Store.
    *   **Tecnologias:** Pandas, Scikit-learn, Imblearn, `RedisFeatureStore`.

5.  **`src/model_training.py` (Módulo de Treinamento do Modelo)**
    *   **Função:** Recupera as features processadas e balanceadas do Redis Feature Store, busca os melhores hyperparâmetros usando `RandomizedSearchCV` treina um modelo de Machine Learning `RandomForestClassifier` para prever a sobrevivência, avalia seu desempenho e salva o modelo treinado (ex: `random_forest_model.pkl`) no diretório `artifacts/models/`.
    *   **Tecnologias:** Scikit-learn, `RedisFeatureStore`.

6.  **`pipeline/training_pipeline.py` (Pipeline Principal do MLOps)**
    *   **Função:** Orquestra a execução sequencial de todas as etapas do pipeline: Ingestão de Dados Brutos (via `data_ingestion.py`), Pré-processamento/Feature Engineering/Balanceamento (`data_processing.py`) e Treinamento do Modelo (`model_training.py`).
    *   **Tecnologias:** Apache Airflow, Feature Store, logger, CustomException.

7.  **`application.py` (Servidor Flask para Servir o Modelo e Monitorar Drift)**
    *   **Função:** Expõe o modelo de ML treinado via uma API web e interface de usuário. Recebe inputs do usuário, faz previsões e, crucialmente, monitora a qualidade dos dados de entrada em tempo real.
    *   **Tecnologias:** Flask, `Alibi-Detect` (KSDrift), `prometheus_client`, `Grafana`, `RedisFeatureStore`, Scikit-learn.
    *   **Rotas:**
        *   `/`: Renderiza o formulário de previsão (`index.html`).
        *   `/predict` (POST): Processa inputs, detecta drift, faz previsão e exibe resultado.
        *   `/metrics`: Expõe métricas de Prometheus (`prediction_count`, `drift_count`).

## 🚀 Como Executar o Projeto Localmente

Siga estes passos para configurar e executar todo o pipeline em sua máquina local.

### Pré-requisitos

*   Docker e Docker Compose
*   Python 3.12+
*   Astro CLI (para gerenciar o ambiente Airflow)
*   Uma conta GCP com um bucket configurado e uma chave de conta de serviço (JSON) para acesso ao GCS.

### Configuração

1.  **Clone o Repositório:**
    ```bash
    git clone https://github.com/ZeyOliveira/MLOps_User_Survival_Prediction.git
    cd user_survival_prediction
    ```

2.  **Configuração do GCP:**
    *   Certifique-se de ter um bucket no GCP com o arquivo `Titanic-Dataset.csv`.
    *   Crie uma chave de conta de serviço com permissões de leitura para o bucket e salve o arquivo JSON resultante em `include/gcp_key.json` dentro do seu projeto. (Crie a pasta `include` se ela não existir).

3.  **Configuração Astro CLI e Docker Compose:**
    *   Inicialize o ambiente Astro Airflow:
        ```bash
        astro dev init
        ```
    *   O Airflow usará o `requirements.txt` para instalar as dependências. Verifique se ele contém todas as bibliotecas necessárias.
    *   **Ajuste o `docker-compose.yaml`:**
        *   Certifique-se de que o `docker-compose.yml` inclua serviços, **Prometheus** e **Grafana**, além dos serviços padrão do Astro Airflow. Exemplo de estrutura no `docker-compose.yaml`:
            ```yaml            
            prometheus:
              image: prom/prometheus:latest
              command: --config.file=/etc/prometheus/prometheus.yml
              ports:
                - "9090:9090"
              volumes:
                - ./prometheus.yml:/etc/prometheus/prometheus.yml # Seu arquivo de config prometheus
            
            grafana:
              image: grafana/grafana:latest
              ports:
                - "3000:3000"
              environment:
                GF_SECURITY_ADMIN_USER: admin
                GF_SECURITY_ADMIN_PASSWORD: admin # Mude para uma senha segura em produção
              volumes:
                - grafana_data:/var/lib/grafana
            
            volumes:
              postgres_data:
              grafana_data:
            ```
        *   Crie um arquivo `prometheus.yml` na raiz do seu projeto com o seguinte conteúdo para que o Prometheus possa "raspar" as métricas do seu aplicativo Flask:
            ```yaml
            global:
              scrape_interval: 15s # By default, scrape targets every 15 seconds.
            
            scrape_configs:
              - job_name: 'flask-app-metrics'
                static_configs:
                  - targets: ['host.docker.internal:8000'] # Para Docker no Windows/Mac, use 'host.docker.internal'
                                                           # Para Linux, pode ser necessário usar o IP do host ou um alias de rede.
            ```

4.  **Inicie os Serviços Docker:**
    ```bash
    docker-compose up -d
    ```
    Isso iniciará Prometheus, Grafana.

5.  **Inicie o Ambiente Airflow:**
    ```bash
    astro dev start
    ```
    Acesse a UI do Airflow em `http://localhost:8080`.

6.  **Configure Conexões no Airflow:**
    *   Na UI do Airflow, vá em `Admin > Connections` e crie:
        *   Uma conexão `google_cloud_default` usando o tipo `Google Cloud` e apontando para o arquivo de chave JSON que você salvou em `include/gcp_key.json`.
        *   Uma conexão `postgres_default` usando o tipo `Postgres`, Host `postgres` (nome do serviço Docker), Schema `user_survival_db`, Login `postgres`, Password `postgres`.

7.  **Habilite e Rode a DAG Principal:**
    *   Na UI do Airflow, procure pela DAG `extract_data_from_gcp.py` (ou o nome que você deu à sua DAG principal).
    *   Ative-a (toggle).
    *   Acione-a manualmente para iniciar o pipeline completo.
    *   Ou rode o arquivo `setup_connections_astro.py`, para contruir a DAG, com o arquivo `config.yml` com esse conteúdo:
  ```
  connections:
    - conn_id: google_cloud_default
      conn_type: google_cloud_platform
      key_path: /usr/local/airflow/include/gcp-key.json
      schema: https://www.googleapis.com/auth/cloud-platform
  
    - conn_id: postgres_default
      conn_type: postgres
      host: localhost
      login: postgres
      password: postgres
      schema: public
      port: 5432
  ```

8.  **Execute o Aplicativo Flask:**
    *   Após o pipeline do Airflow ter sido executado com sucesso e o modelo ter sido treinado e salvo (e as features no Redis), você pode iniciar o aplicativo Flask.
    *   Abra um novo terminal na raiz do projeto e execute:
        ```bash
        python application.py
        ```
    *   Acesse o aplicativo em `http://localhost:5000`.
    *   As métricas do Prometheus estarão disponíveis em `http://localhost:9090/`.
    *   Acesse o Grafana em `http://localhost:3000` (admin/admin) e configure uma fonte de dados Prometheus apontando para `http://prometheus:9090`. Crie um dashboard para visualizar `prediction_count_total` e `drift_count_total`.

## 📸 Demonstração do Projeto

Aqui você encontrará capturas de tela e GIFs que ilustram o funcionamento do pipeline e da aplicação.

*(**Instruções para você, Zeygler:** Substitua o texto abaixo pelas suas próprias imagens e GIFs de alta qualidade.)*

### 1. **Pipeline de Ingestão e Treinamento no Airflow**
*   Screenshot mostrando a DAG principal (`ml_pipeline_dag.py`) com todas as tarefas em estado "Success".
*   Screenshot dos logs de uma tarefa chave (ex: `data_processing`) mostrando a execução.
*   *Opcional:* GIF curto da DAG sendo acionada e as tarefas passando para verde.

### 2. **Dados no PostgreSQL**
*   Screenshot do DBeaver mostrando a tabela `titanic` populada após a execução da DAG de ingestão, com uma query `SELECT * FROM titanic;`.

### 3. **Aplicação Flask de Previsão**
*   Screenshot da página inicial (`http://localhost:5000`) com o formulário vazio.
*   Screenshot do formulário preenchido e o resultado da previsão (ex: "The prediction is: Survived").
*   GIF curto de você preenchendo o formulário e clicando em "Predict", mostrando o resultado.

### 4. **Monitoramento com Prometheus e Grafana**
*   Screenshot da UI do Prometheus (`http://localhost:9090`) com uma query para `prediction_count_total` ou `drift_count_total` exibindo o valor.
*   Screenshot de um dashboard no Grafana (`http://localhost:3000`) que você criou, mostrando gráficos de `prediction_count_total` e `drift_count_total` ao longo do tempo.
*   **🎉 Demonstração de Data Drift (O MAIS IMPACTANTE!):**
    *   GIF ou vídeo curto: Comece mostrando o dashboard do Grafana com `drift_count_total` baixo/zero.
    *   Em seguida, na aplicação Flask, **insira dados de entrada deliberadamente "estranhos" ou muito diferentes** dos dados de referência (ex: Idade = 1000, Tarifa = -500).
    *   Mostre o `drift_count_total` no Grafana incrementando após essas submissões, demonstrando que o Alibi-Detect identificou o desvio e o Prometheus registrou.

## ✨ MLOps em Destaque

Este projeto demonstra uma compreensão prática dos princípios de MLOps:

*   **Automação:** Todas as etapas do ciclo de vida do ML são automatizadas via Airflow, reduzindo erros manuais e tempo de execução.
*   **Versionamento:** Código e dados são versionados no GitHub, garantindo reprodutibilidade e rastreabilidade.
*   **Feature Store:** O Redis atua como um repositório centralizado e eficiente para features, desacoplando a geração do consumo e garantindo consistência.
*   **Monitoramento e Observabilidade:** A integração com Prometheus e Grafana fornece visibilidade em tempo real sobre a saúde do serviço e o comportamento do modelo.
*   **Detecção de Drift:** A implementação do Alibi-Detect oferece um mecanismo proativo para identificar quando o modelo pode estar se tornando obsoleto devido a mudanças nos dados.
*   **Desacoplamento:** Componentes como o Feature Store e o servidor de modelo são independentes, facilitando a manutenção e a escalabilidade.

## 🔮 Próximos Passos

*   **Integração com ChatGPT:** Melhorar a experiência do usuário na aplicação Flask, fornecendo explicações mais ricas ou contexto adicional para as previsões usando uma API de linguagem natural.
*   **CI/CD:** Implementar pipelines de Integração Contínua e Entrega Contínua (CI/CD) para automatizar o deploy do código.
*   **A/B Testing:** Adicionar funcionalidades para testar diferentes versões do modelo em produção.
*   **Mais Modelos:** Explorar outros algoritmos de ML e comparar seu desempenho.
*   **Containerização do Flask:** Criar um Dockerfile para o aplicativo Flask e integrá-lo ao `docker-compose.yaml`.

---

**Conecte-se comigo:**

*   **LinkedIn:** https://www.linkedin.com/in/zeygleroliveira/
*   **GitHub:** https://github.com/ZeyOliveira
*   **Gmail:** zeyglerdasilva@gmail.com

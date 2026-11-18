import os
from dotenv import load_dotenv
from src.connectors.mock_connector import generate_mock_data

# Carrega as variáveis de ambiente do ficheiro .env
load_dotenv()

def run_ingestion():
    """
    Serviço central de ingestão que dispara a geração de dados mockados 
    (Google Ads e Meta Ads) e populariza o banco SQLite.
    """
    print(" A iniciar sincronização de dados das plataformas...")
    
    # Valida se as chaves principais existem no .env
    google_dev_token = os.getenv("GOOGLE_DEVELOPER_TOKEN")
    meta_app_id = os.getenv("META_APP_ID")
    
    if not google_dev_token or not meta_app_id:
        print(" Atenção: Algumas variáveis do .env não foram encontradas. A utilizar modo de simulação.")
    else:
        print(" Configurações de ambiente validadas com sucesso.")

    # Executa a função do conector que gera e grava os dados na base SQLite
    generate_mock_data(days=30)
    
    print(" Sincronização e persistência concluídas com sucesso!")
    return True

if __name__ == "__main__":
    run_ingestion()
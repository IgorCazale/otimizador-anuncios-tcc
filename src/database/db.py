import sqlite3
import os
from dotenv import load_dotenv


load_dotenv()

# Pega o caminho do banco definido no .env ou usa o padrão 'data/database.db'
DB_PATH = os.getenv("DB_PATH", "data/database.db")

def get_connection():
    """Cria e retorna a conexão com o banco de dados SQLite."""
    
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    return conn

def init_db():
    """Inicializa a tabela de dados brutos das campanhas."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tabela para armazenar as métricas brutas vinda das APIs (Google, Meta, etc)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS campaign_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT NOT NULL,         -- 'Google Ads', 'Meta Ads'
            campaign_id TEXT NOT NULL,
            campaign_name TEXT NOT NULL,
            date TEXT NOT NULL,
            impressions INTEGER DEFAULT 0,  -- Impressões
            clicks INTEGER DEFAULT 0,       -- Cliques
            cost REAL DEFAULT 0.0,          -- Valor investido (Custo)
            conversions INTEGER DEFAULT 0,  -- Número de Vendas/Aquisições
            revenue REAL DEFAULT 0.0        -- Receita total gerada
        )
    ''')
    
    conn.commit()
    conn.close()
    print(" Banco de dados e tabela 'campaign_metrics' criados com sucesso!")

if __name__ == "__main__":
    init_db()
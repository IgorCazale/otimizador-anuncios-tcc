import pandas as pd
import sqlite3
import sys
import os

# Permite importar módulos da pasta src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.database.db import get_connection

def load_raw_data():
    """Carrega os dados brutos da tabela SQLite para um DataFrame do Pandas."""
    conn = get_connection()
    query = "SELECT * FROM campaign_metrics"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def calculate_kpis(df):
    """
    Agrupa os dados e calcula as métricas-chave de marketing digital:
    - CTR (Click-Through Rate): (Cliques / Impressões) * 100
    - CPC (Custo por Clique): Custo / Cliques
    - CPA (Custo por Aquisição/Conversão): Custo / Conversões
    - ROAS (Retorno sobre Investimento em Anúncios): Receita / Custo
    """
    if df.empty:
        return df

    # Agrupamento por Plataforma e Campanha
    summary = df.groupby(['platform', 'campaign_name']).agg({
        'impressions': 'sum',
        'clicks': 'sum',
        'cost': 'sum',
        'conversions': 'sum',
        'revenue': 'sum'
    }).reset_index()

    # Fórmulas de KPIs com proteção contra divisão por zero
    summary['CTR (%)'] = summary.apply(
        lambda r: round((r['clicks'] / r['impressions'] * 100), 2) if r['impressions'] > 0 else 0.0, axis=1
    )
    summary['CPC (R$)'] = summary.apply(
        lambda r: round(r['cost'] / r['clicks'], 2) if r['clicks'] > 0 else 0.0, axis=1
    )
    summary['CPA (R$)'] = summary.apply(
        lambda r: round(r['cost'] / r['conversions'], 2) if r['conversions'] > 0 else 0.0, axis=1
    )
    summary['ROAS'] = summary.apply(
        lambda r: round(r['revenue'] / r['cost'], 2) if r['cost'] > 0 else 0.0, axis=1
    )

    return summary

if __name__ == "__main__":
    df_raw = load_raw_data()
    df_kpis = calculate_kpis(df_raw)
    
    print("\n📊 Resumo Agrupado das Métricas com Pandas:\n")
    print(df_kpis.to_string(index=False))
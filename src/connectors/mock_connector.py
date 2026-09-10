import random
from datetime import datetime, timedelta
import sys
import os

# Permite importar módulos da pasta src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.database.db import get_connection

def generate_mock_data(days=30):
    """Gera dados simulados de campanhas do Google Ads e Meta Ads dos últimos X dias."""
    conn = get_connection()
    cursor = conn.cursor()

    campaigns = [
        {"platform": "Google Ads", "campaign_id": "G-01", "campaign_name": "Search - Institucional"},
        {"platform": "Google Ads", "campaign_id": "G-02", "campaign_name": "Performance Max - Vendas"},
        {"platform": "Meta Ads", "campaign_id": "M-01", "campaign_name": "Remarketing - Instagram Feed"},
        {"platform": "Meta Ads", "campaign_id": "M-02", "campaign_name": "Prospection - Stories/Reels"},
    ]

    today = datetime.now()
    records_inserted = 0

    for day in range(days):
        current_date = (today - timedelta(days=day)).strftime('%Y-%m-%d')
        
        for camp in campaigns:
            # Métricas simuladas coerentes
            impressions = random.randint(1000, 5000)
            clicks = random.randint(20, int(impressions * 0.10)) # CTR de ~2% a 10%
            cost = round(random.uniform(30.0, 150.0), 2)
            conversions = random.randint(0, int(clicks * 0.20)) # Conversões baseadas em cliques
            revenue = round(conversions * random.uniform(80.0, 200.0), 2) if conversions > 0 else 0.0

            cursor.execute('''
                INSERT INTO campaign_metrics 
                (platform, campaign_id, campaign_name, date, impressions, clicks, cost, conversions, revenue)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                camp["platform"], 
                camp["campaign_id"], 
                camp["campaign_name"], 
                current_date, 
                impressions, 
                clicks, 
                cost, 
                conversions, 
                revenue
            ))
            records_inserted += 1

    conn.commit()
    conn.close()
    print(f"✅ {records_inserted} registros simulados inseridos com sucesso no SQLite!")

if __name__ == "__main__":
    generate_mock_data()
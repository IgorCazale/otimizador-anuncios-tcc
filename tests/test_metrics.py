import sys
import os
import pandas as pd

# Adiciona o diretório raiz do projeto ao sys.path do Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.metrics import calculate_kpis

def test_kpi_calculations():
    sample_data = pd.DataFrame([{
        'platform': 'Meta Ads',
        'campaign_name': 'Teste',
        'impressions': 100,
        'clicks': 10,
        'cost': 50.0,
        'conversions': 2,
        'revenue': 200.0
    }])
    
    result = calculate_kpis(sample_data)
    
    assert result['CTR (%)'].iloc[0] == 10.0
    assert result['CPC (R$)'].iloc[0] == 5.0
    assert result['CPA (R$)'].iloc[0] == 25.0
    assert result['ROAS'].iloc[0] == 4.0
    print(" Todos os testes de KPIs passaram com sucesso!")

if __name__ == "__main__":
    test_kpi_calculations()
    
import pandas as pd
from src.database.db import get_connection

def load_raw_data():
    """Carrega os dados brutos de métricas do SQLite."""
    conn = get_connection()
    query = "SELECT * FROM campaign_metrics;"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def calculate_kpis(df):
    """Consolida os dados por campanha e calcula as métricas derivadas (CTR, CPC, CPA, ROAS)."""
    if df.empty:
        return pd.DataFrame()

    grouped = df.groupby(['platform', 'campaign_name']).agg({
        'impressions': 'sum',
        'clicks': 'sum',
        'cost': 'sum',
        'conversions': 'sum',
        'revenue': 'sum'
    }).reset_index()

    # Evita divisão por zero
    grouped['CTR (%)'] = grouped.apply(
        lambda r: (r['clicks'] / r['impressions'] * 100) if r['impressions'] > 0 else 0, axis=1
    )
    grouped['CPC (R$)'] = grouped.apply(
        lambda r: (r['cost'] / r['clicks']) if r['clicks'] > 0 else 0, axis=1
    )
    grouped['CPA (R$)'] = grouped.apply(
        lambda r: (r['cost'] / r['conversions']) if r['conversions'] > 0 else 0, axis=1
    )
    grouped['ROAS'] = grouped.apply(
        lambda r: (r['revenue'] / r['cost']) if r['cost'] > 0 else 0, axis=1
    )

    return grouped

def add_performance_alerts(df):
    """
    Classifica a performance da campanha com base em limites (thresholds):
    - ROAS >= 20.0 e CTR >= 5.0%: Alta Performance
    - ROAS < 20.0: Atenção / Baixo ROAS
    - Caso contrário: Neutro / Normal
    """
    def classify(row):
        if row['ROAS'] >= 20.0 and row['CTR (%)'] >= 5.0:
            return ' Alta Performance'
        elif row['ROAS'] < 20.0:
            return ' Baixo ROAS'
        else:
            return ' Estável'

    df_copy = df.copy()
    df_copy['Status'] = df_copy.apply(classify, axis=1)
    return df_copy

def generate_insights(df_alerts):
    """Gera sugestões de otimização automatizadas com base no status de cada campanha."""
    insights = []
    
    for _, row in df_alerts.iterrows():
        campanha = row['campaign_name']
        plataforma = row['platform']
        roas = row['ROAS']
        ctr = row['CTR (%)']
        cpa = row['CPA (R$)']
        
        if 'Alta Performance' in row['Status']:
            insights.append({
                'tipo': 'success',
                'titulo': f"🚀 Oportunidade de Escala: {campanha} ({plataforma})",
                'mensagem': f"Esta campanha apresenta alto retorno (ROAS de **{roas:.2f}x**) e CTR de **{ctr:.2f}%**. **Recomendação:** Aumentar o orçamento diário em 15% a 20% para otimizar a tração."
            })
        elif 'Baixo ROAS' in row['Status']:
            insights.append({
                'tipo': 'warning',
                'titulo': f"⚠️ Ponto de Atenção: {campanha} ({plataforma})",
                'mensagem': f"O ROAS está abaixo do ideal (**{roas:.2f}x**) com CPA de **R$ {cpa:.2f}**. **Recomendação:** Revisar a segmentação de público, atualizar os criativos ou pausar temporariamente se o custo continuar subindo."
            })
            
    return insights

def simulate_budget_increase(df_kpis, campaign_name, extra_budget):
    """
    Simula o impacto de um aumento de verba (extra_budget) em uma campanha específica,
    projetando novos cliques, novas conversões e receita estimada com base na média histórica.
    """
    if df_kpis.empty:
        return None
        
    # Localiza a campanha selecionada
    campaign_row = df_kpis[df_kpis['campaign_name'] == campaign_name]
    
    if campaign_row.empty:
        return None
        
    row = campaign_row.iloc[0]
    
    cost_atual = row['cost']
    clicks_atuais = row['clicks']
    conversions_atuais = row['conversions']
    revenue_atual = row['revenue']
    
    # Evita divisão por zero caso a campanha não tenha dados suficientes
    if cost_atual <= 0 or clicks_atuais <= 0:
        return None
        
    # Calcula taxas de eficiência unitária
    cpc_medio = cost_atual / clicks_atuais
    taxa_conversao = conversions_atuais / clicks_atuais if clicks_atuais > 0 else 0
    ticket_medio_conv = revenue_atual / conversions_atuais if conversions_atuais > 0 else 0
    
    # Projeção com o orçamento extra
    novos_clicks_estimados = extra_budget / cpc_medio
    novas_conversoes_estimadas = novos_clicks_estimados * taxa_conversao
    nova_receita_estimada = novas_conversoes_estimadas * ticket_medio_conv
    
    return {
        "campanha": campaign_name,
        "plataforma": row['platform'],
        "extra_budget": extra_budget,
        "novos_clicks": int(novos_clicks_estimados),
        "novas_conversoes": int(novas_conversoes_estimadas),
        "nova_receita": round(nova_receita_estimada, 2),
        "roas_projetado": round(nova_receita_estimada / extra_budget, 2) if extra_budget > 0 else 0
    }
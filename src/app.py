import streamlit as st
import pandas as pd
import sys
import os

# Permite importar módulos do projeto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.metrics import load_raw_data, calculate_kpis

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Otimizador de Anúncios TCC",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Painel Otimizador de Anúncios Digital")
st.markdown("Consolidação e análise de performance em tempo real (Google Ads & Meta Ads).")

# Carrega e processa os dados
df_raw = load_raw_data()

if df_raw.empty:
    st.warning("Nenhum dado encontrado no banco de dados SQLite.")
else:
    # Filtro lateral por plataforma
    st.sidebar.header("Filtros")
    platforms = st.sidebar.multiselect(
        "Selecione as Plataformas:",
        options=df_raw['platform'].unique(),
        default=df_raw['platform'].unique()
    )

    df_filtered = df_raw[df_raw['platform'].isin(platforms)]
    df_kpis = calculate_kpis(df_filtered)

    # Exibição dos KPIs Principais (Cards)
    total_cost = df_filtered['cost'].sum()
    total_revenue = df_filtered['revenue'].sum()
    total_clicks = df_filtered['clicks'].sum()
    total_impressions = df_filtered['impressions'].sum()
    
    global_roas = round(total_revenue / total_cost, 2) if total_cost > 0 else 0
    global_ctr = round((total_clicks / total_impressions) * 100, 2) if total_impressions > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Investimento Total", f"R$ {total_cost:,.2f}")
    col2.metric("Receita Total", f"R$ {total_revenue:,.2f}")
    col3.metric("ROAS Geral", f"{global_roas}x")
    col4.metric("CTR Médio", f"{global_ctr}%")

    st.divider()

    # Tabela consolidada com Pandas
    st.subheader("📋 Performance Detalhada por Campanha")
    st.dataframe(df_kpis, use_container_width=True)

    # Gráficos Comparativos
    st.divider()
    st.subheader("📈 Comparativo de ROAS por Campanha")
    st.bar_chart(df_kpis.set_index('campaign_name')['ROAS'])
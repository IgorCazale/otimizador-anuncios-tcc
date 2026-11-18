import sys
import os

# 0. Garante que o Python encontre a pasta 'src' ANTES de qualquer import do projeto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Imports do projeto
from src.services.metrics import (
    load_raw_data, 
    calculate_kpis, 
    add_performance_alerts, 
    generate_insights,
    simulate_budget_increase
)
from src.services.api_ingestion import run_ingestion

# 1. Configuração da página
st.set_page_config(
    page_title="Otimizador de Anúncios Digital",
    page_icon="⚡",
    layout="wide"
)

# 2. Injeção de CSS Customizado para Identidade Visual Exclusiva (Sem aspecto quadrado)
st.markdown("""
    <style>
    /* Fundo escuro profundo e fontes modernas */
    .stApp {
        background-color: #0b0f19;
        color: #f1f5f9;
    }
    
    /* Estilização da Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #1e293b;
    }

    /* Cards de KPI mais orgânicos e menos quadrados (border-radius maior) */
    .kpi-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 20px;
        padding: 22px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        border-color: #38bdf8;
    }
    .kpi-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #f8fafc;
    }
    .kpi-sub {
        font-size: 0.8rem;
        color: #38bdf8;
        margin-top: 4px;
    }

    /* Ajustes no cabeçalho */
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Cabeçalho Principal
st.markdown('<div class="main-header">Otimizador de Anúncios Digital</div>', unsafe_allow_html=True)
st.markdown("<p style='color: #94a3b8; margin-bottom: 25px;'>Painel de Inteligência e Consolidação de Métricas (Google Ads & Meta Ads)</p>", unsafe_allow_html=True)

# 4. Carga de Dados
df_raw = load_raw_data()

if df_raw.empty:
    st.error("Nenhum dado encontrado no banco de dados SQLite.")
else:
    # Garantir conversão para datetime
    df_raw['date'] = pd.to_datetime(df_raw['date'])

    # 5. Barra Lateral (Filtros Avançados)
    st.sidebar.markdown("<h3 style='color: #f8fafc;'>Filtros de Controle</h3>", unsafe_allow_html=True)

    # --- BOTÃO DE SINCRONIZAÇÃO DE DADOS ---
    if st.sidebar.button("Sincronizar / Ingerir Dados", use_container_width=True):
        with st.spinner("A conectar às APIs e a atualizar o banco..."):
            success = run_ingestion()
            if success:
                st.sidebar.success("Dados atualizados com sucesso!")
                st.rerun()  # Recarrega o app para atualizar os gráficos na hora
    
    st.sidebar.markdown("---")
    # ---------------------------------------------
    
    # Filtro de Plataformas
    platforms = st.sidebar.multiselect(
        "Plataformas:",
        options=df_raw['platform'].unique(),
        default=df_raw['platform'].unique()
    )

    # Filtro por Período de Datas
    min_date = df_raw['date'].min().date()
    max_date = df_raw['date'].max().date()
    
    date_range = st.sidebar.date_input(
        "Período de Análise:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # Aplicação dos Filtros
    if len(date_range) == 2:
        start_date, end_date = date_range
        df_filtered = df_raw[
            (df_raw['platform'].isin(platforms)) &
            (df_raw['date'].dt.date >= start_date) &
            (df_raw['date'].dt.date <= end_date)
        ]
    else:
        df_filtered = df_raw[df_raw['platform'].isin(platforms)]

    df_kpis = calculate_kpis(df_filtered)

    # 6. Cards Customizados (KPIs Gerais)
    total_cost = df_filtered['cost'].sum()
    total_revenue = df_filtered['revenue'].sum()
    total_clicks = df_filtered['clicks'].sum()
    total_impressions = df_filtered['impressions'].sum()
    
    global_roas = round(total_revenue / total_cost, 2) if total_cost > 0 else 0
    global_ctr = round((total_clicks / total_impressions) * 100, 2) if total_impressions > 0 else 0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Investimento Total</div>
                <div class="kpi-value">R$ {total_cost:,.2f}</div>
                <div class="kpi-sub">Verba Consumida</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Receita Gerada</div>
                <div class="kpi-value">R$ {total_revenue:,.2f}</div>
                <div class="kpi-sub">Retorno Bruto</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">ROAS Geral</div>
                <div class="kpi-value" style="color: #38bdf8;">{global_roas}x</div>
                <div class="kpi-sub">Eficiência dos Anúncios</div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">CTR Médio</div>
                <div class="kpi-value" style="color: #818cf8;">{global_ctr}%</div>
                <div class="kpi-sub">Taxa de Engajamento</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 7. Gráfico Interativo com Plotly (Ajustado para não ficar muito largo/esticado)
    st.markdown("<h3 style='color: #f8fafc;'>Performance de ROAS por Campanha</h3>", unsafe_allow_html=True)
    
    fig = px.bar(
        df_kpis,
        x='campaign_name',
        y='ROAS',
        color='platform',
        text='ROAS',
        color_discrete_map={'Google Ads': '#38bdf8', 'Meta Ads': '#818cf8'},
        labels={'campaign_name': 'Campanha', 'ROAS': 'ROAS (x)'}
    )

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#94a3b8'),
        xaxis=dict(showgrid=False, color='#94a3b8'),
        yaxis=dict(showgrid=True, gridcolor='#1e293b', color='#94a3b8'),
        legend=dict(title_text='', orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    fig.update_traces(texttemplate='%{text:.2f}x', textposition='outside')

    # Envolve o gráfico em colunas para limitar a largura e dar respiro visual
    _, col_chart, _ = st.columns([0.05, 0.9, 0.05])
    with col_chart:
        st.plotly_chart(fig, use_container_width=True)

    # 8. Tabela Consolidada com Engine de Alertas
    df_kpis_alerts = add_performance_alerts(df_kpis)

    st.markdown("<h3 style='color: #f8fafc;'>Detalhamento Consolidado com Status</h3>", unsafe_allow_html=True)
    
    cols_order = ['platform', 'campaign_name', 'Status', 'impressions', 'clicks', 'cost', 'conversions', 'revenue', 'CTR (%)', 'CPC (R$)', 'CPA (R$)', 'ROAS']
    df_kpis_alerts = df_kpis_alerts[cols_order]

    st.dataframe(
        df_kpis_alerts.style.format({
            'impressions': '{:,}',
            'clicks': '{:,}',
            'cost': 'R$ {:,.2f}',
            'conversions': '{:,}',
            'revenue': 'R$ {:,.2f}',
            'CTR (%)': '{:.2f}%',
            'CPC (R$)': 'R$ {:.2f}',
            'CPA (R$)': 'R$ {:.2f}',
            'ROAS': '{:.2f}x'
        }),
        use_container_width=True
    )

    # 9. Módulo de Sugestões de Otimização
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #f8fafc;'>Sugestões Automáticas de Otimização</h3>", unsafe_allow_html=True)

    insights = generate_insights(df_kpis_alerts)

    for item in insights:
        if item['tipo'] == 'success':
            st.success(f"**{item['titulo']}**\n\n{item['mensagem']}")
        elif item['tipo'] == 'warning':
            st.warning(f"**{item['titulo']}**\n\n{item['mensagem']}")

    # 10. Módulo de Inteligência: Simulador de Orçamento ("E se?")
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #f8fafc;'>Simulador de Inteligência & Orçamento (\"E se?\")</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8;'>Simule o impacto de um investimento extra em uma campanha específica com base na eficiência histórica.</p>", unsafe_allow_html=True)

    sim_col1, sim_col2 = st.columns(2)

    with sim_col1:
        campanhas_disponiveis = df_kpis['campaign_name'].unique()
        campanha_selecionada = st.selectbox("Selecione a Campanha para Simular:", options=campanhas_disponiveis)

    with sim_col2:
        orcamento_extra = st.slider("Orçamento Extra a Injetar (R$):", min_value=100.0, max_value=5000.0, step=100.0, value=1000.0)

    resultado_simulacao = simulate_budget_increase(df_kpis, campanha_selecionada, orcamento_extra)

    if resultado_simulacao:
        st.markdown("<br>", unsafe_allow_html=True)
        res_col1, res_col2, res_col3, res_col4 = st.columns(4)

        with res_col1:
            st.metric(label="Cliques Estimados", value=f"+{resultado_simulacao['novos_clicks']:,}")
        with res_col2:
            st.metric(label="Conversões Estimadas", value=f"+{resultado_simulacao['novas_conversoes']:,}")
        with res_col3:
            st.metric(label="Receita Projetada", value=f"R$ {resultado_simulacao['nova_receita']:,.2f}")
        with res_col4:
            st.metric(label="ROAS Projetado da Ação", value=f"{resultado_simulacao['roas_projetado']}x", delta=f"{resultado_simulacao['roas_projetado']}x")
        
        st.info(f"Conclusão da Simulação: Ao injetar R$ {orcamento_extra:,.2f} extras na campanha *{campanha_selecionada}*, o algoritmo projeta um retorno adicional de R$ {resultado_simulacao['nova_receita']:,.2f}.")
    else:
        st.warning("Não há dados suficientes para calcular a simulação desta campanha.")
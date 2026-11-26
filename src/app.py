import sys
import os

# 0. Garante que o Python encontre a pasta 'src' ANTES de qualquer import do projeto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
    page_title="Otimizador de Anúncios Digital | Growth Intelligence",
    page_icon=":material/bolt:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Biblioteca de Ícones Vetoriais SVG (Estilo Lucide)
ICONS = {
    "bolt": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
    "link": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>',
    "bar_chart": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
    "target": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>',
    "trending_up": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>',
    "arrow_right": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>',
    "calculator": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#34D399" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="2" width="16" height="20" rx="2"/><line x1="8" y1="6" x2="16" y2="6"/><line x1="16" y1="14" x2="16" y2="18"/><path d="M16 10h.01"/><path d="M12 10h.01"/><path d="M8 10h.01"/><path d="M12 14h.01"/><path d="M8 14h.01"/><path d="M12 18h.01"/><path d="M8 18h.01"/></svg>',
    "activity": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#34D399" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
    "pie_chart": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#22D3EE" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.21 15.89A10 10 0 1 1 8 2.83"/><path d="M22 12A10 10 0 0 0 12 2v10z"/></svg>',
    "sparkles": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#34D399" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/></svg>',
    "dot": '<svg width="8" height="8" viewBox="0 0 8 8" fill="#34D399"><circle cx="4" cy="4" r="4"/></svg>'
}

# 2. CSS Customizado (Paleta Obsidian #050507 + Esmeralda #10B981 / #34D399 + Ciano #22D3EE)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Fundo principal obsidian com brilho radial sutil */
    .stApp {
        background-color: #050507;
        background-image: 
            radial-gradient(circle at 50% 0%, rgba(16, 185, 129, 0.14) 0%, transparent 45%),
            radial-gradient(circle at 85% 28%, rgba(6, 182, 212, 0.08) 0%, transparent 40%);
        color: #F8FAFC;
    }

    /* Ocultar barra superior e rodapé padrão do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {background: transparent;}

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #090C12;
        border-right: 1px solid rgba(255, 255, 255, 0.07);
    }

    /* --- SEÇÃO 1: HERO CENTRALIZADO --- */
    .hero-wrapper {
        text-align: center;
        max-width: 880px;
        margin: 10px auto 36px auto;
        padding: 10px 16px;
    }
    .hero-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 7px 18px;
        border-radius: 999px;
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.28);
        color: #34D399;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-bottom: 18px;
    }
    .hero-title {
        font-size: 3.1rem;
        font-weight: 800;
        line-height: 1.12;
        letter-spacing: -0.03em;
        color: #FFFFFF;
        margin-bottom: 18px;
    }
    .hero-title span {
        background: linear-gradient(90deg, #34D399 0%, #22D3EE 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-subtitle {
        font-size: 1.1rem;
        line-height: 1.65;
        color: #94A3B8;
        max-width: 740px;
        margin: 0 auto;
    }

    /* --- SEÇÃO 2: BANNER DESTAQUE ARREDONDADO --- */
    .spotlight-box {
        background: linear-gradient(180deg, rgba(20, 25, 36, 0.92) 0%, rgba(11, 14, 21, 0.96) 100%);
        border: 1px solid rgba(52, 211, 153, 0.28);
        border-radius: 28px;
        padding: 38px 42px;
        text-align: center;
        max-width: 960px;
        margin: 0 auto 54px auto;
        box-shadow: 0 20px 50px -15px rgba(16, 185, 129, 0.16);
    }
    .spotlight-title {
        font-size: 2rem;
        font-weight: 800;
        color: #FFFFFF;
        margin-bottom: 14px;
        letter-spacing: -0.02em;
    }
    .spotlight-title span {
        background: linear-gradient(90deg, #34D399 0%, #22D3EE 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .spotlight-divider {
        height: 1px;
        width: 65%;
        margin: 0 auto 20px auto;
        background: linear-gradient(90deg, transparent, rgba(52, 211, 153, 0.5), rgba(34, 211, 238, 0.5), transparent);
    }
    .spotlight-text {
        font-size: 1rem;
        line-height: 1.7;
        color: #CBD5E1;
        max-width: 780px;
        margin: 0 auto 12px auto;
    }

    /* --- CABEÇALHOS DE SEÇÃO --- */
    .section-eyebrow {
        font-size: 0.78rem;
        font-weight: 700;
        color: #34D399;
        text-transform: uppercase;
        letter-spacing: 0.09em;
        margin-bottom: 6px;
    }
    .section-heading {
        font-size: 2.05rem;
        font-weight: 800;
        line-height: 1.18;
        color: #FFFFFF;
        letter-spacing: -0.02em;
        margin-bottom: 12px;
    }
    .section-heading span {
        background: linear-gradient(90deg, #34D399 0%, #22D3EE 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .section-lead {
        font-size: 0.98rem;
        line-height: 1.65;
        color: #94A3B8;
        margin-bottom: 24px;
    }
    .inline-heading {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 1.15rem;
        font-weight: 700;
        color: #F8FAFC;
        margin-bottom: 4px;
    }

    /* --- CARDS DE PILARES E PÍLULAS DE BENEFÍCIOS --- */
    .feature-grid-2 {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 16px;
    }
    @media (max-width: 900px) {
        .feature-grid-2 { grid-template-columns: 1fr; }
    }
    .feature-item {
        background: rgba(13, 16, 23, 0.9);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 18px;
        padding: 20px;
        display: flex;
        align-items: flex-start;
        gap: 14px;
        transition: all 0.25s ease;
    }
    .feature-item:hover {
        border-color: rgba(52, 211, 153, 0.4);
        transform: translateY(-2px);
    }
    .feature-icon {
        min-width: 44px;
        height: 44px;
        border-radius: 12px;
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: #04130D;
        box-shadow: 0 6px 16px rgba(16, 185, 129, 0.22);
    }
    .feature-title {
        font-size: 0.98rem;
        font-weight: 700;
        color: #F8FAFC;
        margin-bottom: 4px;
    }
    .feature-desc {
        font-size: 0.84rem;
        color: #94A3B8;
        line-height: 1.45;
    }

    /* Pílulas horizontais estilo checklist */
    .benefit-pill {
        background: rgba(13, 16, 23, 0.95);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 15px 18px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 14px;
        transition: border-color 0.2s ease;
    }
    .benefit-pill:hover {
        border-color: rgba(52, 211, 153, 0.45);
    }
    .benefit-arrow {
        min-width: 32px;
        height: 32px;
        border-radius: 50%;
        background: rgba(16, 185, 129, 0.14);
        border: 1px solid rgba(52, 211, 153, 0.25);
        color: #34D399;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .benefit-text {
        font-size: 0.95rem;
        font-weight: 600;
        color: #F8FAFC;
    }

    /* --- DICIONÁRIO DE MÉTRICAS ABERTO (4 CARDS) --- */
    .dict-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 24px;
    }
    @media (max-width: 1000px) {
        .dict-grid { grid-template-columns: repeat(2, 1fr); }
    }
    @media (max-width: 600px) {
        .dict-grid { grid-template-columns: 1fr; }
    }
    .dict-card {
        background: linear-gradient(180deg, rgba(20, 25, 36, 0.92) 0%, rgba(11, 14, 21, 0.96) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 22px;
        transition: border-color 0.2s ease;
    }
    .dict-card:hover {
        border-color: rgba(52, 211, 153, 0.4);
    }
    .dict-tag {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 8px;
        background: rgba(16, 185, 129, 0.12);
        color: #34D399;
        font-size: 0.78rem;
        font-weight: 800;
        margin-bottom: 10px;
    }
    .dict-name {
        font-size: 0.95rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 8px;
    }
    .dict-body {
        font-size: 0.85rem;
        color: #94A3B8;
        line-height: 1.55;
    }

    /* --- CARDS DE KPI DO DASHBOARD --- */
    .kpi-card {
        background: linear-gradient(180deg, rgba(20, 25, 36, 0.92) 0%, rgba(11, 14, 21, 0.96) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 18px;
        padding: 22px 24px;
        position: relative;
        overflow: hidden;
        transition: all 0.25s ease;
    }
    .kpi-card::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(52, 211, 153, 0.45), transparent);
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        border-color: rgba(52, 211, 153, 0.4);
        box-shadow: 0 12px 30px -10px rgba(16, 185, 129, 0.2);
    }
    .kpi-title {
        font-size: 0.78rem;
        font-weight: 600;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        margin-bottom: 10px;
    }
    .kpi-value {
        font-size: 1.95rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: #FFFFFF;
    }
    .kpi-sub {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 0.8rem;
        color: #34D399;
        margin-top: 6px;
        font-weight: 500;
    }

    /* Box de resumo da simulação sem emoji */
    .summary-callout {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        background: rgba(16, 185, 129, 0.08);
        border: 1px solid rgba(52, 211, 153, 0.28);
        border-radius: 14px;
        padding: 16px 20px;
        color: #E2E8F0;
        font-size: 0.92rem;
        line-height: 1.55;
        margin-top: 12px;
    }

    /* Botão principal na Sidebar e Download */
    div.stButton > button, div.stDownloadButton > button {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: #04130D;
        font-weight: 700;
        border: none;
        border-radius: 12px;
        padding: 0.65rem 1rem;
        transition: all 0.2s ease;
    }
    div.stButton > button:hover, div.stDownloadButton > button:hover {
        background: linear-gradient(135deg, #34D399 0%, #10B981 100%);
        color: #04130D;
        box-shadow: 0 0 20px rgba(16, 185, 129, 0.35);
    }

    .divider-glow {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
        margin: 48px 0;
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# SEÇÃO 1: HERO DE APRESENTAÇÃO
# ==============================================================================
st.markdown(f"""
    <div class="hero-wrapper">
        <div class="hero-pill">{ICONS['bolt']} Inteligência de Performance & Tráfego Pago</div>
        <div class="hero-title">Nós não apenas monitoramos mídia.<br><span>Nós otimizamos lucro.</span></div>
        <div class="hero-subtitle">
            O <strong>Otimizador de Anúncios Digital</strong> centraliza campanhas de Google Ads e Meta Ads, 
            diagnostica gargalos automaticamente e simula cenários de escala antes de você investir mais verba.
        </div>
    </div>
""", unsafe_allow_html=True)

# ==============================================================================
# SEÇÃO 2: BLOCO DESTAQUE DO PROBLEMA & SOLUÇÃO
# ==============================================================================
st.markdown("""
    <div class="spotlight-box">
        <div class="spotlight-title">Você quer <span>escalar suas campanhas</span> com previsibilidade?</div>
        <div class="spotlight-divider"></div>
        <div class="spotlight-text">
            Gestores de tráfego frequentemente analisam plataformas de anúncios de forma isolada em planilhas manuais, 
            o que dificulta comparar onde cada real investido gera maior retorno financeiro.
        </div>
        <div class="spotlight-text">
            Nossa plataforma unifica dados brutos de mídia paga, classifica a saúde de cada campanha em tempo real 
            e apoia decisões estratégicas de realocação de orçamento.
        </div>
    </div>
""", unsafe_allow_html=True)

# ==============================================================================
# SEÇÃO 3: COMO A FERRAMENTA FUNCIONA & O QUE ENTREGAMOS
# ==============================================================================
col_left, col_right = st.columns([1.35, 1], gap="large")

with col_left:
    st.markdown('<div class="section-eyebrow">Arquitetura & Metodologia</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Como funciona o <span>Otimizador Digital?</span></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-lead">'
        'Unimos ingestão automatizada de dados, cálculo padronizado de indicadores e um motor '
        'de regras inteligente para transformar métricas dispersas em ações práticas.'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(f"""
        <div class="feature-grid-2">
            <div class="feature-item">
                <div class="feature-icon">{ICONS['link']}</div>
                <div>
                    <div class="feature-title">Integração Multi-Canal</div>
                    <div class="feature-desc">Consolida Google Ads e Meta Ads em um único banco analítico padronizado.</div>
                </div>
            </div>
            <div class="feature-item">
                <div class="feature-icon">{ICONS['bar_chart']}</div>
                <div>
                    <div class="feature-title">Cálculo Automático de KPIs</div>
                    <div class="feature-desc">Processa ROAS, CTR, CPC e CPA sem risco de erro humano em planilhas.</div>
                </div>
            </div>
            <div class="feature-item">
                <div class="feature-icon">{ICONS['target']}</div>
                <div>
                    <div class="feature-title">Engine de Diagnóstico</div>
                    <div class="feature-desc">Identifica campanhas prontas para escala e sinaliza alertas de desperdício.</div>
                </div>
            </div>
            <div class="feature-item">
                <div class="feature-icon">{ICONS['trending_up']}</div>
                <div>
                    <div class="feature-title">Simulador Preditivo</div>
                    <div class="feature-desc">Projeta cliques, conversões e receita antes de injetar verba extra.</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="section-eyebrow">Veja o que entregamos</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Decisões reais, com <span>dados expressivos.</span></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-lead">'
        'Interaja com a calculadora abaixo, explore os gráficos dinâmicos por métrica '
        'e teste cenários no simulador preditivo.'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(f"""
        <div class="benefit-pill">
            <div class="benefit-arrow">{ICONS['arrow_right']}</div>
            <div class="benefit-text">Consolidação instantânea entre canais de aquisição</div>
        </div>
        <div class="benefit-pill">
            <div class="benefit-arrow">{ICONS['arrow_right']}</div>
            <div class="benefit-text">ROAS consistente com alertas automáticos de saúde</div>
        </div>
        <div class="benefit-pill">
            <div class="benefit-arrow">{ICONS['arrow_right']}</div>
            <div class="benefit-text">Crescimento sustentável com simulação de orçamento</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="divider-glow"></div>', unsafe_allow_html=True)

# ==============================================================================
# SEÇÃO 4: GUIA ABERTO DE INDICADORES + CALCULADORA INTERATIVA DE KPIs
# ==============================================================================
st.markdown('<div class="section-eyebrow">Glossário & Laboratório Prático</div>', unsafe_allow_html=True)
st.markdown('<div class="section-heading">Entenda e teste os <span>indicadores analisados</span></div>', unsafe_allow_html=True)
st.markdown('<div class="section-lead">Todos os gráficos e recomendações do sistema são calculados a partir destes quatro pilares fundamentais:</div>', unsafe_allow_html=True)

st.markdown("""
    <div class="dict-grid">
        <div class="dict-card">
            <div class="dict-tag">ROAS</div>
            <div class="dict-name">Return on Ad Spend</div>
            <div class="dict-body">
                Receita gerada dividida pelo investimento. Um ROAS de <strong>3.50x</strong> indica que cada <strong>R$ 1,00</strong> investido retornou <strong>R$ 3,50</strong> em vendas.
            </div>
        </div>
        <div class="dict-card">
            <div class="dict-tag" style="color: #22D3EE; background: rgba(6, 182, 212, 0.12);">CTR</div>
            <div class="dict-name">Click-Through Rate</div>
            <div class="dict-body">
                Percentual de usuários que clicaram no anúncio após visualizá-lo. Mede a atratividade criativa e a relevância da segmentação.
            </div>
        </div>
        <div class="dict-card">
            <div class="dict-tag">CPC</div>
            <div class="dict-name">Custo por Clique</div>
            <div class="dict-body">
                Valor médio pago por cada clique recebido na campanha. Essencial para avaliar a competitividade e eficiência do leilão de mídia.
            </div>
        </div>
        <div class="dict-card">
            <div class="dict-tag" style="color: #22D3EE; background: rgba(6, 182, 212, 0.12);">CPA</div>
            <div class="dict-name">Custo por Aquisição</div>
            <div class="dict-body">
                Investimento médio necessário para gerar uma conversão (lead ou venda). Determina a sustentabilidade financeira da operação.
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Calculadora Interativa de KPIs
with st.container(border=True):
    st.markdown(f'<div class="inline-heading">{ICONS["calculator"]} Calculadora Interativa de KPIs (Teste na Prática)</div>', unsafe_allow_html=True)
    st.caption("Altere os valores abaixo para ver como o algoritmo calcula os indicadores em tempo real:")
    c_imp, c_cli, c_inv, c_conv, c_rec = st.columns(5)
    with c_imp:
        calc_imp = st.number_input("Impressões", min_value=100, value=10000, step=500)
    with c_cli:
        calc_cli = st.number_input("Cliques", min_value=1, value=350, step=10)
    with c_inv:
        calc_inv = st.number_input("Investimento (R$)", min_value=10.0, value=500.0, step=50.0)
    with c_conv:
        calc_conv = st.number_input("Conversões", min_value=1, value=25, step=1)
    with c_rec:
        calc_rec = st.number_input("Receita (R$)", min_value=0.0, value=2250.0, step=100.0)

    res_roas = round(calc_rec / calc_inv, 2) if calc_inv > 0 else 0
    res_ctr = round((calc_cli / calc_imp) * 100, 2) if calc_imp > 0 else 0
    res_cpc = round(calc_inv / calc_cli, 2) if calc_cli > 0 else 0
    res_cpa = round(calc_inv / calc_conv, 2) if calc_conv > 0 else 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("ROAS Calculado", f"{res_roas}x", "Saudável" if res_roas >= 3 else "Atenção")
    m2.metric("CTR Calculado", f"{res_ctr}%")
    m3.metric("CPC Médio", f"R$ {res_cpc:.2f}")
    m4.metric("CPA Médio", f"R$ {res_cpa:.2f}")

st.markdown('<div class="divider-glow"></div>', unsafe_allow_html=True)

# ==============================================================================
# SEÇÃO 5: PAINEL INTERATIVO & DADOS EM TEMPO REAL
# ==============================================================================
st.markdown('<div class="section-eyebrow">Ambiente Analítico Interativo</div>', unsafe_allow_html=True)
st.markdown('<div class="section-heading">Resultados consolidados <span>em tempo real</span></div>', unsafe_allow_html=True)
st.markdown('<div class="section-lead">Utilize os filtros na barra lateral para segmentar por plataforma, campanha ou período de veiculação.</div>', unsafe_allow_html=True)

df_raw = load_raw_data()

if df_raw.empty:
    st.error("Nenhum dado encontrado no banco de dados SQLite.")
else:
    df_raw['date'] = pd.to_datetime(df_raw['date'])

    # Barra Lateral (Filtros Avançados)
    st.sidebar.markdown("### Painel de Controle")
    st.sidebar.caption("Sincronize as APIs e filtre os dados exibidos na página.")

    if st.sidebar.button("Sincronizar / Ingerir Dados", use_container_width=True):
        with st.spinner("Conectando às APIs e atualizando o banco..."):
            success = run_ingestion()
            if success:
                st.sidebar.success("Dados atualizados com sucesso!")
                st.rerun()

    st.sidebar.markdown("---")

    platforms = st.sidebar.multiselect(
        "Plataformas de Mídia:",
        options=df_raw['platform'].unique(),
        default=df_raw['platform'].unique()
    )

    campaigns_filter = st.sidebar.multiselect(
        "Campanhas Específicas (Opcional):",
        options=df_raw[df_raw['platform'].isin(platforms)]['campaign_name'].unique(),
        default=df_raw[df_raw['platform'].isin(platforms)]['campaign_name'].unique()
    )

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
            (df_raw['campaign_name'].isin(campaigns_filter)) &
            (df_raw['date'].dt.date >= start_date) &
            (df_raw['date'].dt.date <= end_date)
        ]
    else:
        df_filtered = df_raw[
            (df_raw['platform'].isin(platforms)) &
            (df_raw['campaign_name'].isin(campaigns_filter))
        ]

    if df_filtered.empty:
        st.warning("Nenhum registro encontrado para os filtros selecionados. Ajuste os filtros na barra lateral.")
        st.stop()

    df_kpis = calculate_kpis(df_filtered)
    df_kpis_alerts = add_performance_alerts(df_kpis)

    # Cards de KPIs Gerais
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
                <div class="kpi-sub">{ICONS['dot']} Verba consumida no período</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Receita Gerada</div>
                <div class="kpi-value">R$ {total_revenue:,.2f}</div>
                <div class="kpi-sub">{ICONS['dot']} Retorno bruto atribuído</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">ROAS Geral</div>
                <div class="kpi-value" style="color: #34D399;">{global_roas}x</div>
                <div class="kpi-sub">{ICONS['dot']} Retorno sobre investimento</div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">CTR Médio</div>
                <div class="kpi-value" style="color: #22D3EE;">{global_ctr}%</div>
                <div class="kpi-sub">{ICONS['dot']} Taxa média de cliques</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # --- GRÁFICO INTERATIVO COM SELETOR DINÂMICO DE MÉTRICA ---
    with st.container(border=True):
        g_header1, g_header2 = st.columns([2, 1])
        with g_header1:
            st.markdown("### Análise Visual Comparativa por Campanha")
            st.caption("Escolha qual métrica deseja comparar entre as campanhas ativas.")
        with g_header2:
            metrica_escolhida = st.selectbox(
                "Métrica do Gráfico:",
                options=["ROAS", "revenue", "cost", "CTR (%)", "CPA (R$)"],
                format_func=lambda x: {
                    "ROAS": "ROAS (Retorno sobre Investimento)",
                    "revenue": "Receita Gerada (R$)",
                    "cost": "Investimento Consumido (R$)",
                    "CTR (%)": "CTR (%)",
                    "CPA (R$)": "CPA - Custo por Aquisição (R$)"
                }[x]
            )

        formato_texto = '%{text:.2f}x' if metrica_escolhida == 'ROAS' else ('%{text:.2f}%' if metrica_escolhida == 'CTR (%)' else 'R$ %{text:,.2f}')

        fig = px.bar(
            df_kpis,
            x='campaign_name',
            y=metrica_escolhida,
            color='platform',
            text=metrica_escolhida,
            color_discrete_map={'Google Ads': '#10B981', 'Meta Ads': '#22D3EE'},
            labels={'campaign_name': 'Campanha', metrica_escolhida: metrica_escolhida, 'platform': 'Plataforma'}
        )

        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Plus Jakarta Sans', color='#94A3B8'),
            xaxis=dict(showgrid=False, color='#94A3B8', title=''),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.06)', color='#94A3B8'),
            legend=dict(title_text='', orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            margin=dict(l=10, r=10, t=35, b=10),
            bargap=0.35
        )
        fig.update_traces(
            texttemplate=formato_texto,
            textposition='outside',
            marker_line_width=0
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- GRÁFICOS INTERATIVOS: EVOLUÇÃO DIÁRIA + DISTRIBUIÇÃO POR CANAL ---
    chart_col1, chart_col2 = st.columns([1.6, 1], gap="medium")

    with chart_col1:
        with st.container(border=True):
            st.markdown(f'<div class="inline-heading">{ICONS["activity"]} Evolução Diária: Investimento vs. Receita</div>', unsafe_allow_html=True)
            st.caption("Acompanhe a tendência diária do retorno financeiro ao longo do período filtrado.")

            df_daily = df_filtered.groupby('date', as_index=False)[['cost', 'revenue']].sum()
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(
                x=df_daily['date'], y=df_daily['revenue'],
                mode='lines+markers', name='Receita (R$)',
                line=dict(color='#34D399', width=3),
                fill='tozeroy', fillcolor='rgba(52, 211, 153, 0.08)'
            ))
            fig_line.add_trace(go.Scatter(
                x=df_daily['date'], y=df_daily['cost'],
                mode='lines+markers', name='Investimento (R$)',
                line=dict(color='#22D3EE', width=2.5, dash='dot')
            ))
            fig_line.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Plus Jakarta Sans', color='#94A3B8'),
                xaxis=dict(showgrid=False, color='#94A3B8'),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.06)', color='#94A3B8'),
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                margin=dict(l=10, r=10, t=30, b=10),
                height=340
            )
            st.plotly_chart(fig_line, use_container_width=True)

    with chart_col2:
        with st.container(border=True):
            st.markdown(f'<div class="inline-heading">{ICONS["pie_chart"]} Share de Receita por Canal</div>', unsafe_allow_html=True)
            st.caption("Participação percentual de cada plataforma na receita total.")

            df_share = df_filtered.groupby('platform', as_index=False)['revenue'].sum()
            fig_donut = px.pie(
                df_share,
                values='revenue',
                names='platform',
                hole=0.62,
                color='platform',
                color_discrete_map={'Google Ads': '#10B981', 'Meta Ads': '#22D3EE'}
            )
            fig_donut.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Plus Jakarta Sans', color='#94A3B8'),
                legend=dict(orientation='h', yanchor='bottom', y=-0.1, xanchor='center', x=0.5),
                margin=dict(l=10, r=10, t=30, b=20),
                height=340
            )
            fig_donut.update_traces(textinfo='percent+label', textfont_color='#FFFFFF')
            st.plotly_chart(fig_donut, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Recomendações Automáticas
    st.markdown("### Sugestões Automáticas de Otimização")
    st.caption("Diagnósticos gerados pelo motor de regras com base na eficiência histórica de cada campanha.")

    insights = generate_insights(df_kpis_alerts)

    for item in insights:
        if item['tipo'] == 'success':
            st.success(f"**{item['titulo']}** — {item['mensagem']}")
        elif item['tipo'] == 'warning':
            st.warning(f"**{item['titulo']}** — {item['mensagem']}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Tabela Consolidada Interativa + Exportação CSV
    with st.container(border=True):
        t_col1, t_col2, t_col3 = st.columns([2, 1.2, 0.8])
        with t_col1:
            st.markdown("### Detalhamento Consolidado com Status")
            st.caption("Filtre por status de saúde ou exporte o relatório completo em planilha.")
        with t_col2:
            status_disponiveis = ["Todos"] + list(df_kpis_alerts['Status'].unique())
            filtro_status = st.selectbox("Filtrar por Status:", options=status_disponiveis)

        cols_order = ['platform', 'campaign_name', 'Status', 'impressions', 'clicks', 'cost', 'conversions', 'revenue', 'CTR (%)', 'CPC (R$)', 'CPA (R$)', 'ROAS']
        df_table_view = df_kpis_alerts[cols_order]

        if filtro_status != "Todos":
            df_table_view = df_table_view[df_table_view['Status'] == filtro_status]

        with t_col3:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            csv_data = df_table_view.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Exportar CSV",
                data=csv_data,
                file_name="relatorio_otimizador_anuncios.csv",
                mime="text/csv",
                use_container_width=True
            )

        st.dataframe(
            df_table_view.style.format({
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
            use_container_width=True,
            hide_index=True
        )

    st.markdown('<div class="divider-glow"></div>', unsafe_allow_html=True)

    # ==========================================================================
    # SEÇÃO 6: SIMULADOR INTERATIVO MULTI-CENÁRIO ("E SE?")
    # ==========================================================================
    st.markdown('<div class="section-eyebrow">Projeção Preditiva</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Simulador de Inteligência & <span>Escala ("E se?")</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-lead">Ajuste a campanha, o aporte extra e o cenário de mercado para visualizar o impacto financeiro antes vs. depois.</div>', unsafe_allow_html=True)

    with st.container(border=True):
        sim_col1, sim_col2, sim_col3 = st.columns([1.2, 1.3, 1])

        with sim_col1:
            campanhas_disponiveis = df_kpis['campaign_name'].unique()
            campanha_selecionada = st.selectbox("Selecione a Campanha para Simular:", options=campanhas_disponiveis)

        with sim_col2:
            orcamento_extra = st.slider("Orçamento Extra a Injetar (R$):", min_value=100.0, max_value=10000.0, step=100.0, value=1500.0)

        with sim_col3:
            cenario = st.radio(
                "Cenário de Eficiência:",
                options=["Conservador (-15%)", "Realista (Histórico)", "Otimista (+15%)"],
                index=1
            )

        fator_cenario = 0.85 if "Conservador" in cenario else (1.15 if "Otimista" in cenario else 1.0)
        resultado_simulacao = simulate_budget_increase(df_kpis, campanha_selecionada, orcamento_extra)

        if resultado_simulacao:
            novos_clicks_adj = int(round(resultado_simulacao['novos_clicks'] * fator_cenario))
            novas_conv_adj = int(round(resultado_simulacao['novas_conversoes'] * fator_cenario))
            nova_receita_adj = round(resultado_simulacao['nova_receita'] * fator_cenario, 2)
            roas_proj_adj = round(resultado_simulacao['roas_projetado'] * fator_cenario, 2)

            st.markdown("<br>", unsafe_allow_html=True)
            res_col1, res_col2, res_col3, res_col4 = st.columns(4)

            with res_col1:
                st.markdown(f"""
                    <div class="kpi-card">
                        <div class="kpi-title">Cliques Estimados</div>
                        <div class="kpi-value">+{novos_clicks_adj:,}</div>
                        <div class="kpi-sub">Tráfego incremental</div>
                    </div>
                """, unsafe_allow_html=True)

            with res_col2:
                st.markdown(f"""
                    <div class="kpi-card">
                        <div class="kpi-title">Conversões Estimadas</div>
                        <div class="kpi-value">+{novas_conv_adj:,}</div>
                        <div class="kpi-sub">Leads / Vendas extras</div>
                    </div>
                """, unsafe_allow_html=True)

            with res_col3:
                st.markdown(f"""
                    <div class="kpi-card">
                        <div class="kpi-title">Receita Projetada</div>
                        <div class="kpi-value" style="color: #34D399;">R$ {nova_receita_adj:,.2f}</div>
                        <div class="kpi-sub">Retorno adicional estimado</div>
                    </div>
                """, unsafe_allow_html=True)

            with res_col4:
                st.markdown(f"""
                    <div class="kpi-card">
                        <div class="kpi-title">ROAS Projetado</div>
                        <div class="kpi-value" style="color: #22D3EE;">{roas_proj_adj}x</div>
                        <div class="kpi-sub">Cenário {cenario.split()[0]}</div>
                    </div>
                """, unsafe_allow_html=True)

            # Gráfico comparativo Antes vs. Depois da Escala
            camp_atual = df_kpis[df_kpis['campaign_name'] == campanha_selecionada].iloc[0]
            custo_atual = float(camp_atual['cost'])
            receita_atual = float(camp_atual['revenue'])

            df_comp = pd.DataFrame({
                "Momento": ["Cenário Atual", "Após Escala Projetada", "Cenário Atual", "Após Escala Projetada"],
                "Indicador": ["Investimento", "Investimento", "Receita", "Receita"],
                "Valor (R$)": [custo_atual, custo_atual + orcamento_extra, receita_atual, receita_atual + nova_receita_adj]
            })

            fig_sim = px.bar(
                df_comp,
                x="Momento",
                y="Valor (R$)",
                color="Indicador",
                barmode="group",
                text="Valor (R$)",
                color_discrete_map={"Investimento": "#22D3EE", "Receita": "#10B981"}
            )
            fig_sim.update_layout(
                title=f"Comparativo de Escala: {campanha_selecionada}",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Plus Jakarta Sans', color='#94A3B8'),
                xaxis=dict(showgrid=False, title=''),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.06)'),
                legend=dict(title_text='', orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                margin=dict(l=10, r=10, t=45, b=10),
                height=310
            )
            fig_sim.update_traces(texttemplate='R$ %{text:,.2f}', textposition='outside')
            st.plotly_chart(fig_sim, use_container_width=True)

            st.markdown(f"""
                <div class="summary-callout">
                    <div style="margin-top: 2px;">{ICONS['sparkles']}</div>
                    <div>
                        <strong>Resumo da Projeção ({cenario}):</strong> Ao injetar <strong>R$ {orcamento_extra:,.2f}</strong> extras na campanha 
                        <strong>{campanha_selecionada}</strong>, o modelo estima um retorno adicional de <strong>R$ {nova_receita_adj:,.2f}</strong> 
                        (elevando a receita total da campanha para <strong>R$ {receita_atual + nova_receita_adj:,.2f}</strong>).
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Não há dados suficientes para calcular a simulação desta campanha.")
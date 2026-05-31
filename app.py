import streamlit as st
from datetime import date

from data import fetch_petr4_data, validate_data, get_current_price
from analysis import (
    calc_linear_target,
    calc_sma,
    calc_bollinger_bands,
    calc_metrics,
)
from charts import build_main_chart, build_volume_chart, build_returns_histogram

st.set_page_config(
    page_title="PETR4 Analyzer 2026",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Sidebar ----------
st.sidebar.header("Configurações")

projection_days = st.sidebar.slider("Dias de projeção (dias úteis)", 10, 90, 30)

analyst_target_input = st.sidebar.number_input(
    "Preço alvo de analistas (R$)",
    min_value=0.0,
    value=0.0,
    step=0.50,
    format="%.2f",
    help="Informe manualmente o consenso de analistas obtido em fontes como Infomoney, Status Invest ou XP Research.",
)
analyst_target = analyst_target_input if analyst_target_input > 0 else None

show_bollinger = st.sidebar.checkbox("Mostrar Bandas de Bollinger", value=False)
show_volume = st.sidebar.checkbox("Mostrar gráfico de volume", value=True)

st.sidebar.divider()
st.sidebar.info(
    "**Fonte:** Yahoo Finance (yfinance)  \n"
    "Dados históricos com delay de ~24h."
)
st.sidebar.warning(
    "Preço alvo técnico é uma projeção de tendência linear, "
    "**não** uma recomendação de investimento."
)

# ---------- Cabeçalho ----------
st.title("PETR4.SA — Análise Petrobras 2026")
hoje = date.today()
st.caption(f"Dados de 01/01/2026 até {hoje.strftime('%d/%m/%Y')} • Atualizado a cada hora")

# ---------- Download de dados ----------
with st.spinner("Carregando dados do Yahoo Finance..."):
    df, erro = fetch_petr4_data("2026-01-01", hoje.isoformat())

ok, msg_val = validate_data(df)
if not ok:
    st.error(f"Não foi possível carregar os dados: {erro or msg_val}")
    st.stop()

# ---------- Cálculos ----------
linear = calc_linear_target(df, projection_days)
sma20 = calc_sma(df, 20)
sma50 = calc_sma(df, 50)
bb_upper, bb_lower = calc_bollinger_bands(df)

displayed_target = analyst_target if analyst_target else linear["target_price"]
metrics = calc_metrics(df, displayed_target)

# ---------- Métricas ----------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Preço Atual", f"R$ {metrics['current_price']:.2f}")
col2.metric(
    "Preço Alvo" + (" (analistas)" if analyst_target else " (técnico)"),
    f"R$ {metrics['target_price']:.2f}",
    delta=f"{metrics['upside_pct']:+.1f}%",
)
col3.metric("Volatilidade Anual", f"{metrics['volatility_annual']:.1f}%")
col4.metric("Volume Médio 30d", f"{metrics['avg_volume_30d'] / 1e6:.1f}M")

st.divider()

# ---------- Gráfico principal ----------
fig_main = build_main_chart(
    df=df,
    regression_series=linear["regression_series"],
    target_price=linear["target_price"],
    target_date=linear["target_date"],
    analyst_target=analyst_target,
    show_bollinger=show_bollinger,
    bb_upper=bb_upper,
    bb_lower=bb_lower,
    sma20=sma20,
    sma50=sma50,
)
st.plotly_chart(fig_main, use_container_width=True)

# ---------- Gráfico de volume ----------
if show_volume:
    st.plotly_chart(build_volume_chart(df), use_container_width=True)

# ---------- Dados detalhados ----------
with st.expander("Ver dados detalhados e estatísticas"):
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.subheader("Últimos 30 pregões")
        display_df = df[["date", "open", "high", "low", "close", "volume"]].tail(30).copy()
        display_df["date"] = display_df["date"].dt.strftime("%d/%m/%Y")
        display_df = display_df.rename(columns={
            "date": "Data", "open": "Abertura", "high": "Máxima",
            "low": "Mínima", "close": "Fechamento", "volume": "Volume",
        })
        st.dataframe(
            display_df.style.format({
                "Abertura": "R$ {:.2f}", "Máxima": "R$ {:.2f}",
                "Mínima": "R$ {:.2f}", "Fechamento": "R$ {:.2f}",
                "Volume": "{:,.0f}",
            }),
            use_container_width=True,
            hide_index=True,
        )
    with col_b:
        st.plotly_chart(build_returns_histogram(df), use_container_width=True)

# ---------- Metodologia ----------
with st.expander("Metodologia do Preço Alvo Técnico"):
    st.markdown(f"""
**Regressão Linear Simples sobre Preços de Fechamento**

- **Período analisado:** 01/01/2026 até {hoje.strftime('%d/%m/%Y')} ({len(df)} pregões)
- **R² do ajuste:** `{linear['r2']:.3f}` — quanto mais próximo de 1.0, mais linear foi a tendência
- **Inclinação:** `R$ {linear['slope_brl_per_day']:.4f} / dia útil`
  {'(tendência de alta)' if linear['slope_brl_per_day'] > 0 else '(tendência de baixa)'}
- **Projeção:** {projection_days} dias úteis além do último pregão disponível → **{linear['target_date'].strftime('%d/%m/%Y')}**

---

**Limitações importantes:**
- Este modelo assume continuidade da tendência linear recente.
- PETR4 é sensível ao preço do petróleo Brent, política de dividendos da Petrobras e cenário macroeconômico brasileiro — nenhum desses fatores está incorporado neste modelo.
- R² baixo (< 0,5) indica que os preços não seguiram tendência linear consistente no período, reduzindo a confiabilidade da projeção.
- **Esta análise não constitui recomendação de investimento.** Para preço alvo fundamentalista, consulte relatórios de analistas certificados.
""")

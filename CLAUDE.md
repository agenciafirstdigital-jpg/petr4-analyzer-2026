# PETR4 Analyzer 2026

App web em Python que exibe a cotação histórica da PETR4 (Petrobras/B3) durante 2026 com gráfico interativo e projeção de preço alvo via regressão linear.

## Como rodar

```powershell
# Ativar ambiente virtual
.\.venv\Scripts\Activate.ps1

# Iniciar o app
streamlit run app.py
# Acesse: http://localhost:8501
```

Python instalado em: `C:\Users\Felipe\AppData\Local\Programs\Python\Python314\`  
Venv em: `.venv\` (criado com Python 3.14.5)

## Estrutura

```
.
├── app.py          # Entrypoint Streamlit — UI, sidebar, orquestração
├── data.py         # Download e cache de dados via yfinance
├── analysis.py     # Cálculos: regressão linear, médias móveis, métricas
├── charts.py       # Figuras Plotly (candlestick, volume, histograma)
└── requirements.txt
```

## Stack

| Lib | Versão | Papel |
|---|---|---|
| streamlit | 1.58.0 | Framework web |
| yfinance | 1.4.1 | Dados históricos (ticker: `PETR4.SA`) |
| plotly | 6.7.0 | Gráficos interativos |
| pandas | 3.0.3 | Manipulação de dados |
| numpy | 2.4.6 | Cálculos numéricos |
| scikit-learn | 1.8.0 | Regressão linear (`LinearRegression`) |

## Fonte de dados

- **Ticker:** `PETR4.SA` no Yahoo Finance via `yfinance.download()`
- **Período:** `2026-01-01` até `date.today()`
- **`auto_adjust=True`:** aplica ajuste de splits e dividendos automaticamente
- **Cache:** `@st.cache_data(ttl=3600)` — re-baixa uma vez por hora
- yfinance retorna MultiIndex para um único ticker; `data.py` faz o flatten antes de usar

## Módulos

### `data.py`
- `fetch_petr4_data(start, end)` → `(DataFrame, str_erro)` — download com tratamento de exceção
- `get_current_price(df)` → `float` — último fechamento
- `validate_data(df)` → `(bool, str)` — exige mínimo de 20 pregões

### `analysis.py`
- `calc_linear_target(df, projection_days)` → `dict` com `target_price`, `target_date`, `r2`, `slope_brl_per_day`, `regression_series`
- `calc_sma(df, window)` → `pd.Series` — média móvel simples
- `calc_ema(df, window)` → `pd.Series` — média móvel exponencial
- `calc_bollinger_bands(df, window=20, std_mult=2.0)` → `(upper, lower)`
- `calc_metrics(df, target_price)` → `dict` com `current_price`, `upside_pct`, `volatility_annual` (anualizada: std × √252 × 100), `avg_volume_30d`, `max_2026`, `min_2026`

### `charts.py`
- `build_main_chart(...)` → `go.Figure` — candlestick + SMA20/50 + regressão + projeção + alvo analistas
- `build_volume_chart(df)` → `go.Figure` — barras verde/vermelho, altura 150px
- `build_returns_histogram(df)` → `go.Figure` — histograma de retornos diários, altura 300px

### `app.py`
Fluxo de execução (Streamlit re-executa tudo a cada interação do usuário):
1. Sidebar: slider de projeção (10–90 dias úteis), `number_input` para alvo de analistas, checkboxes de Bollinger e volume
2. Download com `st.spinner`
3. Cálculos em `analysis.py`
4. 4 métricas: Preço Atual | Preço Alvo | Volatilidade Anual | Volume Médio 30d
5. Gráfico principal → volume (condicional) → expander com tabela + histograma → expander com metodologia

## Preço alvo — decisões de design

**Por que não usar `yfinance.info['targetMeanPrice']`:** retorna o alvo do ADR americano (PBR) em USD, não corresponde à PETR4.SA em BRL.

**Abordagem atual:**
- **Alvo técnico (padrão):** regressão linear sobre os fechamentos do ano, projetada `N` dias úteis à frente. Exibe R² como indicador de confiabilidade.
- **Alvo de analistas (manual):** usuário digita na sidebar o consenso obtido em Infomoney, Status Invest ou XP Research. Quando preenchido, substitui o alvo técnico nas métricas e adiciona linha verde horizontal no gráfico.

## Gráfico principal — camadas

| Camada | Cor | Condição |
|---|---|---|
| Bandas de Bollinger (envelope) | cinza transparente | checkbox ativado |
| Candlestick OHLC | verde #26a69a / vermelho #ef5350 | sempre |
| SMA20 | azul #42A5F5 | sempre |
| SMA50 | roxo #AB47BC | sempre |
| Linha de regressão (histórico) | laranja tracejado #FF9800 | sempre |
| Projeção futura | laranja pontilhado #FF9800 | sempre |
| Marcador alvo técnico | estrela dourada #FFD700 | sempre |
| Linha alvo analistas | verde horizontal #4CAF50 | se preenchido |
| Anotações máx/mín do ano | verde/vermelho | sempre |

Layout: `template='plotly_dark'`, `height=600`, `hovermode='x unified'`, sem rangeslider.

## Decisões importantes

- **Sem banco de dados:** dados re-baixados em runtime; janela de ~100 linhas é trivial para pandas em memória.
- **Dois gráficos separados** (principal + volume): Streamlit não suporta bem `make_subplots` com `go.Candlestick`, dois `st.plotly_chart` com `use_container_width=True` dão o mesmo efeito visual.
- **`auto_adjust=True` obrigatório** para PETR4: a ação paga dividendos frequentes e sem ajuste os preços históricos aparecem com gaps artificiais.
- **Disclaimer legal** exibido na sidebar e no expander de metodologia — o app não é recomendação de investimento.

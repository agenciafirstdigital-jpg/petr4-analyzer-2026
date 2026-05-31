import pandas as pd
import plotly.graph_objects as go


def build_main_chart(
    df: pd.DataFrame,
    regression_series: pd.Series,
    target_price: float,
    target_date: pd.Timestamp,
    analyst_target: float | None,
    show_bollinger: bool,
    bb_upper: pd.Series,
    bb_lower: pd.Series,
    sma20: pd.Series,
    sma50: pd.Series,
) -> go.Figure:
    fig = go.Figure()

    if show_bollinger:
        fig.add_trace(go.Scatter(
            x=df["date"], y=bb_upper,
            line=dict(color="rgba(150,150,150,0.3)", width=1),
            name="BB Superior", showlegend=True,
        ))
        fig.add_trace(go.Scatter(
            x=df["date"], y=bb_lower,
            line=dict(color="rgba(150,150,150,0.3)", width=1),
            fill="tonexty", fillcolor="rgba(150,150,150,0.08)",
            name="BB Inferior", showlegend=True,
        ))

    fig.add_trace(go.Candlestick(
        x=df["date"],
        open=df["open"], high=df["high"],
        low=df["low"], close=df["close"],
        increasing_line_color="#26a69a",
        decreasing_line_color="#ef5350",
        name="PETR4.SA",
    ))

    fig.add_trace(go.Scatter(
        x=df["date"], y=sma20,
        line=dict(color="#42A5F5", width=1),
        name="SMA20",
    ))
    fig.add_trace(go.Scatter(
        x=df["date"], y=sma50,
        line=dict(color="#AB47BC", width=1),
        name="SMA50",
    ))

    fig.add_trace(go.Scatter(
        x=df["date"], y=regression_series,
        line=dict(color="#FF9800", width=1.5, dash="dash"),
        name="Tendência (Reg. Linear)",
    ))

    last_date = df["date"].iloc[-1]
    last_reg_val = float(regression_series.iloc[-1])
    fig.add_trace(go.Scatter(
        x=[last_date, target_date],
        y=[last_reg_val, target_price],
        line=dict(color="#FF9800", width=1.5, dash="dot"),
        mode="lines+markers",
        marker=dict(size=[0, 12], symbol=["circle", "star"], color="#FFD700"),
        name=f"Alvo Técnico: R$ {target_price:.2f}",
    ))

    fig.add_annotation(
        x=target_date, y=target_price,
        text=f"<b>Alvo Técnico<br>R$ {target_price:.2f}</b>",
        showarrow=True, arrowhead=2, arrowcolor="#FFD700",
        bgcolor="#2d2d2d", bordercolor="#FFD700", borderwidth=1,
        font=dict(color="#FFD700", size=11),
        xanchor="left", yanchor="middle",
    )

    if analyst_target is not None:
        fig.add_hline(
            y=analyst_target,
            line=dict(color="#4CAF50", width=2, dash="dash"),
            annotation_text=f"Alvo Analistas: R$ {analyst_target:.2f}",
            annotation_position="right",
            annotation_font=dict(color="#4CAF50", size=11),
        )

    # Marcadores de máxima e mínima do ano
    idx_max = df["close"].idxmax()
    idx_min = df["close"].idxmin()
    fig.add_annotation(
        x=df.loc[idx_max, "date"], y=df.loc[idx_max, "high"],
        text=f"Máx: R$ {df.loc[idx_max, 'close']:.2f}",
        showarrow=True, arrowhead=1, ay=-30,
        font=dict(color="#26a69a", size=10),
        bgcolor="rgba(0,0,0,0.5)",
    )
    fig.add_annotation(
        x=df.loc[idx_min, "date"], y=df.loc[idx_min, "low"],
        text=f"Mín: R$ {df.loc[idx_min, 'close']:.2f}",
        showarrow=True, arrowhead=1, ay=30,
        font=dict(color="#ef5350", size=10),
        bgcolor="rgba(0,0,0,0.5)",
    )

    last_date_str = last_date.strftime("%d/%m/%Y")
    fig.update_layout(
        title=f"PETR4.SA — Cotação 2026 (até {last_date_str})",
        template="plotly_dark",
        height=600,
        hovermode="x unified",
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
        margin=dict(t=80, b=20, l=60, r=60),
        xaxis=dict(title=""),
        yaxis=dict(title="Preço (R$)", tickprefix="R$ "),
    )
    return fig


def build_volume_chart(df: pd.DataFrame) -> go.Figure:
    colors = ["#26a69a" if c >= o else "#ef5350"
              for c, o in zip(df["close"], df["open"])]
    fig = go.Figure(go.Bar(
        x=df["date"], y=df["volume"],
        marker_color=colors,
        name="Volume",
        hovertemplate="%{x}<br>Volume: %{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        template="plotly_dark",
        height=150,
        showlegend=False,
        margin=dict(t=10, b=20, l=60, r=60),
        xaxis=dict(title=""),
        yaxis=dict(title="Volume", tickformat=".2s"),
    )
    return fig


def build_returns_histogram(df: pd.DataFrame) -> go.Figure:
    returns = df["close"].pct_change().dropna() * 100
    mean_ret = returns.mean()

    fig = go.Figure(go.Histogram(
        x=returns,
        nbinsx=30,
        marker_color="#42A5F5",
        opacity=0.8,
        name="Retornos",
        hovertemplate="Retorno: %{x:.2f}%<br>Freq: %{y}<extra></extra>",
    ))
    fig.add_vline(
        x=mean_ret,
        line=dict(color="#FFD700", width=2, dash="dash"),
        annotation_text=f"Média: {mean_ret:.2f}%",
        annotation_font=dict(color="#FFD700"),
    )
    fig.update_layout(
        title="Distribuição de Retornos Diários (%)",
        template="plotly_dark",
        height=300,
        showlegend=False,
        margin=dict(t=40, b=40, l=50, r=20),
        xaxis=dict(title="Retorno (%)"),
        yaxis=dict(title="Frequência"),
    )
    return fig

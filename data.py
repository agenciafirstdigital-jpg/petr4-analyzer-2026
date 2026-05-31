import streamlit as st
import yfinance as yf
import pandas as pd


@st.cache_data(ttl=3600)
def fetch_petr4_data(start: str, end: str) -> tuple[pd.DataFrame, str]:
    try:
        raw = yf.download("PETR4.SA", start=start, end=end, auto_adjust=True, progress=False)
        if raw.empty:
            return pd.DataFrame(), "Nenhum dado retornado pelo Yahoo Finance para PETR4.SA."

        # yfinance retorna MultiIndex quando há múltiplos tickers; flatten para um ticker
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = raw.columns.get_level_values(0)

        raw.columns = [c.lower() for c in raw.columns]
        raw = raw.reset_index()
        raw = raw.rename(columns={"Date": "date"})
        raw = raw[["date", "open", "high", "low", "close", "volume"]].dropna(subset=["close"])
        raw["date"] = pd.to_datetime(raw["date"])
        return raw, ""
    except Exception as exc:
        return pd.DataFrame(), f"Erro ao baixar dados: {exc}"


def get_current_price(df: pd.DataFrame) -> float:
    return float(df["close"].iloc[-1])


def validate_data(df: pd.DataFrame) -> tuple[bool, str]:
    if df.empty:
        return False, "DataFrame vazio — nenhum dado disponível."
    if len(df) < 20:
        return False, f"Apenas {len(df)} pregões disponíveis (mínimo: 20)."
    return True, ""

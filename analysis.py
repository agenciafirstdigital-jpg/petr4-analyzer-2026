import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


def calc_sma(df: pd.DataFrame, window: int) -> pd.Series:
    return df["close"].rolling(window).mean()


def calc_ema(df: pd.DataFrame, window: int) -> pd.Series:
    return df["close"].ewm(span=window, adjust=False).mean()


def calc_bollinger_bands(
    df: pd.DataFrame, window: int = 20, std_mult: float = 2.0
) -> tuple[pd.Series, pd.Series]:
    sma = df["close"].rolling(window).mean()
    std = df["close"].rolling(window).std()
    return sma + std_mult * std, sma - std_mult * std


def calc_linear_target(df: pd.DataFrame, projection_days: int = 30) -> dict:
    X = np.arange(len(df)).reshape(-1, 1)
    y = df["close"].values

    model = LinearRegression()
    model.fit(X, y)

    regression_series = pd.Series(model.predict(X), index=df.index)

    future_idx = np.array([[len(df) - 1 + projection_days]])
    target_price = float(model.predict(future_idx)[0])

    last_date = df["date"].iloc[-1]
    # avança dias úteis aproximados (5/7 dos dias corridos)
    target_date = last_date + pd.tseries.offsets.BDay(projection_days)

    r2 = float(model.score(X, y))
    slope = float(model.coef_[0])

    return {
        "target_price": target_price,
        "target_date": target_date,
        "r2": r2,
        "slope_brl_per_day": slope,
        "regression_series": regression_series,
    }


def calc_metrics(df: pd.DataFrame, target_price: float) -> dict:
    current = float(df["close"].iloc[-1])
    returns = df["close"].pct_change().dropna()
    vol_annual = float(returns.std() * np.sqrt(252) * 100)
    avg_vol_30d = float(df["volume"].tail(30).mean())

    return {
        "current_price": current,
        "target_price": target_price,
        "upside_pct": (target_price / current - 1) * 100,
        "max_2026": float(df["close"].max()),
        "min_2026": float(df["close"].min()),
        "volatility_annual": vol_annual,
        "avg_volume_30d": avg_vol_30d,
    }

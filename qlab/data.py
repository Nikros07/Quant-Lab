"""Datenschicht: Yahoo-Kurse (angepasst, Open+Close) und Ken-French-Daten, lokal gecacht.

Alle Preise sind `auto_adjust=True` (Splits + Dividenden eingerechnet), damit Total-Return-
Rechnungen stimmen. Open und Close werden gemeinsam angepasst, ihr Verhältnis bleibt also
korrekt (wichtig für die Ausführung zur Eröffnung).

Bekannte Grenze: Yahoo liefert nur heute noch existierende Titel (Survivorship-Bias bei
Einzelaktien). Für ETF-Strategien ist das Risiko klein, für Aktien-Universen nicht.
"""
from __future__ import annotations

import io
import time
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import requests

CACHE = Path(__file__).resolve().parent.parent / "data_cache"
CACHE.mkdir(exist_ok=True)

FRENCH_BASE = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
UA = {"User-Agent": "Mozilla/5.0 (quant-lab research)"}


def _safe(ticker: str) -> str:
    return ticker.replace("^", "_idx_").replace("=", "_eq_").replace("/", "_")


def _fresh(path: Path, max_age_days: float) -> bool:
    return path.exists() and (time.time() - path.stat().st_mtime) < max_age_days * 86400


def load_ticker(ticker: str, start: str = "1990-01-01", max_age_days: float = 3.0,
                refresh: bool = False) -> pd.DataFrame:
    """Open/High/Low/Close/Volume (angepasst) für einen Ticker, Index = Handelstag."""
    import yfinance as yf

    path = CACHE / f"px_{_safe(ticker)}.parquet"
    if not refresh and _fresh(path, max_age_days):
        return pd.read_parquet(path)
    last_err = None
    for attempt in range(3):
        try:
            df = yf.Ticker(ticker).history(start=start, auto_adjust=True, actions=False)
            if df is not None and len(df) > 0:
                df.index = pd.to_datetime(df.index).tz_localize(None).normalize()
                df = df[["Open", "High", "Low", "Close", "Volume"]].astype(float)
                df = df[~df.index.duplicated(keep="last")].sort_index()
                df.to_parquet(path)
                return df
            last_err = RuntimeError(f"leere Antwort für {ticker}")
        except Exception as exc:  # Netz, Rate-Limit
            last_err = exc
        time.sleep(1.5 * (attempt + 1))
    if path.exists():  # lieber alter Cache als gar nichts, aber laut
        print(f"[data] WARNUNG: {ticker} nicht aktualisierbar ({last_err}); alter Cache wird genutzt")
        return pd.read_parquet(path)
    raise RuntimeError(f"Ticker {ticker} nicht ladbar: {last_err}")


class Panel:
    """Gleich indizierte Open/Close-Matrizen (Spalten = Ticker)."""

    def __init__(self, open_: pd.DataFrame, close: pd.DataFrame, volume: pd.DataFrame | None = None):
        self.open = open_
        self.close = close
        self.volume = volume if volume is not None else pd.DataFrame(index=close.index)

    @property
    def tickers(self) -> list[str]:
        return list(self.close.columns)

    def truncate(self, end) -> "Panel":
        end = pd.Timestamp(end)
        return Panel(self.open.loc[:end], self.close.loc[:end], self.volume.loc[:end])

    def slice(self, start=None, end=None) -> "Panel":
        sl = slice(pd.Timestamp(start) if start else None, pd.Timestamp(end) if end else None)
        return Panel(self.open.loc[sl], self.close.loc[sl], self.volume.loc[sl])


def panel_from_returns(ret: pd.DataFrame, base: float = 100.0) -> Panel:
    """Panel aus Renditereihen (z. B. Ken-French-Portfolios).

    open == close: Der Tageskursgewinn liegt komplett "über Nacht", ein Signal von Tag t wird
    also erst zum Schlusskurs von t+1 umgesetzt — konservativ und einheitlich. Fehlende Werte
    (NaN) bleiben NaN (nicht handelbar).
    """
    px = (1.0 + ret.fillna(0.0)).cumprod() * base
    px = px.where(ret.notna() | ret.shift(1).notna())
    return Panel(px.copy(), px)


def load_panel(tickers: list[str], start: str = "1990-01-01", **kw) -> Panel:
    opens, closes, vols = {}, {}, {}
    for t in tickers:
        df = load_ticker(t, start=start, **kw)
        opens[t], closes[t], vols[t] = df["Open"], df["Close"], df["Volume"]
    open_ = pd.DataFrame(opens).sort_index()
    close = pd.DataFrame(closes).sort_index()
    vol = pd.DataFrame(vols).sort_index()
    # Index = Vereinigung aller Handelstage; Lücken NICHT stillschweigend füllen,
    # die Engine behandelt NaN-Kurse als "nicht handelbar".
    return Panel(open_.reindex(close.index), close, vol.reindex(close.index))


# --------------------------------------------------------------------------------------
# Ken French
# --------------------------------------------------------------------------------------

def _french_blocks(raw: str) -> list[pd.DataFrame]:
    """Alle Datenblöcke (Monats- oder Tagesdaten) einer French-CSV, in Dateireihenfolge.

    Ein Block beginnt bei einer Zeile mit 6-stelligem (YYYYMM) oder 8-stelligem (YYYYMMDD)
    Datum und endet bei der ersten Nicht-Datenzeile. Jahrestabellen (4-stellig) werden ignoriert.
    Die Kopfzeile ist die letzte nichtleere Zeile vor dem Block.
    """
    lines = raw.splitlines()
    blocks: list[pd.DataFrame] = []
    i, n = 0, len(lines)
    while i < n:
        first = lines[i].split(",")[0].strip()
        if first.isdigit() and len(first) in (6, 8):
            width = len(first)
            j = i - 1
            while j >= 0 and not lines[j].strip():
                j -= 1
            header = [c.strip() for c in lines[j].split(",")] if j >= 0 else []
            k = i
            rows = []
            while k < n and lines[k].split(",")[0].strip().isdigit() and len(lines[k].split(",")[0].strip()) == width:
                rows.append(lines[k])
                k += 1
            df = pd.read_csv(io.StringIO("\n".join(rows)), header=None)
            cols = header[1:len(df.columns)] if len(header) >= len(df.columns) else [f"c{c}" for c in range(1, len(df.columns))]
            df.columns = ["date"] + [c if c else f"c{idx}" for idx, c in enumerate(cols, 1)]
            df["date"] = pd.to_datetime(df["date"].astype(str), format="%Y%m%d" if width == 8 else "%Y%m")
            df = df.set_index("date").astype(float).replace([-99.99, -999.0], np.nan) / 100.0
            blocks.append(df)
            i = k
        else:
            i += 1
    if not blocks:
        raise ValueError("French-CSV ohne lesbare Datenblöcke")
    return blocks


def french(dataset: str, daily: bool | None = None, table: int = 0, max_age_days: float = 30.0) -> pd.DataFrame:
    """Ken-French-Datei als DataFrame (Dezimalrenditen).

    dataset: Dateiname ohne "_CSV.zip", z. B. "F-F_Research_Data_Factors",
             "F-F_Research_Data_5_Factors_2x3", "F-F_Momentum_Factor",
             "10_Portfolios_Prior_12_2_Daily", "49_Industry_Portfolios", "Portfolios_Formed_on_BETA".
    daily:   nur Komfort: True hängt "_daily" an, falls der Name es nicht schon enthält.
    table:   0 = erste Tabelle der Datei (meist value-weighted), 1 = zweite (meist equal-weighted) usw.
    """
    name = dataset
    if daily and not name.lower().endswith("daily"):
        name = f"{name}_daily"
    path = CACHE / f"french_{name}_t{table}.parquet"
    if _fresh(path, max_age_days):
        return pd.read_parquet(path)
    r = requests.get(FRENCH_BASE + f"{name}_CSV.zip", headers=UA, timeout=60)
    r.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        raw = z.read(z.namelist()[0]).decode("latin-1")
    blocks = _french_blocks(raw)
    if table >= len(blocks):
        raise IndexError(f"{name}: nur {len(blocks)} Tabellen")
    df = blocks[table]
    df.to_parquet(path)
    return df


def risk_free_daily(index: pd.DatetimeIndex) -> pd.Series:
    """Tagesrendite des risikolosen Zinses (Fama-French RF), auf `index` gelegt.

    French veröffentlicht mit Verzögerung; Lücken am Ende werden mit dem letzten Wert
    gefüllt (Näherung, nur für Cash-Verzinsung).
    """
    rf = french("F-F_Research_Data_Factors", daily=True)["RF"]
    return rf.reindex(index).ffill().fillna(0.0)


# --------------------------------------------------------------------------------------
# Shiller (Robert Shiller, ie_data.xls): S&P-Preise, Dividenden, Gewinne, CPI, GS10, CAPE seit 1871
# --------------------------------------------------------------------------------------

SHILLER_URL = "https://img1.wsimg.com/blobby/go/e5e77e0b-59d1-44d9-ab25-4763ac982e53/downloads/ie_data.xls"


def shiller(max_age_days: float = 30.0) -> pd.DataFrame:
    """Monatsdaten, Index = Monatsende. Spalten: price, dividend, earnings, cpi, long_rate, real_price, cape.

    Hinweis: Das Original veröffentlicht Monatsdurchschnitte (nicht Schlusskurse) und CPI mit
    Verzögerung — für Signale daher mindestens 1 Monat (CPI: 2 Monate) verzögern.
    """
    path = CACHE / "shiller_ie_data.parquet"
    if _fresh(path, max_age_days):
        return pd.read_parquet(path)
    r = requests.get(SHILLER_URL, headers=UA, timeout=90)
    r.raise_for_status()
    raw = pd.read_excel(io.BytesIO(r.content), sheet_name="Data", header=None, skiprows=8)
    raw = raw.iloc[:, :13]
    raw.columns = ["date", "price", "dividend", "earnings", "cpi", "date_frac", "long_rate", "real_price",
                   "real_dividend", "real_total_return_price", "real_earnings", "real_tr_earnings", "cape"]
    raw = raw[pd.to_numeric(raw["date"], errors="coerce").notna()].copy()
    d = raw["date"].astype(float)
    year = d.astype(int)
    month = ((d - year) * 100).round().astype(int).clip(1, 12)
    raw.index = (pd.to_datetime({"year": year, "month": month, "day": 1}) + pd.offsets.MonthEnd(0)).to_numpy()
    out = raw[["price", "dividend", "earnings", "cpi", "long_rate", "real_price", "cape"]].apply(pd.to_numeric, errors="coerce")
    out["long_rate"] = out["long_rate"] / 100.0
    out.index.name = "date"
    out.to_parquet(path)
    return out

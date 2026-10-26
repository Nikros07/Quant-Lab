"""Tests für strategies/nagel_vix_gated_sector_etf_reversal.py — nur synthetische Daten, kein Netz, kein Datencache."""
from __future__ import annotations

import inspect
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from qlab.data import Panel
from qlab.engine import check_causality, run_backtest
from strategies import nagel_vix_gated_sector_etf_reversal as strat

ETFS, VIX = strat.ETFS, strat.VIX
VARIANTS = {"base": {}, **strat.SPEC["variants"]}
EPS = 1e-9


def _vix_path(n: int, seed: int = 4) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return 22.0 + 10.0 * np.sin(np.arange(n) / 45.0) + rng.normal(0.0, 1.5, n)


def _panel(n: int = 800, seed: int = 3, vix=None, start: str = "2001-01-02", extra_vix_days: int = 0) -> Panel:
    """9 ETF-Zufallspfade + VIX-Spalte; `extra_vix_days` = VIX-Vorlauf vor dem ETF-Start (ETFs dort NaN)."""
    rng = np.random.default_rng(seed)
    total = n + extra_vix_days
    idx = pd.bdate_range(start, periods=total)
    rets = rng.normal(0.0003, 0.01, (total, len(ETFS)))
    close = pd.DataFrame(100.0 * np.exp(np.cumsum(rets, axis=0)), index=idx, columns=ETFS)
    close[VIX] = _vix_path(total) if vix is None else np.asarray(vix, float)
    if extra_vix_days:
        close.iloc[:extra_vix_days, :len(ETFS)] = np.nan
    return Panel((close * 0.999).copy(), close)


def _flat_panel(n: int = 420, vix_level: float = 30.0, drop_day: int | None = None, drop: float = -0.01,
                drop_ticker: str = "XLB") -> Panel:
    """Alle ETFs konstant 100, optional ein einzelner Kurseinbruch; Open == Close."""
    idx = pd.bdate_range("2001-01-02", periods=n)
    close = pd.DataFrame(100.0, index=idx, columns=ETFS + [VIX])
    close[VIX] = vix_level
    if drop_day is not None:
        close.iloc[drop_day:, close.columns.get_loc(drop_ticker)] = 100.0 * (1.0 + drop)
    return Panel(close.copy(), close)


def _reference(close: pd.DataFrame, threshold, window: int = 252, lags: int = 5) -> pd.DataFrame:
    """Unabhängige, zeilenweise Referenz (reine Schleife) ohne fehlende Kurse."""
    px = close[ETFS]
    r = px / px.shift(1) - 1.0
    vix = close[VIX]
    out = {}
    for i in range(len(px)):
        if i < max(window - 1, lags):
            continue
        ws = []
        for j in range(lags):
            rr = r.iloc[i - j].to_numpy()
            x = rr - rr.mean()
            ws.append(-x / (0.5 * np.abs(x).sum()))
        overlay = np.mean(ws, axis=0)
        ref = np.median(vix.iloc[i - window + 1:i + 1].to_numpy()) if threshold is None else threshold
        out[px.index[i]] = overlay * float(vix.iloc[i] > ref)
    return pd.DataFrame(out, index=ETFS).T


def test_spec_contract():
    spec = strat.SPEC
    assert spec["id"] == "nagel_vix_gated_sector_etf_reversal"
    assert Path(strat.__file__).stem == spec["id"]
    assert spec["family"] == "reversal"
    assert spec["sources"] and spec["start"]
    assert len(spec["variants"]) <= 3
    sig = inspect.signature(strat.weights)
    for name in list(spec["params"]) + [k for v in spec["variants"].values() for k in v]:
        assert name in sig.parameters, name
    assert ETFS == ["XLB", "XLE", "XLF", "XLI", "XLK", "XLP", "XLU", "XLV", "XLY"]
    assert spec["tickers"] == ETFS + [VIX]
    assert spec["params"] == {"vix_threshold": None, "vix_window": 252, "n_lags": 5}
    assert {v["vix_threshold"] for v in spec["variants"].values()} == {20.0, 25.0, 30.0}
    assert set(spec["cost_bps"]) == set(ETFS) and set(spec["cost_bps"].values()) == {3.0}
    assert VIX not in spec["cost_bps"]


def test_registry_discovers_module():
    from strategies._registry import discover

    mods = discover()
    assert mods[strat.SPEC["id"]] is strat


@pytest.mark.parametrize("variant", list(VARIANTS))
def test_shape_and_range(variant):
    panel = _panel()
    w = strat.weights(panel, **{**strat.SPEC["params"], **VARIANTS[variant]})
    assert list(w.columns) == ETFS                                   # ^VIX bekommt nie eine Spalte/ein Gewicht
    assert len(w) > 300
    assert w.notna().all().all() and np.isfinite(w.to_numpy()).all()
    assert w.index.isin(panel.close.index).all() and w.index.is_monotonic_increasing
    gross = w.abs().sum(axis=1)
    assert (gross <= 2.0 + EPS).all()                                # Long-Leg +1, Short-Leg -1
    assert (w.sum(axis=1).abs() <= EPS).all()                        # dollar-neutral
    assert (w.abs() <= 2.0 + EPS).all().all()
    assert (gross > 0.1).any()                                       # Gate geht auch auf (Test nicht leer)
    assert (gross == 0.0).any()                                      # ...und zu


def test_variants_are_gated_differently():
    panel = _panel()
    shares = {}
    for name, kw in VARIANTS.items():
        w = strat.weights(panel, **kw)
        shares[name] = float((w.abs().sum(axis=1) > 0).mean())
    # synthetischer VIX schwankt um 22 +/- 10: höhere Schwelle -> seltener aktiv
    assert shares["vix_20"] > shares["vix_25"] > shares["vix_30"] > 0.0


@pytest.mark.parametrize("threshold", [None, 20.0, 25.0, 30.0])
def test_matches_reference_rule(threshold):
    panel = _panel(n=700, seed=9)
    w = strat.weights(panel, vix_threshold=threshold)
    ref = _reference(panel.close, threshold)
    assert list(w.index) == list(ref.index)
    assert np.allclose(w.to_numpy(), ref[ETFS].to_numpy(), atol=1e-12)
    assert (ref.abs().sum(axis=1) > 0).any() and (ref.abs().sum(axis=1) == 0).any()


def test_single_loser_gets_long_overlay_for_five_days():
    panel = _flat_panel(drop_day=300, drop=-0.01)
    w = strat.weights(panel, vix_threshold=0.0)                      # VIX 30 > 0: Gate immer offen (nach Vorlauf)
    idx = panel.close.index
    k = idx[300]
    # vor dem Einbruch: keine Renditen -> Nenner 0 -> Gewichte 0 (kein NaN, keine inf)
    assert (w.loc[:idx[299]].to_numpy() == 0.0).all()
    for j in range(5):                                               # Tage k .. k+4 tragen das Signal von Tag k
        row = w.loc[idx[300 + j]]
        assert row["XLB"] == pytest.approx(0.2)                      # Verlierer: w = +1, Overlay 1/5
        assert row.drop("XLB").to_numpy() == pytest.approx(-0.025)   # Gewinner: je -1/8, Overlay 1/5
    assert (w.loc[idx[305]:].to_numpy() == 0.0).all()                # nach 5 Tagen läuft es aus
    assert w.index.max() == idx[-1] and k in w.index


def test_single_winner_gets_short_overlay():
    panel = _flat_panel(drop_day=300, drop=+0.02, drop_ticker="XLK")
    w = strat.weights(panel, vix_threshold=0.0)
    assert w.loc[panel.close.index[300], "XLK"] == pytest.approx(-0.2)
    assert w.loc[panel.close.index[300]].drop("XLK").to_numpy() == pytest.approx(0.025)


def test_overlay_averages_five_daily_weights():
    """Zwei Einbrüche in verschiedenen ETFs an aufeinanderfolgenden Tagen: Overlay = Mittel der Tagesgewichte."""
    panel = _flat_panel()
    close = panel.close.copy()
    close.iloc[300:, close.columns.get_loc("XLB")] = 99.0            # Tag 300: XLB -1 %
    close.iloc[301:, close.columns.get_loc("XLE")] = 98.0            # Tag 301: XLE -2 %
    w = strat.weights(Panel(close.copy(), close), vix_threshold=0.0)
    idx = close.index
    r = close[ETFS] / close[ETFS].shift(1) - 1.0
    daily = {}
    for d in (idx[300], idx[301]):
        x = r.loc[d] - r.loc[d].mean()
        daily[d] = -x / (0.5 * x.abs().sum())
    assert daily[idx[300]]["XLB"] == pytest.approx(1.0)
    expect = (daily[idx[300]] + daily[idx[301]]) / 5.0
    assert np.allclose(w.loc[idx[301]].to_numpy(), expect.to_numpy())
    assert np.allclose(w.loc[idx[300]].to_numpy(), (daily[idx[300]] / 5.0).to_numpy())
    assert w.loc[idx[301], "XLB"] != w.loc[idx[300], "XLB"]


def test_gate_median_is_strict():
    n = 320
    panel = _flat_panel(n=n, drop_day=280, drop=-0.01)
    close = panel.close.copy()
    close[VIX] = 20.0
    idx = close.index
    w = strat.weights(Panel(close.copy(), close))
    # VIX == Median (20 == 20) -> Gate zu: Zeilen vorhanden, aber 0
    assert (w.loc[idx[280]].to_numpy() == 0.0).all()
    assert (w.to_numpy() == 0.0).all()
    # VIX springt am Tag 281 auf 21 (251 x 20 + 1 x 21 -> Median 20): Gate auf, das Signal vom Tag 280 lebt noch
    close.loc[idx[281], VIX] = 21.0
    w2 = strat.weights(Panel(close.copy(), close))
    assert w2.loc[idx[281], "XLB"] == pytest.approx(0.2)
    assert (w2.loc[idx[280]].to_numpy() == 0.0).all()                # Gate des Vortags (VIX 20) bleibt zu


def test_gate_median_moves_with_the_window():
    """VIX 20 bis Tag 299, danach 21: Kurz nach dem Sprung ist 21 > Median 20 (Gate auf), nach einem Jahr
    ist der Median selbst 21 und 21 > 21 falsch (Gate zu)."""
    n = 700
    idx = pd.bdate_range("2001-01-02", periods=n)
    close = pd.DataFrame(100.0, index=idx, columns=ETFS + [VIX])
    close[VIX] = np.where(np.arange(n) < 300, 20.0, 21.0)
    close.iloc[310:, close.columns.get_loc("XLB")] = 99.0           # Tag 310: XLB -1 %
    close.iloc[650:, close.columns.get_loc("XLE")] = 99.0           # Tag 650: XLE -1 %
    w = strat.weights(Panel(close.copy(), close))
    assert w.loc[idx[310], "XLB"] == pytest.approx(0.2)             # Fenster 59..310: 241 x 20, 11 x 21 -> Median 20
    assert w.loc[idx[650], "XLE"] == 0.0                            # Fenster 399..650: nur 21 -> Median 21
    assert (w.loc[idx[650]].to_numpy() == 0.0).all()


def test_gate_median_window_excludes_future():
    """Median über t-251..t: Ein VIX-Ausreißer NACH t verändert das Gate bei t nicht."""
    panel = _panel(n=700, seed=21)
    base = strat.weights(panel)
    close = panel.close.copy()
    cut = close.index[500]
    close.loc[close.index > cut, VIX] = 80.0
    other = strat.weights(Panel((close * 0.999).copy(), close))
    assert base.loc[:cut].equals(other.loc[:cut])
    assert not base.loc[cut:].equals(other.loc[cut:])                # Test ist nicht trivial


def test_fixed_threshold_strict_comparison():
    n = 320
    panel = _flat_panel(n=n, vix_level=25.0, drop_day=300, drop=-0.01)
    idx = panel.close.index
    on20 = strat.weights(panel, vix_threshold=20.0).loc[idx[300], "XLB"]
    off25 = strat.weights(panel, vix_threshold=25.0).loc[idx[300], "XLB"]      # 25 > 25 ist falsch
    off30 = strat.weights(panel, vix_threshold=30.0).loc[idx[300], "XLB"]
    assert on20 == pytest.approx(0.2)
    assert off25 == 0.0 and off30 == 0.0


def test_gate_off_emits_explicit_zero_rows():
    panel = _flat_panel(drop_day=300, drop=-0.01, vix_level=10.0)
    w = strat.weights(panel, vix_threshold=30.0)                     # Gate immer zu
    assert len(w) > 100
    assert (w.to_numpy() == 0.0).all()                               # 0.0, nicht NaN (sonst würde die Engine nicht flach gehen)
    assert not w.isna().any().any()


def test_warmup_and_first_signal():
    n = 600
    panel = _panel(n=n)
    idx = panel.close.index
    w = strat.weights(panel)
    assert w.index[0] == idx[251]                                    # 252 VIX-Beobachtungen inkl. t
    w_fix = strat.weights(panel, vix_threshold=25.0)
    assert w_fix.index[0] == idx[251]                                # feste Schwelle: gleicher Zeitraum
    w_short = strat.weights(panel, vix_window=20, n_lags=5)
    assert w_short.index[0] == idx[19]
    w_lag = strat.weights(panel, vix_window=3, n_lags=5)
    assert w_lag.index[0] == idx[5]                                  # 5 Renditen: Tage 1..5


def test_vix_history_before_etf_start_is_used():
    """VIX-Vorlauf vor dem ETF-Start zählt für das Gate; erstes Signal erst nach 5 ETF-Renditen."""
    panel = _panel(n=400, extra_vix_days=300)
    idx = panel.close.index
    etf_days = idx[300:]
    w = strat.weights(panel)
    assert w.index[0] == etf_days[5]
    assert w.index.isin(etf_days).all()
    # gleiche ETF-Pfade ohne Vorlauf: Gate braucht erst 252 Tage
    p2 = Panel(panel.open.iloc[300:], panel.close.iloc[300:])
    assert strat.weights(p2).index[0] == etf_days[251]


def test_no_weights_on_nan_prices():
    panel = _panel(n=700, seed=5)
    close = panel.close.copy()
    close.iloc[:350, close.columns.get_loc("XLK")] = np.nan          # XLK später gelistet
    close.iloc[500:504, close.columns.get_loc("XLE")] = np.nan       # kurze Datenlücke
    p2 = Panel((close * 0.999).copy(), close)
    for kw in VARIANTS.values():
        w = strat.weights(p2, **kw)
        assert len(w) > 300
        assert w.notna().all().all()
        nan_mask = close.loc[w.index, ETFS].isna().to_numpy()
        assert nan_mask.sum() > 50
        assert (w.to_numpy()[nan_mask] == 0.0).all()
        assert (w["XLK"].loc[:close.index[349]] == 0.0).all()
        assert (w.abs().sum(axis=1) <= 2.0 + EPS).all()
        # an Tagen ohne fehlenden Kurs bleibt das Buch dollar-neutral (Tagesgewichte summieren je auf 0)
        clean = ~close.loc[w.index, ETFS].isna().any(axis=1)
        assert clean.sum() > 100
        assert (w[clean.to_numpy()].sum(axis=1).abs() <= 1e-9).all()


def test_phantom_holiday_row_is_ignored():
    """Zeile mit VIX-Wert, aber ohne jeden ETF-Kurs (Feiertag): keine Zeile, Renditen laufen über die Lücke."""
    panel = _panel(n=700, seed=8)
    p = 450
    close = panel.close.copy()
    close.iloc[p, :len(ETFS)] = np.nan
    with_phantom = Panel((close * 0.999).copy(), close)
    dropped_close = close.drop(index=close.index[p])
    without = Panel((dropped_close * 0.999).copy(), dropped_close)
    w_a = strat.weights(with_phantom, vix_threshold=25.0)
    w_b = strat.weights(without, vix_threshold=25.0)
    assert close.index[p] not in w_a.index
    common = w_a.index.intersection(w_b.index)
    assert len(common) > 300
    assert np.allclose(w_a.loc[common].to_numpy(), w_b.loc[common].to_numpy(), atol=1e-12)


def test_all_equal_returns_give_zero_weights():
    panel = _flat_panel()
    w = strat.weights(panel, vix_threshold=0.0)
    assert len(w) > 100
    assert (w.to_numpy() == 0.0).all()


def test_empty_when_no_etf_data():
    idx = pd.bdate_range("2001-01-02", periods=30)
    close = pd.DataFrame(np.nan, index=idx, columns=ETFS + [VIX])
    close[VIX] = 20.0
    w = strat.weights(Panel(close.copy(), close))
    assert len(w) == 0 and list(w.columns) == ETFS


@pytest.mark.parametrize("variant", list(VARIANTS))
def test_causality_check(variant):
    panel = _panel(n=900, seed=13)
    params = {**strat.SPEC["params"], **VARIANTS[variant]}
    assert check_causality(lambda p: strat.weights(p, **params), panel) == []


def test_causality_check_with_gaps():
    panel = _panel(n=900, seed=14)
    close = panel.close.copy()
    close.iloc[:300, close.columns.get_loc("XLU")] = np.nan
    close.iloc[600:603, close.columns.get_loc("XLF")] = np.nan
    close.iloc[650, :len(ETFS)] = np.nan
    p2 = Panel((close * 0.999).copy(), close)
    assert check_causality(lambda p: strat.weights(p, vix_threshold=None), p2) == []
    assert check_causality(lambda p: strat.weights(p, vix_threshold=25.0), p2) == []


def test_future_prices_do_not_change_past_weights():
    panel = _panel(n=800, seed=17)
    base = strat.weights(panel)
    cut = panel.close.index[int(len(panel.close) * 0.7)]
    close = panel.close.copy()
    close.loc[close.index > cut, ETFS] *= np.linspace(0.5, 1.5, len(ETFS))   # ungleiche Sprünge
    other = strat.weights(Panel((close * 0.999).copy(), close))
    assert base.loc[:cut].equals(other.loc[:cut])
    assert not base.loc[cut:].equals(other.loc[cut:])


def test_engine_integration_timing_and_flat_exit():
    panel = _flat_panel(drop_day=300, drop=-0.01)
    idx = panel.close.index
    w = strat.weights(panel, vix_threshold=0.0)
    rf = pd.Series(0.0, index=idx)
    res = run_backtest(panel, w, rf=rf)
    assert res.weights.loc[idx[300]].abs().max() < 1e-9                      # Signaltag: noch keine Position
    after = res.weights.loc[idx[301]]
    assert after["XLB"] == pytest.approx(0.2, abs=0.005)                     # Handel zur Eröffnung t+1
    assert after.drop(["XLB", VIX]).to_numpy() == pytest.approx(-0.025, abs=0.002)
    assert res.weights[VIX].abs().max() == 0.0                               # ^VIX wird nie gehandelt
    assert res.weights.loc[idx[305], "XLB"] == pytest.approx(0.2, abs=0.005)
    assert res.gross_exposure.max() <= 2.0 + 0.01
    assert res.weights.loc[idx[306]:].abs().to_numpy().max() < 1e-9          # Nullzeile am Tag 305 -> flach ab 306
    assert res.skipped_orders == 0


def test_engine_integration_random_panel_goes_flat_when_gate_closes():
    panel = _panel(n=800, seed=2)
    w = strat.weights(panel)
    idx = panel.close.index
    res = run_backtest(panel, w, rf=pd.Series(0.0, index=idx))
    assert np.isfinite(res.nav.to_numpy()).all() and (res.nav > 0).all()
    assert res.gross_exposure.max() < 2.5
    zero_days = w.index[(w.abs().sum(axis=1) == 0.0).to_numpy()]
    assert len(zero_days) > 30
    pos = idx.get_indexer(zero_days) + 1
    nxt = idx[pos[pos < len(idx)]]                                           # Nullzeile an t -> flach nach Handel an t+1
    assert len(nxt) > 30
    assert res.weights.loc[nxt].abs().to_numpy().max() < 1e-9
    assert res.weights[VIX].abs().max() == 0.0

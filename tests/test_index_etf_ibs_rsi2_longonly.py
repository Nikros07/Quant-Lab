"""Tests der Index-ETF-Kurzfrist-Umkehr (IBS-Kern, Connors-RSI(2) als Variante).

Alles auf synthetischen Panels: kein Netz, kein Datencache. Bekannte Antworten statt Vertrauen:
* handgebaute Szenarien mit exakt gesetzten IBS-Werten pruefen Einstieg, Ausstieg, Zeitstopp, Wiedereinstieg;
* eine unabhaengig geschriebene Referenz (reines Python, Schleifen ueber Listen) muss auf Zufallspfaden
  dieselben Zielzustaende liefern wie die Strategie;
* der Kausalitaetstest der Engine laeuft fuer Basis und beide Varianten.
"""
import numpy as np
import pandas as pd
import pytest

from qlab.calendar import NYSE_BDAY
from qlab.data import Panel
from qlab.engine import check_causality, run_backtest
from strategies import index_etf_ibs_rsi2_longonly as mod
from strategies.index_etf_ibs_rsi2_longonly import OHLCPanel, SPEC, _ibs, _wilder_rsi, weights

VARIANTS = ["base"] + sorted(SPEC["variants"])
WARM = SPEC["params"]["sma_window"] - 1          # Position des ersten gueltigen Tages (200 Schlusskurse)


def params_for(variant: str) -> dict:
    return dict(SPEC["params"]) if variant == "base" else {**SPEC["params"], **SPEC["variants"][variant]}


def wfun(**kw):
    """weights mit Basisparametern + Ueberschreibungen (damit Tests keine Standardwerte vergessen)."""
    return weights(kw.pop("panel"), **{**SPEC["params"], **kw})


# --------------------------------------------------------------------------------------
# Synthetische Panels
# --------------------------------------------------------------------------------------

def random_ohlc(names=("SPY",), n=1800, seed=0, drift=0.0004, vol=0.011, start="2005-01-03"):
    """Zufallspfade mit gueltigem OHLC (Low <= Open, Close <= High) auf dem NYSE-Kalender."""
    idx = pd.date_range(start, periods=n, freq=NYSE_BDAY)
    rng = np.random.default_rng(seed)
    o, h, l, c = {}, {}, {}, {}
    for t in names:
        close = 100.0 * np.exp(np.cumsum(rng.normal(drift, vol, n)))
        open_ = np.r_[close[0], close[:-1]] * (1.0 + rng.normal(0.0, 0.002, n))
        hi = np.maximum(open_, close) * (1.0 + np.abs(rng.normal(0.0, 0.004, n)))
        lo = np.minimum(open_, close) * (1.0 - np.abs(rng.normal(0.0, 0.004, n)))
        o[t], h[t], l[t], c[t] = open_, hi, lo, close
    f = lambda d: pd.DataFrame(d, index=idx)
    return OHLCPanel(f(o), f(c), f(h), f(l))


def scenario(ibs, trend=0.001, ticker="SPY", n=None):
    """Glatter Trend, IBS je Tag exakt vorgegeben (Liste/Array der Laenge n).

    Spanne = 1 % vom Schlusskurs; Low = Close - IBS*Spanne, High = Low + Spanne => IBS = (C-L)/(H-L).
    Steigt der Kurs jeden Tag um `trend`, liegt Close deutlich ueber dem SMA200 (trend > 0) bzw. darunter (< 0).
    """
    ibs = np.asarray(ibs, float)
    n = len(ibs) if n is None else n
    idx = pd.date_range("2020-01-02", periods=n, freq=NYSE_BDAY)
    close = 100.0 * np.exp(np.cumsum(np.full(n, trend)))
    rng_ = 0.01 * close
    low = close - np.nan_to_num(ibs, nan=0.0) * rng_
    high = low + rng_
    flat = np.isnan(ibs)                                    # NaN-IBS = High == Low == Close
    low = np.where(flat, close, low)
    high = np.where(flat, close, high)
    open_ = np.r_[close[0], close[:-1]]
    f = lambda a: pd.DataFrame({ticker: a}, index=idx)
    return OHLCPanel(f(open_), f(close), f(high), f(low))


def ibs_path(n=330, **overrides):
    """IBS 0.5 an allen Tagen (kein Signal), einzelne Tage ueberschrieben: ibs_path(250=0.1) -> Dict-Syntax."""
    a = np.full(n, 0.5)
    for k, v in overrides.items():
        a[int(k.lstrip("d"))] = v
    return a


def rows_of(w: pd.DataFrame):
    """Zeilen als Liste (Datum, Gewicht)."""
    return [(d, float(x)) for d, x in w.iloc[:, 0].items()]


def positions(w: pd.DataFrame, panel) -> list:
    idx = panel.close.index
    return [(int(idx.get_loc(d)), x) for d, x in rows_of(w)]


# --------------------------------------------------------------------------------------
# Unabhaengige Referenz (anders gebaut: Listen und Schleifen, kein pandas im Kern)
# --------------------------------------------------------------------------------------

def reference_states(close, high, low, *, signal="ibs", use_sma_filter=True, sma_window=200, ibs_entry=0.2,
                     ibs_exit=0.7, max_hold=5, rsi_len=2, rsi_entry=10.0, exit_sma=5, **_ignored):
    """Zielzustand je Tag (Liste, None vor dem Start) fuer die Serie der gueltigen Kurse."""
    c, h, l = list(close), list(high), list(low)
    n = len(c)

    def ibs(i):
        if not (h[i] > l[i]):
            return None
        return (c[i] - l[i]) / (h[i] - l[i])

    def rsi(i):                                  # klassischer Wilder-RSI mit SMA-Startwert, Rohform RS
        if i < rsi_len:
            return None
        gains = [max(c[j + 1] - c[j], 0.0) for j in range(i)]
        losses = [max(c[j] - c[j + 1], 0.0) for j in range(i)]
        ag = sum(gains[:rsi_len]) / rsi_len
        al = sum(losses[:rsi_len]) / rsi_len
        for j in range(rsi_len, i):
            ag = (ag * (rsi_len - 1) + gains[j]) / rsi_len
            al = (al * (rsi_len - 1) + losses[j]) / rsi_len
        if ag + al == 0:
            return None
        if al == 0:
            return 100.0
        return 100.0 - 100.0 / (1.0 + ag / al)

    def sma(i, w):
        return sum(c[i - w + 1:i + 1]) / w if i >= w - 1 else None

    out = [None] * n
    long_, t0 = False, None
    for i in range(sma_window - 1, n):
        trend = True
        if use_sma_filter:
            s = sma(i, sma_window)
            trend = s is not None and c[i] > s
        if long_:
            if signal == "ibs":
                x = ibs(i)
                ex = x is not None and x > ibs_exit
            else:
                s5 = sma(i, exit_sma)
                ex = s5 is not None and c[i] > s5
            if ex or (max_hold is not None and i - t0 >= max_hold):
                long_ = False
        else:
            if signal == "ibs":
                x = ibs(i)
                en = x is not None and x < ibs_entry
            else:
                r = rsi(i)
                en = r is not None and r < rsi_entry
            if trend and en:
                long_, t0 = True, i
        out[i] = 1.0 if long_ else 0.0
    return out


def expand(w: pd.DataFrame, index) -> list:
    """Zeilen (nur Wechsel) -> Zielzustand je Tag des Index (None vor der ersten Zeile)."""
    s = w.iloc[:, 0].reindex(index).ffill()
    return [None if np.isnan(x) else float(x) for x in s]


# --------------------------------------------------------------------------------------
# Indikatoren
# --------------------------------------------------------------------------------------

def test_ibs_known_values_and_zero_range():
    c = pd.Series([10.0, 10.0, 7.0])
    h = pd.Series([12.0, 10.0, 9.0])
    l = pd.Series([8.0, 10.0, 5.0])
    ibs = _ibs(h, l, c)
    assert ibs.iloc[0] == pytest.approx(0.5)
    assert np.isnan(ibs.iloc[1])                           # High == Low -> kein Signal
    assert ibs.iloc[2] == pytest.approx(0.5)


def test_wilder_rsi2_hand_computed():
    rsi = _wilder_rsi(pd.Series([10.0, 11.0, 10.5, 10.2, 10.2]), 2)
    assert np.isnan(rsi.iloc[0]) and np.isnan(rsi.iloc[1])
    assert rsi.iloc[2] == pytest.approx(100 * 0.5 / 0.75)          # ag=(1+0)/2, al=(0+0.5)/2
    assert rsi.iloc[3] == pytest.approx(100 * 0.25 / 0.525)        # ag=(0.5+0)/2, al=(0.25+0.3)/2
    assert rsi.iloc[4] == pytest.approx(100 * 0.125 / (0.125 + 0.1375))   # Aenderung 0: beide Mittel halbieren


def test_wilder_rsi_extremes():
    up = _wilder_rsi(pd.Series([1.0, 2.0, 3.0, 4.0, 5.0]), 2)
    assert up.iloc[-1] == pytest.approx(100.0)
    down = _wilder_rsi(pd.Series([5.0, 4.0, 3.0, 2.0, 1.0]), 2)
    assert down.iloc[-1] == pytest.approx(0.0)
    flat = _wilder_rsi(pd.Series([3.0] * 6), 2)
    assert flat.isna().all()                                       # keine Bewegung -> kein Signal


def test_rsi_uses_only_past_values():
    rng = np.random.default_rng(3)
    c = pd.Series(100 * np.exp(np.cumsum(rng.normal(0, 0.01, 120))))
    full = _wilder_rsi(c, 2)
    for k in (30, 60, 100):
        part = _wilder_rsi(c.iloc[:k + 1], 2)
        assert part.iloc[k] == pytest.approx(full.iloc[k])


# --------------------------------------------------------------------------------------
# Handgebaute Szenarien: Timing der Regeln
# --------------------------------------------------------------------------------------

def test_entry_and_ibs_exit_next_day_minimum_hold():
    p = scenario(ibs_path(d250=0.1, d251=0.9))
    w = wfun(panel=p)
    assert positions(w, p) == [(WARM, 0.0), (250, 1.0), (251, 0.0)]     # Ausstieg fruehestens u = t+1


def test_ibs_exit_threshold_is_strict_and_waits_for_first_hit():
    p = scenario(ibs_path(d250=0.1, d251=0.69, d252=0.5, d253=0.71))
    w = wfun(panel=p)
    assert positions(w, p) == [(WARM, 0.0), (250, 1.0), (253, 0.0)]


def test_entry_threshold_is_strict():
    p = scenario(ibs_path(d250=0.2001))
    assert positions(wfun(panel=p), p) == [(WARM, 0.0)]                 # 0.2001 ist nicht < 0.20
    p2 = scenario(ibs_path(d250=0.1999))
    assert positions(wfun(panel=p2), p2) == [(WARM, 0.0), (250, 1.0), (255, 0.0)]


def test_time_exit_after_five_days_without_ibs_signal():
    p = scenario(ibs_path(d250=0.1))
    w = wfun(panel=p)
    assert positions(w, p) == [(WARM, 0.0), (250, 1.0), (255, 0.0)]     # u = t + 5
    # Haltedauer = Ausfuehrung t+1 bis u+1 = 5 Handelstage
    assert 255 + 1 - (250 + 1) == SPEC["params"]["max_hold"]


def test_further_low_ibs_while_long_does_not_reset_hold_counter():
    p = scenario(ibs_path(d250=0.1, d251=0.1, d253=0.05))
    assert positions(wfun(panel=p), p) == [(WARM, 0.0), (250, 1.0), (255, 0.0)]


def test_no_new_entry_on_exit_day_but_possible_next_day():
    # Zeitstopp-Tag 255 hat IBS 0.05: dort noch "gehalten" -> kein neuer Einstieg am selben Tag
    p = scenario(ibs_path(d250=0.1, d255=0.05, d256=0.5))
    assert positions(wfun(panel=p), p) == [(WARM, 0.0), (250, 1.0), (255, 0.0)]
    # Einstiegssignal am Folgetag 256 ist moeglich: Zustand 1 ab 256, Zeitstopp bei 261
    p2 = scenario(ibs_path(d250=0.1, d256=0.05))
    assert positions(wfun(panel=p2), p2) == [(WARM, 0.0), (250, 1.0), (255, 0.0), (256, 1.0), (261, 0.0)]


def test_ibs_exit_day_and_reentry_next_day():
    p = scenario(ibs_path(d250=0.1, d251=0.9, d252=0.1, d253=0.95))
    assert positions(wfun(panel=p), p) == [(WARM, 0.0), (250, 1.0), (251, 0.0), (252, 1.0), (253, 0.0)]


def test_zero_range_day_gives_no_entry_signal():
    p = scenario(ibs_path(d250=np.nan))                       # High == Low == Close
    assert positions(wfun(panel=p), p) == [(WARM, 0.0)]


def test_zero_range_day_while_long_is_no_ibs_exit_but_time_exit_still_applies():
    p = scenario(ibs_path(d250=0.1, d251=np.nan, d252=0.9))
    assert positions(wfun(panel=p), p) == [(WARM, 0.0), (250, 1.0), (252, 0.0)]
    p2 = scenario(ibs_path(d250=0.1, d251=np.nan, d252=np.nan, d253=np.nan, d254=np.nan, d255=np.nan))
    assert positions(wfun(panel=p2), p2) == [(WARM, 0.0), (250, 1.0), (255, 0.0)]


def test_sma200_filter_blocks_entries_in_downtrend_but_variant_without_filter_trades():
    p = scenario(ibs_path(d250=0.1), trend=-0.001)            # Close liegt unter dem SMA200
    assert positions(wfun(panel=p), p) == [(WARM, 0.0)]
    w = weights(p, **params_for("no_sma200"))
    assert positions(w, p) == [(WARM, 0.0), (250, 1.0), (255, 0.0)]


def test_close_equal_to_sma_is_not_above():
    # konstanter Kurs: Close == SMA200 -> strikt nicht darueber, kein Einstieg trotz IBS < 0.2
    p = scenario(ibs_path(d250=0.1), trend=0.0)
    assert positions(wfun(panel=p), p) == [(WARM, 0.0)]


def test_warmup_all_variants_start_on_same_day_and_no_signal_earlier():
    ibs = ibs_path(d100=0.05, d150=0.05)                      # Signale vor dem Warm-up zaehlen nicht
    p = scenario(ibs, trend=0.001)
    for v in VARIANTS:
        w = weights(p, **params_for(v))
        assert w.index[0] == p.close.index[WARM], v
        assert (w.iloc[:, 0].iloc[0] == 0.0), v
    # ohne Filter ebenfalls erst ab Tag WARM (gleicher Bewertungszeitraum)
    w = weights(p, **params_for("no_sma200"))
    assert positions(w, p) == [(WARM, 0.0)]


def test_signal_on_first_valid_day_is_taken():
    p = scenario(ibs_path(**{f"d{WARM}": 0.05}))
    assert positions(wfun(panel=p), p) == [(WARM, 1.0), (WARM + 5, 0.0)]


def test_too_short_history_returns_empty_frame():
    p = scenario(ibs_path(n=150))
    w = wfun(panel=p)
    assert len(w) == 0 and list(w.columns) == ["SPY"]


# --------------------------------------------------------------------------------------
# Connors-RSI(2)-Variante
# --------------------------------------------------------------------------------------

def rsi_scenario():
    """Aufwaertstrend; Tag 250: -5 %, Tag 251: unveraendert, Tag 252: +6 %. Danach wieder Trend."""
    n = 330
    idx = pd.date_range("2020-01-02", periods=n, freq=NYSE_BDAY)
    ret = np.full(n, 0.001)
    ret[250], ret[251], ret[252] = -0.05, 0.0, 0.06
    close = 100.0 * np.exp(np.cumsum(ret))
    f = lambda a: pd.DataFrame({"SPY": a}, index=idx)
    hi = close * 1.004
    lo = close * 0.996
    return OHLCPanel(f(np.r_[close[0], close[:-1]]), f(close), f(hi), f(lo))


def test_connors_variant_entry_on_rsi_drop_and_exit_above_sma5():
    p = rsi_scenario()
    w = weights(p, **params_for("connors_rsi2"))
    assert positions(w, p) == [(WARM, 0.0), (250, 1.0), (252, 0.0)]
    c = p.close["SPY"]
    assert c.iloc[251] < c.iloc[247:252].mean()               # Tag 251: Close noch unter SMA5 -> gehalten
    assert c.iloc[252] > c.iloc[248:253].mean()               # Tag 252: Close ueber SMA5 -> Ausstieg
    assert _wilder_rsi(c, 2).iloc[250] < 10


def test_connors_variant_has_no_time_stop():
    n = 330
    idx = pd.date_range("2020-01-02", periods=n, freq=NYSE_BDAY)
    ret = np.full(n, 0.001)
    ret[250] = -0.05
    ret[251:] = -0.0002                                       # Kurs bleibt unter SMA5, nie darueber
    close = 100.0 * np.exp(np.cumsum(ret))
    f = lambda a: pd.DataFrame({"SPY": a}, index=idx)
    p = OHLCPanel(f(np.r_[close[0], close[:-1]]), f(close), f(close * 1.004), f(close * 0.996))
    w = weights(p, **params_for("connors_rsi2"))
    assert positions(w, p) == [(WARM, 0.0), (250, 1.0)]       # 79 Tage gehalten, kein Zeitstopp
    # derselbe Pfad mit Zeitstopp-Parameter: erster Ausstieg nach 5 Tagen (danach folgen neue RSI-Einstiege)
    w5 = weights(p, **{**params_for("connors_rsi2"), "max_hold": 5})
    assert positions(w5, p)[:3] == [(WARM, 0.0), (250, 1.0), (255, 0.0)]


def test_rsi_entry_respects_sma_filter():
    p = rsi_scenario()
    # Pfad im Abwaertstrend: gleiche Schocktage, aber Trend negativ -> Close unter SMA200
    n = len(p.close)
    ret = np.full(n, -0.001)
    ret[250], ret[251], ret[252] = -0.05, 0.0, 0.06
    close = 100.0 * np.exp(np.cumsum(ret))
    idx = p.close.index
    f = lambda a: pd.DataFrame({"SPY": a}, index=idx)
    q = OHLCPanel(f(np.r_[close[0], close[:-1]]), f(close), f(close * 1.004), f(close * 0.996))
    assert positions(weights(q, **params_for("connors_rsi2")), q) == [(WARM, 0.0)]
    # ohne Filter: stetig fallender Kurs hat RSI(2) = 0 -> Einstieg schon am ersten gueltigen Tag, Ausstieg am +6-%-Tag
    nf = weights(q, **{**params_for("connors_rsi2"), "use_sma_filter": False})
    assert positions(nf, q)[:2] == [(WARM, 1.0), (252, 0.0)]       # danach fallender Kurs: spaeter erneuter Einstieg


# --------------------------------------------------------------------------------------
# Referenz-Vergleich auf Zufallspfaden
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("variant", VARIANTS)
@pytest.mark.parametrize("seed", [0, 1, 2])
def test_matches_independent_reference_on_random_paths(variant, seed):
    p = random_ohlc(seed=seed)
    kw = params_for(variant)
    w = weights(p, **kw)
    ref = reference_states(p.close["SPY"], p.high["SPY"], p.low["SPY"], **kw)
    got = expand(w, p.close.index)
    assert got == ref
    # nicht-trivial: es gab Einstiege und Ausstiege
    changes = sum(1 for a, b in zip(ref, ref[1:]) if a is not None and b is not None and a != b)
    assert changes >= (6 if variant != "connors_rsi2" else 4), (variant, seed, changes)


def test_reference_check_has_signals_in_every_variant_over_all_seeds():
    ent = {v: 0 for v in VARIANTS}
    for seed in range(3):
        p = random_ohlc(seed=seed)
        for v in VARIANTS:
            w = weights(p, **params_for(v))
            ent[v] += int((w.iloc[:, 0] == 1.0).sum())
    assert all(x >= 15 for x in ent.values()), ent


# --------------------------------------------------------------------------------------
# Form, Wertebereich, NaN-Preise
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("variant", VARIANTS)
def test_shape_values_and_exposure(variant):
    p = random_ohlc(names=("SPY", "QQQ", "IWM"), seed=4)
    w = weights(p, **params_for(variant))
    assert list(w.columns) == ["SPY"]                          # genau ein Instrument, nicht gepoolt
    assert w.index.is_monotonic_increasing and w.index.is_unique
    assert w.index.isin(p.close.index).all()
    assert set(np.unique(w.to_numpy())) <= {0.0, 1.0}
    assert (w.sum(axis=1) <= 1.0 + 1e-12).all() and (w >= 0).all().all()   # long-only, kein Hebel
    assert not w.isna().any().any()
    assert w.index[0] == p.close.index[WARM]
    # abwechselnd Einstieg/Ausstieg, nie zweimal derselbe Zustand hintereinander
    s = w.iloc[:, 0].to_numpy()
    assert (s[1:] != s[:-1]).all()


@pytest.mark.parametrize("ticker", ["SPY", "QQQ", "IWM"])
def test_each_instrument_is_run_alone(ticker):
    p = random_ohlc(names=("SPY", "QQQ", "IWM"), seed=5)
    w = weights(p, **{**SPEC["params"], "ticker": ticker})
    assert list(w.columns) == [ticker]
    ref = reference_states(p.close[ticker], p.high[ticker], p.low[ticker])
    assert expand(w, p.close.index) == ref
    # Instrumente unterscheiden sich (nicht heimlich gepoolt)
    other = weights(p, **{**SPEC["params"], "ticker": "SPY" if ticker != "SPY" else "QQQ"})
    assert not w.iloc[:, 0].reset_index(drop=True).equals(other.iloc[:, 0].reset_index(drop=True))


def nan_panel(seed=6):
    """QQQ erst ab Tag 400 gelistet, dazu Luecke mit NaN-Kursen (Open/High/Low/Close) in der Mitte."""
    p = random_ohlc(names=("SPY", "QQQ"), n=1500, seed=seed)
    o, h, l, c = (x.copy() for x in (p.open, p.high, p.low, p.close))
    for df in (o, h, l, c):
        df.iloc[:400, df.columns.get_loc("QQQ")] = np.nan
        df.iloc[900:915, df.columns.get_loc("QQQ")] = np.nan
        df.iloc[1000, df.columns.get_loc("SPY")] = np.nan
    return OHLCPanel(o, c, h, l)


@pytest.mark.parametrize("ticker", ["SPY", "QQQ"])
def test_no_weights_on_nan_prices(ticker):
    p = nan_panel()
    for v in VARIANTS:
        w = weights(p, **{**params_for(v), "ticker": ticker})
        assert len(w) > 0
        px = p.close[ticker].reindex(w.index)
        assert px.notna().all(), (ticker, v)                  # nur Zeilen an Tagen mit Kurs
        assert not w.isna().any().any()
    wq = weights(p, **{**SPEC["params"], "ticker": "QQQ"})
    first_valid = p.close["QQQ"].first_valid_index()
    assert wq.index[0] >= first_valid                          # nichts vor der Listung
    pos = int(p.close["QQQ"].dropna().index.get_loc(wq.index[0]))
    assert pos == WARM                                         # Warm-up zaehlt Kurstage des Instruments


def test_nan_gap_matches_reference_on_valid_days_only():
    p = nan_panel()
    for ticker in ("SPY", "QQQ"):
        c = p.close[ticker].dropna()
        w = weights(p, **{**SPEC["params"], "ticker": ticker})
        ref = reference_states(c, p.high[ticker].reindex(c.index), p.low[ticker].reindex(c.index))
        assert expand(w, c.index) == ref


def test_engine_skips_nothing_and_exposure_is_at_most_one():
    p = random_ohlc(names=("SPY", "QQQ", "IWM"), seed=7)
    w = weights(p, **SPEC["params"])
    res = run_backtest(p, w, exec_mode="open", rf=pd.Series(0.0, index=p.close.index))
    assert res.skipped_orders == 0
    assert res.gross_exposure.max() <= 1.0 + 1e-3
    assert res.n_trades > 10
    assert np.isfinite(res.nav).all() and res.nav.iloc[-1] > 0


def test_engine_executes_entry_after_signal_day_and_exit_after_exit_signal():
    p = scenario(ibs_path(d250=0.1, d251=0.9))
    w = wfun(panel=p)
    res = run_backtest(p, w, exec_mode="open", rf=pd.Series(0.0, index=p.close.index))
    gw = res.weights["SPY"]
    assert gw.iloc[250] == pytest.approx(0.0, abs=1e-12)       # am Signaltag noch keine Position
    assert gw.iloc[251] == pytest.approx(1.0, abs=1e-3)        # Kauf zur Eroeffnung t+1, am Schluss gehalten
    assert gw.iloc[252] == pytest.approx(0.0, abs=1e-12)       # Verkauf zur Eroeffnung u+1
    assert res.n_trades == 2


# --------------------------------------------------------------------------------------
# Kausalitaet
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("variant", VARIANTS)
def test_check_causality_random_panel(variant):
    p = random_ohlc(names=("SPY", "QQQ", "IWM"), seed=8)
    kw = params_for(variant)
    assert check_causality(lambda panel: weights(panel, **kw), p) == []


@pytest.mark.parametrize("variant", VARIANTS)
def test_check_causality_panel_with_nan_gaps(variant):
    p = nan_panel(seed=9)
    kw = params_for(variant)
    assert check_causality(lambda panel: weights(panel, **kw), p) == []
    kq = {**kw, "ticker": "QQQ"}
    assert check_causality(lambda panel: weights(panel, **kq), p) == []


def test_future_shock_does_not_change_past_weights():
    p = random_ohlc(seed=10)
    base = weights(p, **SPEC["params"])
    cut = p.close.index[1200]
    o, h, l, c = (x.copy() for x in (p.open, p.high, p.low, p.close))
    for df in (o, h, l, c):
        df.iloc[1201:] = df.iloc[1201:] * 3.7                 # drastischer Sprung nach dem Stichtag
    shocked = weights(OHLCPanel(o, c, h, l), **SPEC["params"])
    a, b = base.loc[:cut], shocked.loc[:cut]
    pd.testing.assert_frame_equal(a, b)


# --------------------------------------------------------------------------------------
# Panel-Klasse und SPEC
# --------------------------------------------------------------------------------------

def test_ohlcpanel_keeps_high_low_on_truncate_and_slice():
    p = random_ohlc(names=("SPY", "QQQ"), seed=11)
    t = p.truncate(p.close.index[500])
    assert isinstance(t, OHLCPanel) and t.high.index[-1] == p.close.index[500] and t.low.shape == t.close.shape
    s = p.slice(p.close.index[100], p.close.index[300])
    assert isinstance(s, OHLCPanel) and len(s.high) == len(s.close) == 201
    assert isinstance(p, Panel) and p.tickers == ["SPY", "QQQ"]


def test_weights_need_high_low_and_known_ticker():
    p = random_ohlc(seed=12)
    plain = Panel(p.open, p.close)
    with pytest.raises(ValueError, match="High/Low"):
        weights(plain, **SPEC["params"])
    with pytest.raises(KeyError):
        weights(p, **{**SPEC["params"], "ticker": "XYZ"})
    with pytest.raises(ValueError, match="signal"):
        weights(p, **{**SPEC["params"], "signal": "macd"})


def test_spec_contract():
    assert SPEC["id"] == "index_etf_ibs_rsi2_longonly"
    assert mod.__name__.endswith(SPEC["id"])
    assert len(SPEC["variants"]) <= 3                          # vorab festgelegt, hoechstens 3
    assert set(SPEC["tickers"]) == {"SPY", "QQQ", "IWM"}
    p = SPEC["params"]
    assert (p["ibs_entry"], p["ibs_exit"], p["max_hold"], p["sma_window"]) == (0.20, 0.70, 5, 200)
    assert (p["rsi_len"], p["rsi_entry"], p["exit_sma"]) == (2, 10.0, 5)
    for k, v in SPEC["variants"].items():
        assert set(v) <= set(p), k                             # Varianten ueberschreiben nur bekannte Parameter
    assert SPEC["variants"]["connors_rsi2"] == {"signal": "rsi2", "max_hold": None}
    assert SPEC["variants"]["no_sma200"] == {"use_sma_filter": False}
    assert all(SPEC["cost_bps"][t] == 2.0 for t in SPEC["tickers"])   # 2 bp je Seite
    assert callable(mod.load)

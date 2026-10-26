"""Inverse-Volatilitäts-Risk-Parity, ungehebelt, auf dem Multi-Asset-ETF-Universum U9.

Quellen: Asness, Frazzini, Pedersen 2012 ("Leverage Aversion and Risk Parity", FAJ); Anderson, Bianchi,
Goldberg 2012 ("Will My Risk Parity Strategy Outperform?", FAJ); Bruder, Roncalli 2012 ("Managing Risk
Exposures using the Risk Budgeting Approach"). Regeln aus research/strategie-kandidaten.json (Eintrag
ivp_risk_parity_unlevered) und research/families/riskparity.md, Abschnitt S2.

Regel (Spezifikation, unverändert übernommen; Parameter aus der Quelle, keine Optimierung):
    Universum U9 = VTI, EFA, EEM, VNQ, IEF, TLT, TIP, GLD, DBC (angepasste Kurse, auto_adjust).
    Am letzten Handelstag t jedes Monats (qlab.calendar.month_end_flags, kausal), nur Daten bis t:
        sigma_i = Std(Tagesrenditen von i, letzte 756 Handelstage bis inkl. t, ddof=1) * sqrt(252)
                  (mindestens 504 gültige Beobachtungen je Asset)
        w_i     = (1 / sigma_i) / sum_j (1 / sigma_j)                    # Summe w = 1, kein Hebel, kein Short
    Ausführung zur Eröffnung t+1 (Engine), Halten bis zum nächsten Monatsultimo, Gewichte driften.
    Kosten 5 bp je Seite (Engine; Stresstest 15 bp über `run_all.py --cost-mult 3`).

Umsetzung im Engine-Vertrag
* Kein Signal, solange nicht ALLE neun ETFs gehandelt werden und genug Historie haben (Zugangsprüfung unten).
  Fehlende Kurse (NaN) sind nicht handelbar: an einem Tag mit auch nur einem fehlenden Kurs gibt es keine Zeile
  (kein Gewicht auf NaN-Preisen, keine Umverteilung auf die übrigen Titel).
* Fenster = die letzten `window` Zeilen des Panels (Handelstage) einschließlich t. Renditen = close_t/close_{t-1}-1;
  eine Rendite ist NaN, wenn einer der beiden Kurse fehlt (Lücken werden nie gefüllt).

Zugangsprüfung ("Gate", für ALLE Läufe identisch)
    Ein Monatsende ist nur dann ein Signaltag, wenn jedes Asset in den letzten 756 Zeilen mindestens 504 gültige
    Renditen hat (das ist die Anlaufregel der Basisvariante). Dadurch handeln Basis, 1/N-Kontrolle und alle
    Varianten ab demselben ersten Signaltag (ca. 2008-02/03, bestimmt durch den spätesten Titel DBC) und werden
    über dieselbe Stichprobe verglichen. Für die Basisvariante ist das Gate mit `min_obs=504` ohnehin identisch.

Gewichtungsschemata (`scheme`)
    ivp     Inverse Volatilität (Basis, Spezifikation).
    equal   1/N über U9 (die in der Spezifikation geforderte KONTROLLE; zählt NICHT als Variante, siehe CONTROLS).
            Gleiche Signaltage wie die Basis (Gate), Gewichte 1/9.
    erc_lw  Equal Risk Contribution (Bruder/Roncalli) auf der Kovarianz D R* D, mit D = Diagonale der
            Stichproben-Volatilitäten und R* = Ledoit-Wolf-geschrumpfte Korrelation (Ziel: Einheitsmatrix, analytische
            Schrumpfungsintensität nach Ledoit/Wolf 2004 auf den standardisierten Renditen). Löser: konvexe
            Log-Barrieren-Form (Spinu 2013), gedämpftes Newton-Verfahren.
    hrp     Hierarchical Risk Parity (López de Prado 2016): Distanz sqrt((1-rho)/2), Euklid-Abstand der Distanz-
            spalten, Single-Linkage, Quasi-Diagonalisierung (Blattreihenfolge), rekursive Bisektion mit
            Cluster-Varianz aus Inverse-Varianz-Gewichten. Stichproben-Kovarianz (keine Schrumpfung).
    ERC und HRP rechnen mit den Zeilen des Fensters, in denen ALLE neun Renditen gültig sind (gleiche
    Beobachtungen für Kovarianz und Volatilität), und verlangen davon mindestens `min_obs`.

Varianten (vorab festgelegt, laut Spezifikation "sensitivity_variants"; zählen als Versuche; Robustheits-Check,
keine Auswahl der besten):
    erc_lw      ERC mit Ledoit-Wolf-geschrumpfter Korrelation, Fenster 756 (min. 504 vollständige Zeilen).
    hrp_252     Hierarchical Risk Parity, Fenster 252 (min. 168 vollständige Zeilen).
    window_252  Inverse Volatilität mit Fenster 252 statt 756 (min. 168 Beobachtungen je Asset).
Die Mindestbeobachtungen der 252er-Fenster (168 = 2/3 des Fensters, dasselbe Verhältnis wie 504/756) stehen nicht in
der Spezifikation; sie sind eine Festlegung hier und keine Optimierung.

Steuern, Kosten, Ausführung verbucht die Engine; die Strategie liefert nur Zielgewichte (Summe = 1).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from qlab.calendar import month_end_flags

TICKERS = ["VTI", "EFA", "EEM", "VNQ", "IEF", "TLT", "TIP", "GLD", "DBC"]
ANN = 252                  # Handelstage pro Jahr (Annualisierung der Volatilität)
GATE_WINDOW = 756          # Zugangsprüfung: Fenster ...
GATE_MIN_OBS = 504         # ... und Mindestzahl gültiger Renditen je Asset (Anlaufregel der Basis)
SCHEMES = ("ivp", "equal", "erc_lw", "hrp")

SPEC = {
    "id": "ivp_risk_parity_unlevered",
    "name": "Inverse-Volatilitäts-Risk-Parity, ungehebelt (U9-Multi-Asset-ETFs)",
    "family": "riskparity",
    "tickers": TICKERS,
    # Datenstart: DBC startet 2006-02-06 und bestimmt das erste Signal (ca. 2008-02/03). Der frühere Start 2005-01
    # stellt sicher, dass die übrigen Titel bei einem frischen Download das volle 756-Tage-Fenster haben.
    "start": "2005-01-03",
    "sources": [
        "Asness, Frazzini, Pedersen 2012, Leverage Aversion and Risk Parity, "
        "https://www.aqr.com/Insights/Research/Journal-Article/Leverage-Aversion-and-Risk-Parity",
        "Anderson, Bianchi, Goldberg 2012, Will My Risk Parity Strategy Outperform?, "
        "https://rpc.cfainstitute.org/research/financial-analysts-journal/2012/will-my-risk-parity-strategy-outperform",
        "Bruder, Roncalli 2012, Managing Risk Exposures using the Risk Budgeting Approach, "
        "https://mpra.ub.uni-muenchen.de/37246/",
    ],
    "params": {"scheme": "ivp", "window": 756, "min_obs": 504},
    "variants": {
        "erc_lw": {"scheme": "erc_lw"},
        "hrp_252": {"scheme": "hrp", "window": 252, "min_obs": 168},
        "window_252": {"window": 252, "min_obs": 168},
    },
    # Kontrolle der Spezifikation ("1/N-Variante von U9 läuft als zusätzliche Kontrolle mit"): KEINE Variante
    # (Obergrenze 3 ist durch die drei Sensitivitäten belegt). Der Harness liest diesen Schlüssel nicht; abrufbar über
    # weights(panel, **SPEC["controls"]["equal_weight_u9"]).
    "controls": {"equal_weight_u9": {"scheme": "equal"}},
}


# --------------------------------------------------------------------------------------
# Bausteine (reine Funktionen auf Arrays)
# --------------------------------------------------------------------------------------

def ledoit_wolf_corr(rows: np.ndarray):
    """Ledoit-Wolf-geschrumpfte Korrelationsmatrix (Ziel: Einheitsmatrix) und Schrumpfungsintensität delta.

    rows: (n, p) Renditen ohne NaN. Standardisiert mit Mittelwert und Std (ddof=0); die Stichproben-
    korrelation S = z'z/n hat dann Diagonale 1. Analytische Intensität nach Ledoit/Wolf (2004):
        d2 = ||S - m I||_F^2 / p,   m = tr(S)/p
        b2 = min( (1/n^2) sum_k ||z_k z_k' - S||_F^2 / p ,  d2 ),   delta = b2 / d2
        R* = delta * m * I + (1 - delta) * S
    Rückgabe (None, None) bei (numerisch) konstanter Reihe.
    """
    rows = np.asarray(rows, float)
    n, p = rows.shape
    sd0 = rows.std(axis=0, ddof=0)
    if not (np.all(np.isfinite(sd0)) and np.all(sd0 > 1e-12)):      # Rundungsrest einer konstanten Reihe ist > 0
        return None, None
    z = (rows - rows.mean(axis=0)) / sd0
    s = z.T @ z / n
    m = float(np.trace(s)) / p
    d2 = float(np.sum((s - m * np.eye(p)) ** 2)) / p
    # sum_k ||z_k z_k' - S||_F^2 = sum_k ||z_k||^4 - n ||S||_F^2
    b2bar = (float(np.sum(np.sum(z ** 2, axis=1) ** 2)) - n * float(np.sum(s ** 2))) / (n ** 2 * p)
    b2 = min(b2bar, d2)
    delta = 0.0 if d2 <= 0 else b2 / d2
    return delta * m * np.eye(p) + (1.0 - delta) * s, delta


def erc_weights(cov: np.ndarray, tol: float = 1e-12, max_iter: int = 200) -> np.ndarray:
    """Equal-Risk-Contribution-Gewichte (Summe 1) zur Kovarianz `cov` (positiv definit).

    Konvexe Form nach Spinu (2013): minimiere f(x) = x'Sx/2 - (1/n) sum ln x_i über x > 0; die Lösung erfüllt
    x_i (Sx)_i = 1/n, und w = x / sum(x) hat gleiche Risikobeiträge. Gedämpftes Newton-Verfahren mit
    Rückverfolgung (x bleibt positiv, f fällt streng). Bricht mit RuntimeError ab, wenn es nicht konvergiert.
    """
    cov = np.asarray(cov, float)
    n = cov.shape[0]
    b = 1.0 / n

    def f(v):
        return 0.5 * float(v @ cov @ v) - b * float(np.sum(np.log(v)))

    x = 1.0 / np.sqrt(np.diag(cov))
    x = x / np.sqrt(float(x @ cov @ x))                    # Startwert: Inverse Vol, skaliert auf x'Sx = 1
    for _ in range(max_iter):
        sx = cov @ x
        if float(np.max(np.abs(x * sx - b))) < tol:
            return x / x.sum()
        g = sx - b / x
        dx = -np.linalg.solve(cov + np.diag(b / x ** 2), g)
        slope = float(g @ dx)
        t, fx = 1.0, f(x)
        while t > 1e-14:
            xn = x + t * dx
            if np.all(xn > 0) and f(xn) <= fx + 1e-4 * t * slope:
                break
            t *= 0.5
        x = x + t * dx
    sx = cov @ x
    if float(np.max(np.abs(x * sx - b))) < 1e-8:
        return x / x.sum()
    raise RuntimeError("ERC-Löser konvergiert nicht")


def hrp_weights(cov: np.ndarray) -> np.ndarray:
    """Hierarchical-Risk-Parity-Gewichte (López de Prado 2016, Summe 1) zur Kovarianzmatrix `cov`.

    1) Korrelation -> Distanz d = sqrt((1 - rho) / 2); 2) Euklid-Abstand der Distanzspalten, Single-Linkage;
    3) Quasi-Diagonalisierung = Blattreihenfolge des Dendrogramms; 4) rekursive Bisektion: Cluster halbieren,
    Cluster-Varianz mit Inverse-Varianz-Gewichten, alpha = 1 - V0/(V0+V1) auf den linken, 1 - alpha auf den rechten Teil.
    """
    import warnings

    from scipy.cluster.hierarchy import leaves_list, linkage

    cov = np.asarray(cov, float)
    n = cov.shape[0]
    if n == 1:
        return np.ones(1)
    sd = np.sqrt(np.diag(cov))
    corr = np.clip(cov / np.outer(sd, sd), -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)
    dist = np.sqrt((1.0 - corr) / 2.0)
    with warnings.catch_warnings():
        # Absicht (López de Prado): die Distanzmatrix wird als Beobachtungsmatrix übergeben, d.h. Euklid-Abstand der
        # Distanzspalten (d-bar); scipy warnt dabei nur, dass sie wie eine unkomprimierte Distanzmatrix aussieht.
        warnings.simplefilter("ignore")
        order = [int(i) for i in leaves_list(linkage(dist, method="single", metric="euclidean"))]

    def cluster_var(items: list[int]) -> float:
        sub = cov[np.ix_(items, items)]
        ivp = 1.0 / np.diag(sub)
        ivp = ivp / ivp.sum()
        return float(ivp @ sub @ ivp)

    w = np.ones(n)

    def bisect(items: list[int]) -> None:
        if len(items) <= 1:
            return
        h = len(items) // 2
        left, right = items[:h], items[h:]
        v0, v1 = cluster_var(left), cluster_var(right)
        alpha = 1.0 - v0 / (v0 + v1)
        w[left] *= alpha
        w[right] *= 1.0 - alpha
        bisect(left)
        bisect(right)

    bisect(order)
    return w / w.sum()


def _scheme_weights(win: np.ndarray, scheme: str, min_obs: int):
    """Zielgewichte aus dem Renditefenster `win` (Zeilen = Tage, Spalten = U9); None = kein Signal."""
    ok = np.isfinite(win)
    if scheme == "ivp":
        if (ok.sum(axis=0) < min_obs).any():
            return None
        sigma = np.array([win[ok[:, j], j].std(ddof=1) for j in range(win.shape[1])]) * np.sqrt(ANN)
        if not (np.all(np.isfinite(sigma)) and np.all(sigma > 1e-12)):
            return None
        inv = 1.0 / sigma
        return inv / inv.sum()
    rows = win[ok.all(axis=1)]
    if len(rows) < min_obs:
        return None
    sd = rows.std(axis=0, ddof=1) * np.sqrt(ANN)
    if not (np.all(np.isfinite(sd)) and np.all(sd > 1e-12)):
        return None
    if scheme == "erc_lw":
        corr, _ = ledoit_wolf_corr(rows)
        if corr is None:
            return None
        return erc_weights(np.outer(sd, sd) * corr)
    if scheme == "hrp":
        return hrp_weights(np.cov(rows, rowvar=False, ddof=1) * ANN)
    raise ValueError(scheme)


# --------------------------------------------------------------------------------------
# Strategie
# --------------------------------------------------------------------------------------

def weights(panel, scheme: str = "ivp", window: int = 756, min_obs: int = 504) -> pd.DataFrame:
    """Zielgewichte (Summe 1) an jedem Monatsende-Handelstag t mit gültigem Signal, nur aus Daten <= t.

    Keine Zeile, wenn an t ein Kurs fehlt, das Gate (756 Zeilen / 504 Renditen je Asset) nicht erfüllt ist oder das
    Schema zu wenig Beobachtungen im Fenster findet (NaN = nicht handelbar).
    """
    if scheme not in SCHEMES:
        raise ValueError(f"scheme muss eines von {SCHEMES} sein")
    window, min_obs = int(window), int(min_obs)
    if window < 2 or min_obs < 2 or min_obs > window:
        raise ValueError("window >= min_obs >= 2 nötig")

    px = panel.close[TICKERS]
    idx = px.index
    cols = list(TICKERS)
    empty = pd.DataFrame(columns=cols, index=pd.DatetimeIndex([]), dtype=float)
    n = len(idx)
    if n < 3:
        return empty

    close = px.to_numpy(float)
    close = np.where(close > 0, close, np.nan)                         # nicht positive Kurse = ungültig
    ret = np.full_like(close, np.nan)
    with np.errstate(divide="ignore", invalid="ignore"):
        ret[1:] = close[1:] / close[:-1] - 1.0                         # NaN, wenn einer der beiden Kurse fehlt
    flags = month_end_flags(idx).to_numpy()                            # kausal, nicht aus den Daten abgeleitet
    priced = np.isfinite(close).all(axis=1)

    dates, rows = [], []
    for i in np.flatnonzero(flags & priced):
        gate = ret[max(0, i - GATE_WINDOW + 1):i + 1]
        if (np.isfinite(gate).sum(axis=0) < GATE_MIN_OBS).any():
            continue
        if scheme == "equal":
            w = np.full(len(cols), 1.0 / len(cols))
        else:
            w = _scheme_weights(ret[max(0, i - window + 1):i + 1], scheme, min_obs)
            if w is None:
                continue
        dates.append(idx[i])
        rows.append(w)
    if not rows:
        return empty
    return pd.DataFrame(np.vstack(rows), index=pd.DatetimeIndex(dates), columns=cols)

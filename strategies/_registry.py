"""Strategie-Registry.

Jedes Modul in strategies/ (außer Dateien mit führendem Unterstrich) definiert:

    SPEC = {
        "id": "tsmom_12m",                      # eindeutig, snake_case
        "name": "...",
        "family": "tsmom",
        "tickers": ["SPY", ...],                # Yahoo-Ticker ODER Daten über `load()` (siehe unten)
        "start": "2000-01-01",                  # frühester sinnvoller Datenstart
        "sources": ["Autor Jahr Titel URL"],
        "params": {...},                        # FESTE Parameter aus dem Paper
        "variants": {"name": {...}, ...},       # höchstens 3, VORAB festgelegt (zählen als Versuche)
        "cost_bps": {"BTC-USD": 25.0},          # optional, sonst 5 bps
    }

    def weights(panel, **params) -> pd.DataFrame     # siehe qlab/engine.py (Vertrag)

Optional: `def load() -> Panel` für Strategien, die nicht über Yahoo-Ticker laufen
(z. B. Ken-French-Portfolios über qlab.data.panel_from_returns).

Pflicht: `weights` darf nur Daten bis einschließlich des jeweiligen Tages nutzen
(`check_causality` im Harness prüft das), keine Parameteroptimierung auf den Daten.
"""
from __future__ import annotations

import importlib
import pkgutil
from pathlib import Path

import strategies as _pkg


def discover() -> dict[str, object]:
    mods = {}
    for m in pkgutil.iter_modules([str(Path(_pkg.__file__).parent)]):
        if m.name.startswith("_"):
            continue
        mod = importlib.import_module(f"strategies.{m.name}")
        spec = getattr(mod, "SPEC", None)
        if spec is None or not hasattr(mod, "weights"):
            raise ImportError(f"strategies/{m.name}.py braucht SPEC und weights()")
        if spec["id"] in mods:
            raise ImportError(f"doppelte Strategie-ID {spec['id']}")
        mods[spec["id"]] = mod
    return mods

"""Ablauf eines Bot-Laufs: Signal berechnen, Konto/Position lesen, höchstens EINE Order auslösen.

Sicherheitsprinzipien:
* Standard = Papierhandel + Trockenlauf (DRY_RUN=true). Echtes Geld nur mit ALPACA_MODE=live UND
  CONFIRM_LIVE=I_ACCEPT_REAL_MONEY_RISK UND DRY_RUN=false.
* Kein Hebel (Exposure <= 1.0), Kaufbetrag nie größer als das Bar-Guthaben, optionale Obergrenze je Order.
* Bei unvollständigen/veralteten Kursdaten wird NICHT gehandelt (Fehler statt Raten).
* Offene Order vorhanden -> nichts tun (verhindert Doppelkäufe).
* Zustandsbasiert: Jeder Lauf gleicht nur die Position an das Signal an. Läuft er mehrfach am Tag oder fällt
  einer aus, ist das Ergebnis dasselbe.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import requests

from .alpaca import LIVE_URL, PAPER_URL, AlpacaClient, AlpacaError
from .signal import DataError, Signal, decide

NY = ZoneInfo("America/New_York")
LIVE_CONFIRMATION = "I_ACCEPT_REAL_MONEY_RISK"


class ConfigError(Exception):
    pass


def _truthy(v: str | None, default: bool) -> bool:
    if v is None or v.strip() == "":
        return default
    return v.strip().lower() in ("1", "true", "yes", "ja", "on")


def _num(v: str | None):
    return float(v) if v not in (None, "") else None


@dataclass
class Config:
    key_id: str = ""
    secret: str = ""
    mode: str = "paper"                 # paper | live
    confirm_live: str = ""
    trade_symbol: str = "SPY"
    signal_symbol: str = "SPY"
    ma_months: int = 12
    exposure: float = 1.0               # Anteil des Budgets, der investiert wird (max. 1.0)
    allocation_usd: float | None = None  # optional: festes Budget statt gesamtem Kontostand
    dry_run: bool = True
    max_order_usd: float | None = None
    top_up_below: float = 0.5           # Nachkaufen, wenn Position < 50 % des Ziels (z. B. nach Einzahlung)
    min_minutes_after_open: int = 5
    feed: str = "sip"
    enabled: bool = True
    notify_url: str | None = None

    @classmethod
    def from_env(cls, env=None) -> "Config":
        e = os.environ if env is None else env
        return cls(
            key_id=e.get("ALPACA_KEY_ID", ""), secret=e.get("ALPACA_SECRET_KEY", ""),
            mode=(e.get("ALPACA_MODE") or "paper").strip().lower(),
            confirm_live=e.get("CONFIRM_LIVE", ""),
            trade_symbol=(e.get("TRADE_SYMBOL") or "SPY").strip().upper(),
            signal_symbol=(e.get("SIGNAL_SYMBOL") or "SPY").strip().upper(),
            ma_months=int(e.get("MA_MONTHS") or 12),
            exposure=float(e.get("EXPOSURE") or 1.0),
            allocation_usd=_num(e.get("ALLOCATION_USD")),
            dry_run=_truthy(e.get("DRY_RUN"), True),
            max_order_usd=_num(e.get("MAX_ORDER_USD")),
            top_up_below=float(e.get("TOP_UP_BELOW") or 0.5),
            min_minutes_after_open=int(e.get("MIN_MINUTES_AFTER_OPEN") or 5),
            feed=(e.get("DATA_FEED") or "sip").strip().lower(),
            enabled=_truthy(e.get("BOT_ENABLED"), True),
            notify_url=e.get("NOTIFY_WEBHOOK_URL") or None,
        )

    @property
    def base_url(self) -> str:
        return LIVE_URL if self.mode == "live" else PAPER_URL

    def validate(self) -> None:
        if self.mode not in ("paper", "live"):
            raise ConfigError(f"ALPACA_MODE muss 'paper' oder 'live' sein, nicht '{self.mode}'")
        if self.mode == "live" and self.confirm_live != LIVE_CONFIRMATION:
            raise ConfigError(
                "LIVE-Modus verweigert: setze CONFIRM_LIVE=" + LIVE_CONFIRMATION +
                " (echtes Geld, bewusste Entscheidung). Ohne das läuft nur Papierhandel.")
        if not (0.0 < self.exposure <= 1.0):
            raise ConfigError("EXPOSURE muss > 0 und <= 1.0 sein (kein Hebel)")
        if self.ma_months < 2:
            raise ConfigError("MA_MONTHS muss >= 2 sein")
        if self.allocation_usd is not None and self.allocation_usd <= 0:
            raise ConfigError("ALLOCATION_USD muss > 0 sein")
        if self.max_order_usd is not None and self.max_order_usd <= 0:
            raise ConfigError("MAX_ORDER_USD muss > 0 sein")


def _notify(url: str | None, text: str) -> None:
    if not url:
        return
    try:
        requests.post(url, json={"content": text, "text": text}, timeout=10)
    except requests.RequestException as exc:   # Benachrichtigung darf den Lauf nie scheitern lassen
        print(f"[warn] Benachrichtigung fehlgeschlagen: {exc}")


def _minutes_since_open(client, today: date, now_utc: datetime) -> float | None:
    """Minuten seit Handelsbeginn (None, wenn unbekannt). Berücksichtigt Sommer-/Winterzeit via Kalender."""
    try:
        cal = client.calendar_day(today.isoformat())
    except AlpacaError:
        return None
    if not cal or not cal.get("open"):
        return None
    hh, mm = (int(x) for x in cal["open"].split(":")[:2])
    open_ny = datetime(today.year, today.month, today.day, hh, mm, tzinfo=NY)
    return (now_utc - open_ny.astimezone(timezone.utc)).total_seconds() / 60.0


def run_once(client, cfg: Config, now_utc: datetime | None = None) -> dict:
    """Ein kompletter Lauf. Gibt ein Ergebnis-Dict zurück (action, reason, signal, ...)."""
    cfg.validate()
    now_utc = now_utc or datetime.now(timezone.utc)
    today = now_utc.astimezone(NY).date()
    res: dict = {"time_utc": now_utc.strftime("%Y-%m-%d %H:%M:%S"), "mode": cfg.mode, "dry_run": cfg.dry_run,
                 "symbol": cfg.trade_symbol, "action": "NONE", "reason": "", "order": None, "warnings": []}
    if not cfg.enabled:
        res.update(action="SKIP", reason="BOT_ENABLED=false (Notaus aktiv)")
        return res

    acct = client.account()
    if str(acct.get("status", "")).upper() != "ACTIVE" or acct.get("trading_blocked") or acct.get("account_blocked"):
        raise AlpacaError(0, f"Konto nicht handelbar: status={acct.get('status')}, "
                             f"trading_blocked={acct.get('trading_blocked')}, account_blocked={acct.get('account_blocked')}",
                          "account")
    equity = float(acct["equity"])
    cash = float(acct.get("cash", 0.0))
    res.update(equity=equity, cash=cash)

    bars = client.daily_bars(cfg.signal_symbol, feed=cfg.feed)
    if not bars:
        raise DataError("Keine Kursdaten erhalten")
    last_bar = date.fromisoformat(bars[-1][0])
    if (today - last_bar).days > 7:
        raise DataError(f"Kursdaten veraltet: letzter Kurs {last_bar}, heute {today}")
    sig: Signal = decide(bars, today, cfg.ma_months)
    res["signal"] = {"on": sig.on, "month": sig.month, "last_close": sig.last_close, "ma": sig.ma,
                     "distance": sig.distance, "text": sig.describe()}
    if abs(sig.distance) < 0.0015:
        res["warnings"].append(f"Grenzfall: Abstand zum Durchschnitt nur {sig.distance * 100:+.3f} % "
                               "(kleine Kursabweichungen zwischen Datenquellen können das Signal kippen)")

    pos = client.position(cfg.trade_symbol)
    pos_value = float(pos["market_value"]) if pos else 0.0
    res["position_value"] = pos_value
    budget = equity if cfg.allocation_usd is None else min(equity, cfg.allocation_usd)
    target = budget * cfg.exposure
    res["target_value"] = target

    # --- gewünschte Aktion bestimmen ---------------------------------------------------------
    action, notional = "HOLD", 0.0
    if sig.on:
        if pos_value < 1.0:
            action, notional = "BUY", target
        elif pos_value < target * cfg.top_up_below:
            action, notional = "BUY", target - pos_value
            res["warnings"].append(f"Position {pos_value:.2f} < {cfg.top_up_below:.0%} des Ziels {target:.2f}: Nachkauf")
        if action == "BUY":
            if notional > cash:
                res["warnings"].append(f"Kaufbetrag {notional:.2f} auf Bar-Guthaben {cash:.2f} begrenzt (kein Hebel)")
                notional = cash
            if cfg.max_order_usd is not None and notional > cfg.max_order_usd:
                res["warnings"].append(f"Kaufbetrag {notional:.2f} auf MAX_ORDER_USD {cfg.max_order_usd:.2f} begrenzt")
                notional = cfg.max_order_usd
            if notional < 1.0:
                action, notional = "HOLD", 0.0
                res["warnings"].append("Kaufbetrag unter 1 USD — nichts zu tun")
    else:
        if pos_value >= 1.0 or (pos and float(pos.get("qty", 0)) > 0):
            action = "SELL_ALL"
    res.update(action=action, notional=notional)

    if action == "HOLD":
        res["reason"] = ("Signal INVESTIERT, Position vorhanden" if sig.on and pos_value >= 1.0
                         else "Signal CASH, keine Position" if not sig.on else "nichts zu tun")
        return res

    # --- Ausführungsvoraussetzungen ----------------------------------------------------------
    if client.open_orders(cfg.trade_symbol):
        res.update(action="SKIP", reason="offene Order vorhanden — nichts doppelt senden")
        return res
    if cfg.dry_run:
        res["reason"] = f"TROCKENLAUF: würde {action} {notional:.2f} USD {cfg.trade_symbol} ausführen"
        return res
    clock = client.clock()
    if not clock.get("is_open"):
        res.update(action="WAIT", reason="Markt geschlossen — der nächste Lauf übernimmt")
        return res
    mins = _minutes_since_open(client, today, now_utc)
    if mins is not None and mins < cfg.min_minutes_after_open:
        res.update(action="WAIT", reason=f"erst {mins:.0f} min nach Handelsbeginn (Mindestwartezeit {cfg.min_minutes_after_open})")
        return res

    # --- Order senden (genau eine) -----------------------------------------------------------
    if action == "BUY":
        order = client.buy_notional(cfg.trade_symbol, round(notional, 2))
        res["reason"] = f"KAUF {notional:.2f} USD {cfg.trade_symbol} (Signal INVESTIERT)"
    else:
        order = client.close_position(cfg.trade_symbol)
        res["reason"] = f"POSITION GESCHLOSSEN {cfg.trade_symbol} (Signal CASH)"
    res["order"] = {k: (order or {}).get(k) for k in ("id", "status", "side", "notional", "qty", "symbol")}
    return res


def format_result(res: dict) -> str:
    lines = [f"Trendfilter-Bot | {res.get('time_utc')} UTC | {res['mode'].upper()}"
             f"{' | TROCKENLAUF' if res.get('dry_run') else ''}"]
    if res.get("signal"):
        lines.append(res["signal"]["text"])
    if "equity" in res:
        lines.append(f"Konto {res['equity']:.2f} USD (Bar {res.get('cash', 0):.2f}), Position {res.get('position_value', 0):.2f}, "
                     f"Ziel {res.get('target_value', 0):.2f}")
    lines.append(f"Aktion: {res['action']} — {res.get('reason', '')}")
    if res.get("order"):
        lines.append(f"Order: {res['order']}")
    for w in res.get("warnings", []):
        lines.append(f"WARNUNG: {w}")
    return "\n".join(lines)


def run_and_report(cfg: Config, client=None) -> tuple[int, str]:
    """Führt einen Lauf aus, fängt erwartbare Fehler ab. Rückgabe: (Exit-Code, Text)."""
    try:
        cfg.validate()
        client = client or AlpacaClient(cfg.key_id, cfg.secret, cfg.base_url)
        res = run_once(client, cfg)
        text = format_result(res)
        code = 0
        if res["action"] in ("BUY", "SELL_ALL"):          # Order ausgeführt oder (Trockenlauf) vorgeschlagen
            _notify(cfg.notify_url, text)
    except ConfigError as exc:
        text, code = f"KONFIGURATIONSFEHLER: {exc}", 4
        _notify(cfg.notify_url, text)
    except DataError as exc:
        text, code = f"DATENFEHLER (keine Order): {exc}", 2
        _notify(cfg.notify_url, text)
    except AlpacaError as exc:
        text, code = f"ALPACA-FEHLER: {exc}", 3
        _notify(cfg.notify_url, text)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        try:
            with open(summary, "a", encoding="utf-8") as f:
                f.write("```\n" + text + "\n```\n")
        except OSError:
            pass
    return code, text

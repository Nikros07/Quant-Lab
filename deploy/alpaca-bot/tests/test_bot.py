from datetime import datetime, timezone

import pytest

from tests.helpers import make_bars
from trendbot.alpaca import AlpacaError
from trendbot.bot import LIVE_CONFIRMATION, Config, ConfigError, run_and_report, run_once

# 20.10.2026 15:00 UTC = 11:00 New York (Sommerzeit endet erst Anfang November) -> Markt seit 90 min offen
NOW = datetime(2026, 10, 20, 15, 0, tzinfo=timezone.utc)


def bars_for(closes, partial=tuple([100.0] * 15)):
    """Kurse bis September 2026 (abgeschlossen) plus Teilmonat Oktober; `closes` = 14 Monate ab Aug 2025."""
    bars, _ = make_bars(2025, 8, closes, partial_current=list(partial))
    return bars


UP = [100 + 2.0 * i for i in range(14)]               # Aug 2025 .. Sep 2026, steigend  -> investiert
DOWN = [100 + 2.0 * i for i in range(13)] + [80.0]    # letzter Monat bricht ein        -> Cash


class FakeClient:
    def __init__(self, bars, equity=10000.0, cash=10000.0, position_value=0.0, open_orders=None,
                 is_open=True, status="ACTIVE", blocked=False, cal_open="09:30"):
        self._bars, self.equity, self.cash = bars, equity, cash
        self.position_value, self._orders, self.is_open = position_value, open_orders or [], is_open
        self.status, self.blocked, self.cal_open = status, blocked, cal_open
        self.buys, self.closes = [], []

    def account(self):
        return {"status": self.status, "equity": str(self.equity), "cash": str(self.cash),
                "trading_blocked": self.blocked, "account_blocked": False}

    def daily_bars(self, symbol, days_back=460, feed="sip"):
        return self._bars

    def position(self, symbol):
        return ({"market_value": str(self.position_value), "qty": "10"} if self.position_value else None)

    def open_orders(self, symbol):
        return self._orders

    def clock(self):
        return {"is_open": self.is_open}

    def calendar_day(self, day):
        return {"date": day, "open": self.cal_open, "close": "16:00"}

    def buy_notional(self, symbol, usd):
        self.buys.append((symbol, usd))
        return {"id": "o1", "status": "accepted", "side": "buy", "notional": str(usd), "symbol": symbol}

    def close_position(self, symbol):
        self.closes.append(symbol)
        return {"id": "o2", "status": "accepted", "side": "sell", "symbol": symbol, "qty": "10"}


def cfg(**kw):
    base = dict(key_id="k", secret="s", dry_run=False)
    base.update(kw)
    return Config(**base)


def test_signal_on_flat_buys_target_once():
    c = FakeClient(bars_for(UP))
    r = run_once(c, cfg(), NOW)
    assert r["action"] == "BUY" and c.buys == [("SPY", 10000.0)] and not c.closes
    assert r["signal"]["on"] is True


def test_signal_on_with_full_position_holds():
    c = FakeClient(bars_for(UP), position_value=9800.0)
    r = run_once(c, cfg(), NOW)
    assert r["action"] == "HOLD" and not c.buys and not c.closes


def test_signal_off_with_position_closes_once():
    c = FakeClient(bars_for(DOWN), position_value=9800.0)
    r = run_once(c, cfg(), NOW)
    assert r["action"] == "SELL_ALL" and c.closes == ["SPY"] and not c.buys
    assert r["signal"]["on"] is False


def test_signal_off_flat_does_nothing():
    c = FakeClient(bars_for(DOWN))
    r = run_once(c, cfg(), NOW)
    assert r["action"] == "HOLD" and not c.buys and not c.closes


def test_open_order_blocks_everything():
    c = FakeClient(bars_for(UP), open_orders=[{"id": "x"}])
    r = run_once(c, cfg(), NOW)
    assert r["action"] == "SKIP" and not c.buys


def test_dry_run_never_places_orders():
    c = FakeClient(bars_for(UP))
    r = run_once(c, cfg(dry_run=True), NOW)
    assert r["action"] == "BUY" and "TROCKENLAUF" in r["reason"] and not c.buys
    c2 = FakeClient(bars_for(DOWN), position_value=5000.0)
    r2 = run_once(c2, cfg(dry_run=True), NOW)
    assert r2["action"] == "SELL_ALL" and not c2.closes


def test_market_closed_waits():
    c = FakeClient(bars_for(UP), is_open=False)
    r = run_once(c, cfg(), NOW)
    assert r["action"] == "WAIT" and not c.buys


def test_too_early_after_open_waits():
    c = FakeClient(bars_for(UP))
    r = run_once(c, cfg(), datetime(2026, 10, 20, 13, 33, tzinfo=timezone.utc))   # 3 min nach 13:30 UTC
    assert r["action"] == "WAIT" and not c.buys


def test_winter_time_open_is_handled_by_calendar():
    # 14.12.2026 14:34 UTC = 09:34 New York (Winterzeit) -> 4 min nach Handelsbeginn -> warten
    bars, _ = make_bars(2025, 11, [100 + 2.0 * i for i in range(13)], partial_current=[200.0] * 10)
    c = FakeClient(bars)
    r = run_once(c, cfg(), datetime(2026, 12, 14, 14, 34, tzinfo=timezone.utc))
    assert r["action"] == "WAIT"
    r2 = run_once(c, cfg(), datetime(2026, 12, 14, 14, 50, tzinfo=timezone.utc))
    assert r2["action"] == "BUY" and c.buys


def test_exposure_and_cash_limit():
    c = FakeClient(bars_for(UP), equity=10000.0, cash=3000.0)           # Rest steckt woanders
    r = run_once(c, cfg(exposure=0.5), NOW)
    assert c.buys == [("SPY", 3000.0)]                                    # Ziel 5000, aber nie mehr als Bar-Guthaben
    assert any("begrenzt" in w for w in r["warnings"])


def test_allocation_budget_and_exposure():
    c = FakeClient(bars_for(UP), equity=100000.0, cash=100000.0)
    run_once(c, cfg(allocation_usd=2000.0, exposure=0.5), NOW)
    assert c.buys == [("SPY", 1000.0)]


def test_top_up_when_position_far_below_target():
    c = FakeClient(bars_for(UP), position_value=2000.0)
    r = run_once(c, cfg(), NOW)
    assert r["action"] == "BUY" and c.buys == [("SPY", 8000.0)]


def test_max_order_cap():
    c = FakeClient(bars_for(UP))
    run_once(c, cfg(max_order_usd=500.0), NOW)
    assert c.buys == [("SPY", 500.0)]


def test_bot_disabled_is_a_kill_switch():
    c = FakeClient(bars_for(UP))
    r = run_once(c, cfg(enabled=False), NOW)
    assert r["action"] == "SKIP" and not c.buys


def test_borderline_signal_warns():
    # letzter Monat exakt am Durchschnitt (±0,05 %)
    base = [100.0] * 13
    last = (sum(base[-11:]) + 100.0) / 12 * 1.0005
    c = FakeClient(bars_for(base + [last]))
    r = run_once(c, cfg(dry_run=True), NOW)
    assert any("Grenzfall" in w for w in r["warnings"])


def test_blocked_account_raises():
    with pytest.raises(AlpacaError):
        run_once(FakeClient(bars_for(UP), blocked=True), cfg(), NOW)
    with pytest.raises(AlpacaError):
        run_once(FakeClient(bars_for(UP), status="ACCOUNT_UPDATED"), cfg(), NOW)


def test_tiny_buy_amount_is_skipped():
    c = FakeClient(bars_for(UP), equity=10000.0, cash=0.5)
    r = run_once(c, cfg(), NOW)
    assert r["action"] == "HOLD" and not c.buys


# ---- Konfiguration / Sicherheitsschranken -------------------------------------------------------

def test_live_requires_explicit_confirmation():
    with pytest.raises(ConfigError):
        cfg(mode="live").validate()
    cfg(mode="live", confirm_live=LIVE_CONFIRMATION).validate()
    code, text = run_and_report(cfg(mode="live"), client=FakeClient(bars_for(UP)))
    assert code == 4 and "LIVE" in text


@pytest.mark.parametrize("exp", [0.0, -0.1, 1.01, 2.0])
def test_exposure_limits_no_leverage(exp):
    with pytest.raises(ConfigError):
        cfg(exposure=exp).validate()


def test_unknown_mode_rejected():
    with pytest.raises(ConfigError):
        cfg(mode="margin").validate()


def test_defaults_are_safe():
    c = Config.from_env({})
    assert c.mode == "paper" and c.dry_run is True and c.exposure == 1.0


def test_env_parsing():
    c = Config.from_env({"ALPACA_KEY_ID": "a", "ALPACA_SECRET_KEY": "b", "DRY_RUN": "false", "EXPOSURE": "0.8",
                         "ALLOCATION_USD": "1500", "ALPACA_MODE": "PAPER", "BOT_ENABLED": "no"})
    assert (c.dry_run, c.exposure, c.allocation_usd, c.mode, c.enabled) == (False, 0.8, 1500.0, "paper", False)


def test_run_and_report_exit_codes():
    code, text = run_and_report(cfg(), client=FakeClient(bars_for(UP)))
    assert code == 0 and "BUY" in text

    stale, _ = make_bars(2024, 1, [100.0 + i for i in range(14)])        # Daten enden 2025 -> veraltet
    code, text = run_and_report(cfg(), client=FakeClient(stale))
    assert code == 2 and "DATENFEHLER" in text

    class Boom(FakeClient):
        def account(self):
            raise AlpacaError(401, "unauthorized", "account")

    code, text = run_and_report(cfg(), client=Boom(bars_for(UP)))
    assert code == 3 and "ALPACA-FEHLER" in text

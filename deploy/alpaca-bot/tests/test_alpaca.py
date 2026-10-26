"""Alpaca-Client gegen einen gefälschten HTTP-Layer (kein Netz, keine Schlüssel)."""
import pytest

from trendbot import alpaca as al
from trendbot.alpaca import AlpacaClient, AlpacaError


class Resp:
    def __init__(self, status=200, data=None, text=""):
        self.status_code, self._data, self.text = status, data, text or str(data)
        self.content = b"x" if (data is not None or text) else b""

    def json(self):
        return self._data


def client(script):
    """script: Liste von Resp/Exception, die nacheinander zurückgegeben werden; speichert Aufrufe."""
    c = AlpacaClient("key", "secret", retries=3)
    calls = []

    def fake_request(method, url, params=None, json=None, timeout=None):
        calls.append((method, url, params, json))
        item = script.pop(0)
        if isinstance(item, Exception):
            raise item
        return item

    c.s.request = fake_request
    c.calls = calls
    return c


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr(al.time, "sleep", lambda s: None)


def test_requires_keys():
    with pytest.raises(ValueError):
        AlpacaClient("", "")


def test_position_404_means_none():
    c = client([Resp(404, {"code": 40410000, "message": "position does not exist"})])
    assert c.position("SPY") is None


def test_position_other_error_raises():
    c = client([Resp(403, {"message": "forbidden"})])
    with pytest.raises(AlpacaError):
        c.position("SPY")


def test_get_retries_on_503_then_succeeds():
    c = client([Resp(503, text="busy"), Resp(200, {"status": "ACTIVE", "equity": "1"})])
    assert c.account()["status"] == "ACTIVE"
    assert len(c.calls) == 2


def test_post_is_never_retried():
    c = client([Resp(503, text="busy"), Resp(200, {"id": "x"})])
    with pytest.raises(AlpacaError):
        c.buy_notional("SPY", 100.0)
    assert len(c.calls) == 1                                 # kein zweiter Versuch -> kein Doppelkauf


def test_buy_notional_body():
    c = client([Resp(200, {"id": "o"})])
    c.buy_notional("SPY", 1234.567)
    method, url, params, body = c.calls[0]
    assert method == "POST" and url.endswith("/v2/orders")
    assert body == {"symbol": "SPY", "notional": "1234.57", "side": "buy", "type": "market", "time_in_force": "day"}


def test_close_position_uses_delete():
    c = client([Resp(200, {"id": "o"})])
    c.close_position("SPY")
    assert c.calls[0][0] == "DELETE" and c.calls[0][1].endswith("/v2/positions/SPY")


def test_network_error_wrapped():
    import requests
    c = client([requests.ConnectionError("down")] * 3)
    with pytest.raises(AlpacaError):
        c.clock()


def test_daily_bars_paginate_and_parse():
    page1 = Resp(200, {"bars": [{"t": "2026-01-02T05:00:00Z", "c": 100.5}, {"t": "2026-01-05T05:00:00Z", "c": 101.0}],
                       "next_page_token": "abc"})
    page2 = Resp(200, {"bars": [{"t": "2026-01-06T05:00:00Z", "c": 102.25}], "next_page_token": None})
    c = client([page1, page2])
    bars = c.daily_bars("SPY")
    assert bars == [("2026-01-02", 100.5), ("2026-01-05", 101.0), ("2026-01-06", 102.25)]
    assert c.calls[1][2]["page_token"] == "abc"
    assert c.calls[0][2]["adjustment"] == "split" and c.calls[0][2]["feed"] == "sip"


def test_daily_bars_fall_back_to_iex_when_sip_forbidden():
    c = client([Resp(403, {"message": "subscription does not permit"}),
                Resp(200, {"bars": [{"t": "2026-01-02T05:00:00Z", "c": 1.0}], "next_page_token": None})])
    bars = c.daily_bars("SPY")
    assert bars == [("2026-01-02", 1.0)]
    assert c.calls[0][2]["feed"] == "sip" and c.calls[1][2]["feed"] == "iex"


def test_calendar_day_none_on_holiday():
    c = client([Resp(200, [])])
    assert c.calendar_day("2026-12-25") is None

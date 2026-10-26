"""Dünner Alpaca-REST-Client (nur `requests`). Trading-API + historische Tageskurse.

Doku: https://docs.alpaca.markets/ — Papierhandel: https://paper-api.alpaca.markets
Der Client setzt NIE selbst auf "live"; die Basis-URL kommt aus der Konfiguration (siehe bot.py).
"""
from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone

import requests

PAPER_URL = "https://paper-api.alpaca.markets"
LIVE_URL = "https://api.alpaca.markets"
DATA_URL = "https://data.alpaca.markets"


class AlpacaError(Exception):
    def __init__(self, status: int, body: str, where: str = ""):
        super().__init__(f"Alpaca HTTP {status} {where}: {body[:300]}")
        self.status = status
        self.body = body


class AlpacaClient:
    def __init__(self, key_id: str, secret: str, base_url: str = PAPER_URL, data_url: str = DATA_URL,
                 timeout: float = 20.0, retries: int = 3):
        if not key_id or not secret:
            raise ValueError("ALPACA_KEY_ID / ALPACA_SECRET_KEY fehlen")
        self.base_url = base_url.rstrip("/")
        self.data_url = data_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self.s = requests.Session()
        self.s.headers.update({"APCA-API-KEY-ID": key_id, "APCA-API-SECRET-KEY": secret,
                               "Accept": "application/json"})

    # ---- Basis ---------------------------------------------------------------------------
    def _req(self, method: str, url: str, params=None, json=None, retry: bool = True):
        """GET wird bei Netzfehlern/429/5xx wiederholt. Schreibende Aufrufe NIE (kein Doppelkauf)."""
        attempts = self.retries if (retry and method == "GET") else 1
        last = None
        for i in range(attempts):
            try:
                r = self.s.request(method, url, params=params, json=json, timeout=self.timeout)
            except requests.RequestException as exc:
                last = exc
                if i + 1 < attempts:
                    time.sleep(1.5 * (i + 1))
                    continue
                raise AlpacaError(0, f"Netzwerkfehler: {exc}", url) from exc
            if r.status_code in (429, 500, 502, 503, 504) and i + 1 < attempts:
                time.sleep(1.5 * (i + 1))
                continue
            if r.status_code >= 400:
                raise AlpacaError(r.status_code, r.text, url)
            if not r.content:
                return None
            return r.json()
        raise AlpacaError(0, f"Netzwerkfehler: {last}", url)

    # ---- Trading ---------------------------------------------------------------------------
    def account(self) -> dict:
        return self._req("GET", f"{self.base_url}/v2/account")

    def clock(self) -> dict:
        return self._req("GET", f"{self.base_url}/v2/clock")

    def calendar_day(self, day: str) -> dict | None:
        """Handelskalender für einen Tag ('YYYY-MM-DD'); None, wenn kein Handelstag."""
        out = self._req("GET", f"{self.base_url}/v2/calendar", params={"start": day, "end": day})
        return out[0] if out else None

    def position(self, symbol: str) -> dict | None:
        try:
            return self._req("GET", f"{self.base_url}/v2/positions/{symbol}")
        except AlpacaError as exc:
            if exc.status == 404:
                return None
            raise

    def open_orders(self, symbol: str) -> list[dict]:
        return self._req("GET", f"{self.base_url}/v2/orders",
                         params={"status": "open", "symbols": symbol, "limit": 50}) or []

    def buy_notional(self, symbol: str, usd: float) -> dict:
        """Marktorder über einen Dollarbetrag (Bruchstücke möglich), nur für den laufenden Handelstag."""
        body = {"symbol": symbol, "notional": f"{usd:.2f}", "side": "buy", "type": "market",
                "time_in_force": "day"}
        return self._req("POST", f"{self.base_url}/v2/orders", json=body, retry=False)

    def close_position(self, symbol: str) -> dict:
        return self._req("DELETE", f"{self.base_url}/v2/positions/{symbol}", retry=False)

    # ---- Daten ---------------------------------------------------------------------------
    def daily_bars(self, symbol: str, days_back: int = 460, feed: str = "sip") -> list[tuple[str, float]]:
        """Tägliche Schlusskurse (nur Splits angepasst = Preisreihe, ohne Dividenden), aufsteigend.

        Das kostenlose Konto darf SIP-Historie nur mit 15 Minuten Verzögerung abfragen; `end` liegt
        deshalb 20 Minuten in der Vergangenheit. Wird SIP abgelehnt, fällt der Client auf IEX zurück.
        """
        now = datetime.now(timezone.utc)
        params = {"timeframe": "1Day", "start": (now - timedelta(days=days_back)).strftime("%Y-%m-%d"),
                  "end": (now - timedelta(minutes=20)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                  "adjustment": "split", "feed": feed, "limit": 10000, "sort": "asc"}
        bars: list[tuple[str, float]] = []
        try:
            while True:
                out = self._req("GET", f"{self.data_url}/v2/stocks/{symbol}/bars", params=params)
                for b in (out or {}).get("bars") or []:
                    bars.append((b["t"][:10], float(b["c"])))
                tok = (out or {}).get("next_page_token")
                if not tok:
                    break
                params["page_token"] = tok
        except AlpacaError as exc:
            if feed == "sip" and exc.status in (401, 403, 422):
                return self.daily_bars(symbol, days_back, feed="iex")
            raise
        return bars

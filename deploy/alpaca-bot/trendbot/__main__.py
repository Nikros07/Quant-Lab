"""Aufruf:  python -m trendbot [run|signal|status] [--dry-run]

run     Signal berechnen und Position angleichen (Standard; ohne weiteres nur Trockenlauf)
signal  nur Signal ausgeben (keine Konto-/Positionsabfrage, keine Order)
status  Konto, Position und Signal anzeigen (keine Order)
"""
import argparse
import sys

from .alpaca import AlpacaClient, AlpacaError
from .bot import Config, ConfigError, run_and_report
from .signal import DataError, decide


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser(prog="trendbot")
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "signal", "status"])
    ap.add_argument("--dry-run", action="store_true", help="erzwingt Trockenlauf (keine Order)")
    a = ap.parse_args(argv)
    cfg = Config.from_env()
    if a.dry_run:
        cfg.dry_run = True
    if a.cmd == "run":
        code, text = run_and_report(cfg)
        print(text)
        return code
    try:
        cfg.validate()
        client = AlpacaClient(cfg.key_id, cfg.secret, cfg.base_url)
        from datetime import datetime, timezone
        from .bot import NY
        today = datetime.now(timezone.utc).astimezone(NY).date()
        sig = decide(client.daily_bars(cfg.signal_symbol, feed=cfg.feed), today, cfg.ma_months)
        print(sig.describe())
        if a.cmd == "status":
            acct = client.account()
            pos = client.position(cfg.trade_symbol)
            print(f"Konto {acct.get('status')}: Equity {acct.get('equity')} USD, Bar {acct.get('cash')} USD ({cfg.mode})")
            print(f"Position {cfg.trade_symbol}: " + (f"{pos['qty']} Stück, Wert {pos['market_value']} USD" if pos else "keine"))
        return 0
    except (ConfigError, DataError, AlpacaError, ValueError) as exc:
        print(f"FEHLER: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())

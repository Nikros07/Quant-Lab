//+------------------------------------------------------------------+
//|  TrendFilter_MA12.mq5                                            |
//|  Quant-Lab: monatlicher Trendfilter "Aktienindex oder Cash"      |
//|                                                                  |
//|  Regel (aus Backtest 1993-2022 auf SPY, 1930-2022 auf US-Markt): |
//|    P   = Schlusskurs des letzten ABGESCHLOSSENEN Monats         |
//|    MA  = Mittel der letzten 12 abgeschlossenen Monatsschlüsse    |
//|    P >= MA  -> long (voll investiert, kein Hebel)                |
//|    P <  MA  -> flat (Cash)                                       |
//|  Entscheidung nur an Monatsgrenzen, sonst ändert sich nichts.    |
//|                                                                  |
//|  Quellen: Faber 2007 (SSRN 962461); Neely/Rapach/Tu/Zhou 2014.   |
//|  KEINE Anlageberatung. Erst im Demokonto laufen lassen.          |
//+------------------------------------------------------------------+
//| Änderungen v1.10 (Handelslogik, Signal und Gating UNVERÄNDERT):  |
//|  - OnInit: Symboldaten ins Journal (Digits, Kontraktgröße, Swap, |
//|    Volumen-Min/Step) plus Hinweis zu Haltekosten                 |
//|  - InpLogCsv: Entscheidungsprotokoll TrendFilter_MA12_log.csv    |
//|    (FILE_COMMON; nur bei Monatswechsel oder ausgelöster Order)   |
//|  - OnTester(): Recovery Factor als Hilfswert, keine Optimierung  |
//+------------------------------------------------------------------+
//| Änderungen v2.00 (Basis bei Standard-Eingaben IDENTISCH zu 1.10): |
//|  Zusätze, alle Standard AUS (Lab-Test H11, 2026-10-23: schlechter |
//|  als die Basis, deshalb nur als Schalter):                        |
//|  - InpUseVol: Gewicht = min(InpMaxLev, Ziel-Vol / EWMA-Vol),      |
//|    monatlich nachgeführt (nur bei > 15 % Abweichung)              |
//|  - InpUseTrail: Trailing-Stop, sinkt nie. InpTrailMode 1 = Stufen: |
//|    Anfangs-Stop E - R (R = m * Vol / Wurzel(12) * E); bei Höchst- |
//|    kurs >= E + k*R rückt der Stop auf E + (k-1)*R (Break-even bei |
//|    +1R, dann je +1R). Modus 0 = Chandelier (HH * (1 - m*Vol/W12)) |
//|  - InpUseRR: Gewinnziel (R:R * anfänglicher Stop-Abstand)         |
//|  Nach Stop/Ziel Wiedereinstieg erst im nächsten Monat.            |
//|  Eigene Protokolldatei TrendFilter_MA12_v2_log.csv                |
//+------------------------------------------------------------------+
#property copyright "Quant-Lab"
#property version   "2.00"
#property description "Monatlicher 12-Monats-Trendfilter: Index long oder flat (v2 mit optionalen Zusätzen)."

#include <Trade\Trade.mqh>

input string InpSymbol       = "";       // Handelssymbol (leer = Symbol des Charts), z. B. US500
input int    InpMaMonths     = 12;       // Länge des Durchschnitts in Monaten (Studie: 12)
input double InpExposure     = 1.0;      // Nominalwert / Kontostand (1.0 = voll investiert, KEIN Hebel)
input double InpFixedLots    = 0.0;      // >0: feste Lotgröße statt Exposure
input long   InpMagic        = 20261013; // Magic Number
input int    InpSlippage     = 30;       // erlaubte Abweichung in Punkten
input bool   InpTradingOn    = true;     // false = nur Signal ins Journal schreiben
input bool   InpLogCsv       = true;     // Entscheidungen in CSV protokollieren
input bool   InpUseVol       = false;    // Zusatz 1: Gewicht nach Volatilität (Standard AUS)
input double InpTargetVol    = 15.0;     // Ziel-Volatilität p. a. in %
input double InpMaxLev       = 1.0;      // Höchstgewicht (1.0 = kein Hebel, max 1.5)
input bool   InpUseTrail     = false;    // Zusatz 2: Trailing-Stop (Standard AUS)
input int    InpTrailMode    = 1;        // Trailing-Art: 1 = Stufen (Break-even, dann je +1R), 0 = Chandelier
input double InpTrailMult    = 2.0;      // Stop-Abstand = Vielfaches von Vol / Wurzel(12)
input bool   InpUseRR        = false;    // Zusatz 3: Gewinnziel R:R (Standard AUS)
input double InpRR           = 3.0;      // Gewinnziel = R:R * anfänglicher Stop-Abstand

CTrade   g_trade;
string   g_sym;
datetime g_lastBar = 0;
int      g_logMonthKey = 0;              // YYYYMM des zuletzt protokollierten Eintrags (0 = noch keiner in diesem Lauf)
const string LOG_FILE = "TrendFilter_MA12_v2_log.csv";
double   g_hh = 0.0;                     // höchster Schlusskurs seit Einstieg (Trailing-Stop)
double   g_riskFrac = 0.0;               // anfänglicher Stop-Abstand als Bruchteil des Kurses (Gewinnziel)
double   g_entryPrice = 0.0;             // Einstiegskurs der Position
double   g_stopLvl = 0.0;                // aktuelles Stop-Niveau (sinkt nie, 0 = keins)
bool     g_wasLong = false;              // EA hielt gestern eine Position (Stop-Erkennung)
int      g_blockKey = 0;                 // Monat (YYYYMM), in dem nach Stop/Ziel kein Wiedereinstieg erlaubt ist
int      g_rebalKey = 0;                 // Monat der letzten Gewichtsanpassung

//+------------------------------------------------------------------+
int OnInit()
  {
   g_sym = (InpSymbol == "") ? _Symbol : InpSymbol;
   if(!SymbolSelect(g_sym, true))
     {
      Print("Symbol nicht verfügbar: ", g_sym);
      return INIT_FAILED;
     }
   if(InpMaMonths < 2 || InpMaMonths > 60)
     {
      Print("InpMaMonths muss zwischen 2 und 60 liegen");
      return INIT_PARAMETERS_INCORRECT;
     }
   if(InpMaxLev < 0.5 || InpMaxLev > 1.5 || InpTargetVol < 5.0 || InpTargetVol > 40.0 || InpTrailMult < 0.5 || InpRR < 1.0 || (InpTrailMode != 0 && InpTrailMode != 1))
     {
      Print("Eingaben außerhalb des erlaubten Bereichs (MaxLev 0.5-1.5, Ziel-Vol 5-40, Trail >= 0.5, R:R >= 1)");
      return INIT_PARAMETERS_INCORRECT;
     }
   // Symboldaten nur ausgeben (Plausibilität, Haltekosten); ändert nichts am Handel
   PrintFormat("Symboldaten %s: DIGITS=%d CONTRACT_SIZE=%.2f SWAP_MODE=%d SWAP_LONG=%.4f SWAP_SHORT=%.4f VOLUME_MIN=%.4f VOLUME_STEP=%.4f",
               g_sym,
               SymbolInfoInteger(g_sym, SYMBOL_DIGITS),
               SymbolInfoDouble(g_sym, SYMBOL_TRADE_CONTRACT_SIZE),
               SymbolInfoInteger(g_sym, SYMBOL_SWAP_MODE),
               SymbolInfoDouble(g_sym, SYMBOL_SWAP_LONG),
               SymbolInfoDouble(g_sym, SYMBOL_SWAP_SHORT),
               SymbolInfoDouble(g_sym, SYMBOL_VOLUME_MIN),
               SymbolInfoDouble(g_sym, SYMBOL_VOLUME_STEP));
   Print("Hinweis: Long-Swap/Finanzierung beachten – bei Index-CFDs können die Haltekosten den Vorteil der Strategie auffressen.");
   g_trade.SetExpertMagicNumber(InpMagic);
   g_trade.SetDeviationInPoints(InpSlippage);
   g_trade.SetAsyncMode(false);
   PrintFormat("TrendFilter_MA12 v2 gestartet: %s, MA=%d Monate, Exposure=%.2f, Handel=%s | Vol=%s Trail=%s RR=%s",
               g_sym, InpMaMonths, InpExposure, InpTradingOn ? "AN" : "AUS (nur Signal)",
               InpUseVol ? "AN" : "aus", InpUseTrail ? "AN" : "aus", InpUseRR ? "AN" : "aus");
   return INIT_SUCCEEDED;
  }

//+------------------------------------------------------------------+
//| Signal aus den letzten InpMaMonths ABGESCHLOSSENEN Monatsbars.   |
//| Rückgabe: 1 = long, 0 = flat, -1 = nicht genug Daten             |
//+------------------------------------------------------------------+
int ComputeSignal(double &last_close, double &ma)
  {
   double c[];
   ArraySetAsSeries(c, true);
   int got = CopyClose(g_sym, PERIOD_MN1, 1, InpMaMonths, c);   // Start bei Shift 1 = letzter abgeschlossener Monat
   if(got < InpMaMonths)
     {
      PrintFormat("Zu wenig Monatsdaten für %s: %d von %d (Historie im Terminal nachladen)", g_sym, got, InpMaMonths);
      return -1;
     }
   double sum = 0.0;
   for(int i = 0; i < InpMaMonths; i++)
      sum += c[i];
   ma = sum / InpMaMonths;
   last_close = c[0];
   return (last_close >= ma) ? 1 : 0;
  }

//+------------------------------------------------------------------+
//| Annualisierte EWMA-Volatilität der D1-Schlusskurse (Halbwertszeit |
//| 20 Tage), nur abgeschlossene Tage. 0 = zu wenig Daten.           |
//+------------------------------------------------------------------+
double EwmaVol()
  {
   double c[];
   ArraySetAsSeries(c, true);
   int got = CopyClose(g_sym, PERIOD_D1, 1, 260, c);   // Shift 1 = gestern, c[0] neueste
   if(got < 60)
      return 0.0;
   double lambda = MathPow(0.5, 1.0 / 20.0);
   double v = 0.0;
   bool   init = false;
   for(int i = got - 2; i >= 0; i--)                    // vom ältesten zum neuesten
     {
      if(c[i + 1] <= 0.0 || c[i] <= 0.0)
         continue;
      double r = MathLog(c[i] / c[i + 1]);
      v = init ? lambda * v + (1.0 - lambda) * r * r : r * r;
      init = true;
     }
   return init ? MathSqrt(v * 252.0) : 0.0;
  }

int MonthKey(const datetime t)
  {
   MqlDateTime dt;
   TimeToStruct(t, dt);
   return dt.year * 100 + dt.mon;
  }

//+------------------------------------------------------------------+
//| Stop und Ziel auf alle Positionen des EA setzen (0 = keine Marke)|
//+------------------------------------------------------------------+
void ApplySlTp(const double sl, const double tp)
  {
   int digits = (int)SymbolInfoInteger(g_sym, SYMBOL_DIGITS);
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong t = PositionGetTicket(i);
      if(t == 0 || PositionGetString(POSITION_SYMBOL) != g_sym || PositionGetInteger(POSITION_MAGIC) != InpMagic)
         continue;
      double nsl = (sl > 0.0) ? NormalizeDouble(sl, digits) : 0.0;
      double ntp = (tp > 0.0) ? NormalizeDouble(tp, digits) : 0.0;
      if(!g_trade.PositionModify(t, nsl, ntp))
         PrintFormat("SL/TP setzen fehlgeschlagen: %d %s", g_trade.ResultRetcode(), g_trade.ResultRetcodeDescription());
     }
  }

//+------------------------------------------------------------------+
bool FindPosition(ulong &ticket, double &volume)
  {
   ticket = 0;
   volume = 0.0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong t = PositionGetTicket(i);
      if(t == 0)
         continue;
      if(PositionGetString(POSITION_SYMBOL) != g_sym)
         continue;
      if(PositionGetInteger(POSITION_MAGIC) != InpMagic)
         continue;
      if(PositionGetInteger(POSITION_TYPE) != POSITION_TYPE_BUY)
         continue;
      ticket = t;
      volume += PositionGetDouble(POSITION_VOLUME);
     }
   return (ticket != 0);
  }

//+------------------------------------------------------------------+
//| Lotgröße so, dass Nominalwert ~ Exposure * Kontostand            |
//+------------------------------------------------------------------+
double CalcLots(const double weight)
  {
   double vmin  = SymbolInfoDouble(g_sym, SYMBOL_VOLUME_MIN);
   double vmax  = SymbolInfoDouble(g_sym, SYMBOL_VOLUME_MAX);
   double vstep = SymbolInfoDouble(g_sym, SYMBOL_VOLUME_STEP);
   double lots;
   if(InpFixedLots > 0.0)
      lots = InpFixedLots;
   else
     {
      double price = SymbolInfoDouble(g_sym, SYMBOL_ASK);
      double tv    = SymbolInfoDouble(g_sym, SYMBOL_TRADE_TICK_VALUE);
      double ts    = SymbolInfoDouble(g_sym, SYMBOL_TRADE_TICK_SIZE);
      if(price <= 0.0 || tv <= 0.0 || ts <= 0.0)
         return 0.0;
      double notional_per_lot = price * (tv / ts);              // in Kontowährung
      lots = AccountInfoDouble(ACCOUNT_EQUITY) * InpExposure * weight / notional_per_lot;
     }
   if(vstep > 0.0)
      lots = MathFloor(lots / vstep) * vstep;
   lots = MathMax(vmin, MathMin(vmax, lots));
   return NormalizeDouble(lots, 2);
  }

//+------------------------------------------------------------------+
//| CSV-Protokoll: eine Zeile pro Handelstag-Entscheidung, aber nur, |
//| wenn der Monat wechselt oder in diesem Lauf geordert wird.       |
//| Datei: Terminal\Common\Files (FILE_COMMON). Fehler nur Print.    |
//| Der EA läuft bei Fehlern unverändert weiter.                     |
//+------------------------------------------------------------------+
void LogDecision(const double last_close, const double ma, const int sig, const string action)
  {
   if(!InpLogCsv)
      return;
   datetime bar = iTime(g_sym, PERIOD_D1, 0);
   if(bar == 0)
      return;
   MqlDateTime dt;
   TimeToStruct(bar, dt);
   int key = dt.year * 100 + dt.mon;                 // YYYYMM des aktuellen D1-Balkens
   if(key == g_logMonthKey && action == "HOLD")
      return;                                        // gleicher Monat wie letzter Eintrag und keine Order

   int h = FileOpen(LOG_FILE, FILE_READ | FILE_WRITE | FILE_CSV | FILE_ANSI | FILE_COMMON | FILE_SHARE_READ);
   if(h == INVALID_HANDLE)
     {
      PrintFormat("CSV-Log: Datei %s nicht öffnbar (Fehler %d)", LOG_FILE, GetLastError());
      return;
     }
   if(FileSize(h) == 0)
      FileWriteString(h, "date;symbol;month_close;ma;signal;action\r\n");   // Kopfzeile nur beim Anlegen
   FileSeek(h, 0, SEEK_END);
   string line = StringFormat("%s;%s;%.2f;%.2f;%s;%s\r\n",
                              TimeToString(bar, TIME_DATE), g_sym, last_close, ma,
                              (sig == 1 ? "LONG" : "FLAT"), action);
   if(FileWriteString(h, line) == 0)
      PrintFormat("CSV-Log: Schreiben fehlgeschlagen (Fehler %d)", GetLastError());
   FileClose(h);
   g_logMonthKey = key;
  }

//+------------------------------------------------------------------+
void OnTick()
  {
   // höchstens einmal pro neuem Tagesbalken prüfen; das Signal ändert sich nur an Monatsgrenzen
   datetime bar = iTime(g_sym, PERIOD_D1, 0);
   if(bar == 0 || bar == g_lastBar)
      return;
   g_lastBar = bar;
   int key = MonthKey(bar);

   double last_close = 0.0, ma = 0.0;
   int sig = ComputeSignal(last_close, ma);
   if(sig < 0)
     {
      g_lastBar = 0;                                             // nächsten Tick erneut versuchen
      return;
     }

   ulong  ticket;
   double vol;
   bool   have = FindPosition(ticket, vol);
   double dvol = EwmaVol();
   double w = 1.0;
   if(InpUseVol && dvol > 0.0)
      w = MathMin(InpMaxLev, (InpTargetVol / 100.0) / dvol);

   // Stop/Ziel hat die Position beendet (EA hat sie nicht selbst geschlossen): Wiedereinstieg erst im nächsten Monat
   if(g_wasLong && !have)
     {
      g_wasLong = false;
      g_stopLvl = 0.0;
      g_blockKey = MonthKey(iTime(g_sym, PERIOD_D1, 1));
      PrintFormat("Position durch Stop/Ziel beendet, Wiedereinstieg erst nach Monat %d", g_blockKey);
     }
   PrintFormat("Signal %s: Monatsschluss %.2f %s MA%d %.2f -> %s | Position: %s",
               g_sym, last_close, (sig == 1 ? ">=" : "<"), InpMaMonths, ma,
               (sig == 1 ? "LONG" : "FLAT"), (have ? "long" : "keine"));
   Comment(StringFormat("TrendFilter MA%d | %s\nMonatsschluss %.2f  MA %.2f\nSignal: %s  Position: %s",
                        InpMaMonths, g_sym, last_close, ma, (sig == 1 ? "LONG" : "FLAT"), (have ? "long" : "keine")));

   string action = "HOLD";                       // Protokoll-Aktion dieses Durchlaufs (nur für CSV)
   if(!InpTradingOn)
     {
      LogDecision(last_close, ma, sig, action);
      return;
     }

   if(sig == 1 && !have && key != g_blockKey)
     {
      double lots = CalcLots(w);
      if(lots <= 0.0)
        {
         Print("Lotgröße 0 – Kauf übersprungen");
         LogDecision(last_close, ma, sig, action);
         return;
        }
      double margin = 0.0;
      if(OrderCalcMargin(ORDER_TYPE_BUY, g_sym, lots, SymbolInfoDouble(g_sym, SYMBOL_ASK), margin) &&
         margin > AccountInfoDouble(ACCOUNT_MARGIN_FREE))
        {
         PrintFormat("Nicht genug freie Margin (%.2f nötig) – Kauf übersprungen", margin);
         LogDecision(last_close, ma, sig, action);
         return;
        }
      if(g_trade.Buy(lots, g_sym, 0.0, 0.0, 0.0, "TrendFilter MA12"))
        {
         PrintFormat("LONG eröffnet: %.2f Lots @ %.2f (Gewicht %.2f, Vol %.1f %%)", lots, g_trade.ResultPrice(), w, dvol * 100.0);
         action = "BUY";
         g_wasLong = true;
         g_entryPrice = g_trade.ResultPrice();
         g_hh = g_entryPrice;
         g_rebalKey = key;
         g_riskFrac = (dvol > 0.0) ? InpTrailMult * dvol / MathSqrt(12.0) : 0.0;
         double sl0 = (InpUseTrail && g_riskFrac > 0.0) ? g_hh * (1.0 - g_riskFrac) : 0.0;
         g_stopLvl = sl0;
         double tp0 = (InpUseRR && g_riskFrac > 0.0) ? g_entryPrice * (1.0 + InpRR * g_riskFrac) : 0.0;
         if(sl0 > 0.0 || tp0 > 0.0)
            ApplySlTp(sl0, tp0);
        }
      else
        {
         PrintFormat("Kauf fehlgeschlagen: %d %s", g_trade.ResultRetcode(), g_trade.ResultRetcodeDescription());
         g_lastBar = 0;                                          // beim nächsten Tick erneut versuchen
        }
     }
   else if(sig == 0 && have)
     {
      if(g_trade.PositionClose(ticket))
        {
         PrintFormat("Position geschlossen (Signal FLAT) @ %.2f", g_trade.ResultPrice());
         action = "CLOSE";
         g_wasLong = false;
         g_stopLvl = 0.0;
        }
      else
        {
         PrintFormat("Schließen fehlgeschlagen: %d %s", g_trade.ResultRetcode(), g_trade.ResultRetcodeDescription());
         g_lastBar = 0;
        }
     }
   // Position bleibt offen: Trailing-Stop nachführen und Gewicht monatlich anpassen
   if(have && sig == 1 && action == "HOLD")
     {
      if(InpUseTrail && (InpTrailMode == 1 || dvol > 0.0))
        {
         double c1 = iClose(g_sym, PERIOD_D1, 1);
         if(c1 > g_hh)
            g_hh = c1;
         double cand = 0.0;
         if(InpTrailMode == 0)
            cand = g_hh * (1.0 - InpTrailMult * dvol / MathSqrt(12.0));
         else if(g_riskFrac > 0.0 && g_entryPrice > 0.0)
           {
            double rUnit = g_riskFrac * g_entryPrice;
            double kStep = MathFloor((g_hh - g_entryPrice) / rUnit);
            cand = (kStep >= 1.0) ? g_entryPrice + (kStep - 1.0) * rUnit : g_entryPrice - rUnit;
           }
         if(cand > g_stopLvl)
            g_stopLvl = cand;                    // Stop sinkt nie
         double sl = g_stopLvl;
         double tp = (InpUseRR && g_riskFrac > 0.0) ? g_entryPrice * (1.0 + InpRR * g_riskFrac) : 0.0;
         if(sl >= SymbolInfoDouble(g_sym, SYMBOL_BID))
           {
            if(g_trade.PositionClose(ticket))
              {
               PrintFormat("Trailing-Stop erreicht (Stop %.2f), Position geschlossen", sl);
               action = "STOP";
               g_wasLong = false;
               g_stopLvl = 0.0;
               g_blockKey = key;
              }
           }
         else
            ApplySlTp(sl, tp);
        }
      if(InpUseVol && action == "HOLD" && key != g_rebalKey)
        {
         g_rebalKey = key;
         double target = CalcLots(w);
         double diff = target - vol;
         double vstep = SymbolInfoDouble(g_sym, SYMBOL_VOLUME_STEP);
         if(MathAbs(diff) > 0.15 * vol && vstep > 0.0)
           {
            diff = MathFloor(MathAbs(diff) / vstep) * vstep * (diff > 0.0 ? 1.0 : -1.0);
            if(diff > 0.0)
              {
               if(g_trade.Buy(diff, g_sym, 0.0, 0.0, 0.0, "TrendFilter MA12 +"))
                  action = "ADD";
              }
            else if(diff < 0.0 && PositionSelectByTicket(ticket))
              {
               double tv = MathMin(-diff, PositionGetDouble(POSITION_VOLUME));
               if(g_trade.PositionClosePartial(ticket, tv))
                  action = "REDUCE";
              }
           }
        }
     }
   LogDecision(last_close, ma, sig, action);
  }

//+------------------------------------------------------------------+
//| OnTester: Recovery Factor als Hilfswert für Optimierungen.       |
//| Die Strategie braucht KEINE Optimierung: die 12 Monate sind aus  |
//| der Literatur fest vorgegeben. Der Wert dient nur der groben     |
//| Einordnung im Tester, nicht der Auswahl von Parametern.          |
//+------------------------------------------------------------------+
double OnTester()
  {
   double profit = TesterStatistics(STAT_PROFIT);
   double dd     = TesterStatistics(STAT_EQUITY_DD);     // maximaler Equity-Drawdown, absolut
   return profit / MathMax(1.0, dd);
  }

void OnDeinit(const int reason)
  {
   Comment("");
  }
//+------------------------------------------------------------------+

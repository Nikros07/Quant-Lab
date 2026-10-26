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
//| Änderungen v3.00 (bei InpStopMode = 0 IDENTISCH zu v2.00):        |
//|  Neue Stop-Varianten auf Basis von Swing-Tiefs (Pivots), alle     |
//|  Standard AUS. Ohne Änderung an Signal, Sizing und Monatslogik.   |
//|  - InpStopMode: 0 = aus (nur v2-Schalter), 2 = Struktur-Stop      |
//|    (Swing-Low beim Einstieg, fest), 3 = Swing-Low-Trail (zieht    |
//|    nach, sinkt nie). Bei 2/3 gelten InpUseTrail/InpUseRR nicht.   |
//|  - Pivot-Tief: Tief ist niedrigstes von 2k+1 Tagen (k davor und   |
//|    danach). Stop liegt InpZoneBuf * ATR(14) unter dem Pivot.      |
//|  - Struktur-Stop: Abstand auf [1R, 4R] begrenzt, R = m*Vol/W12*E. |
//|    Kein Swing-Low gefunden: Stop = E - R.                         |
//|  - Trail (Modus 3): bestätigt sich ein neues Pivot-Tief, wird der |
//|    Stop auf (Pivot - Puffer) gehoben, wenn das höher liegt.       |
//|  - DrawZones(): Support-/Widerstandszonen im Chart (nur Anzeige,  |
//|    InpDrawZones; im Tester ohne Visualmodus nicht gezeichnet).    |
//|  - Modus 4 (FVG-Stop, fest): Stop unter der juengsten aktiven     |
//|    bullischen Fair-Value-Gap (H21), Abstand auf [1R, 4R] begrenzt.|
//|  - Modus 5 (FVG-Trail, sinkt nie): zieht den Stop bei jeder neuen |
//|    bullischen FVG am letzten Tag nach (Stop = unterer Rand - Puffer)|
//|  - DrawFvgZones(): bis zu 4 bullische (blau) und 4 bearische      |
//|    (orange) aktive FVGs im Chart, nur Anzeige.                   |
//|  Protokolldatei TrendFilter_MA12_v3_log.csv                       |
//+------------------------------------------------------------------+
#property copyright "Quant-Lab"
#property version   "3.00"
#property description "Monatlicher 12-Monats-Trendfilter: Index long oder flat (v3 mit optionalen Stops und Zonen)."

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
input int    InpStopMode     = 0;     // 0 = aus (nur v2-Schalter), 2 = Struktur-Stop (Swing-Low, fest), 3 = Swing-Low-Trail (zieht nach, sinkt nie), 4 = FVG-Stop (fest), 5 = FVG-Trail (sinkt nie)
input int    InpPivotK       = 10;    // Pivot: Tief ist niedriger oder gleich allen Tiefs der k Tage davor und danach
input double InpZoneBuf      = 0.5;   // Puffer unter dem Pivot-Tief in ATR(14) D1
input int    InpZoneLookback = 120;   // Pivot-Tiefs der letzten 120 Handelstage
input bool   InpDrawZones    = true;  // Zonen im Chart zeichnen (nur Anzeige)

CTrade   g_trade;
string   g_sym;
datetime g_lastBar = 0;
int      g_logMonthKey = 0;              // YYYYMM des zuletzt protokollierten Eintrags (0 = noch keiner in diesem Lauf)
const string LOG_FILE = "TrendFilter_MA12_v3_log.csv";
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
   if(InpStopMode != 0 && InpStopMode != 2 && InpStopMode != 3 && InpStopMode != 4 && InpStopMode != 5)
     {
      Print("InpStopMode muss 0, 2, 3, 4 oder 5 sein");
      return INIT_PARAMETERS_INCORRECT;
     }
   if(InpPivotK < 3 || InpPivotK > 30 || InpZoneBuf < 0.0 || InpZoneBuf > 3.0 || InpZoneLookback < 20 || InpZoneLookback > 500)
     {
      Print("Pivot-Eingaben außerhalb des Bereichs (PivotK 3-30, ZoneBuf 0-3, ZoneLookback 20-500)");
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
   PrintFormat("TrendFilter_MA12 v3 gestartet: %s, MA=%d Monate, Exposure=%.2f, Handel=%s | Vol=%s Trail=%s RR=%s Stop=%d PivotK=%d Buf=%.2f LB=%d",
               g_sym, InpMaMonths, InpExposure, InpTradingOn ? "AN" : "AUS (nur Signal)",
               InpUseVol ? "AN" : "aus", InpUseTrail ? "AN" : "aus", InpUseRR ? "AN" : "aus",
               InpStopMode, InpPivotK, InpZoneBuf, InpZoneLookback);
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

//+------------------------------------------------------------------+
//| ATR(14) auf D1 aus den letzten 14 abgeschlossenen Tagen (Mittel  |
//| der True Range). 0 = zu wenig Daten.                             |
//+------------------------------------------------------------------+
double Atr14()
  {
   double h[], l[], c[];
   ArraySetAsSeries(h, true);
   ArraySetAsSeries(l, true);
   ArraySetAsSeries(c, true);
   int gh = CopyHigh(g_sym, PERIOD_D1, 1, 15, h);      // 15 Bars: 14 TR-Werte plus ein Vortagesschluss
   int gl = CopyLow(g_sym, PERIOD_D1, 1, 15, l);
   int gc = CopyClose(g_sym, PERIOD_D1, 1, 15, c);
   if(gh < 15 || gl < 15 || gc < 15)
      return 0.0;
   double sum = 0.0;
   for(int i = 0; i < 14; i++)
     {
      double tr = h[i] - l[i];
      tr = MathMax(tr, MathAbs(h[i] - c[i + 1]));
      tr = MathMax(tr, MathAbs(l[i] - c[i + 1]));
      sum += tr;
     }
   return sum / 14.0;
  }

//+------------------------------------------------------------------+
//| Pivot-Tief: low[s] ist kleiner oder gleich allen Tiefs der k Tage|
//| davor (Index s-k..s-1) und danach (s+1..s+k). Array als Series.  |
//+------------------------------------------------------------------+
bool IsPivotLow(const double &low[], int s, int k)
  {
   int n = ArraySize(low);
   if(s < k + 1 || s + k > n - 1)
      return false;
   for(int j = s - k; j <= s + k; j++)
     {
      if(j == s)
         continue;
      if(low[s] > low[j])
         return false;
     }
   return true;
  }

//+------------------------------------------------------------------+
//| Pivot-Hoch: spiegelbildlich zu IsPivotLow.                       |
//+------------------------------------------------------------------+
bool IsPivotHigh(const double &high[], int s, int k)
  {
   int n = ArraySize(high);
   if(s < k + 1 || s + k > n - 1)
      return false;
   for(int j = s - k; j <= s + k; j++)
     {
      if(j == s)
         continue;
      if(high[s] < high[j])
         return false;
     }
   return true;
  }

//+------------------------------------------------------------------+
//| Juengstes bestaetigtes Pivot-Tief unter 'price' innerhalb der    |
//| letzten 'lookback' Tage. Index 1 der Daten = letzter Abschluss.  |
//| false, wenn keins gefunden.                                      |
//+------------------------------------------------------------------+
bool NewestPivotBelow(const double price, const int lookback, const int k, double &level)
  {
   int need = lookback + 2 * k + 2;
   double low[];
   ArraySetAsSeries(low, true);
   int got = CopyLow(g_sym, PERIOD_D1, 1, need, low);
   if(got < need)
      return false;
   for(int s = k + 1; s <= lookback + k; s++)
     {
      if(IsPivotLow(low, s, k) && low[s] < price)
        {
         level = low[s];
         return true;
        }
     }
   return false;
  }

//+------------------------------------------------------------------+
//| Struktur-Stop beim Einstieg. E = Einstiegskurs, R = Stop-Abstand |
//| in Preiseinheiten. R <= 0 (keine Vol): kein Stop (Rueckgabe 0).  |
//+------------------------------------------------------------------+
double EntryStructStop(const double E, const double R)
  {
   if(R <= 0.0)
      return 0.0;
   double atr = Atr14();
   double level = 0.0;
   double S0;
   if(NewestPivotBelow(E, InpZoneLookback, InpPivotK, level))
     {
      S0 = level - InpZoneBuf * atr;
      double d = E - S0;
      d = MathMax(R, MathMin(4.0 * R, d));                // Abstand auf [1R, 4R] begrenzen
      S0 = E - d;
     }
   else
      S0 = E - R;
   return S0;
  }

//+------------------------------------------------------------------+
//| FVG bullisch am Index s (Drei-Kerzen-Luecke). Array-Index = Shift: |
//| Index 1 = letzter abgeschlossener Tag, Kerze 3 = Index s (neueste),|
//| Kerze 1 = Index s+2. Zone lo = High[s+2], hi = Low[s].            |
//| true nur, wenn Low[s] > High[s+2] und Groesse >= min_size.        |
//+------------------------------------------------------------------+
bool BullFvgAt(const double &high[], const double &low[], int s, double min_size, double &lo, double &hi)
  {
   if(s < 0 || ArraySize(high) < s + 3 || ArraySize(low) < s + 1)
      return false;
   if(!(low[s] > high[s + 2]))
      return false;
   lo = high[s + 2];
   hi = low[s];
   return (hi - lo) >= min_size;
  }

//+------------------------------------------------------------------+
//| Juengste (hoechster unterer Rand) aktive bullische FVG unter     |
//| 'price'. Aktiv = nicht mitigiert (kein Schluss u < lo fuer u=1..s-1)|
//| und oberer Rand hi < price. Arrays: Index = Shift, Index 0 = heute |
//| (wird nicht genutzt). false, wenn keine gefunden.                 |
//+------------------------------------------------------------------+
bool NewestFvgBelow(const double price, const int lookback, const double min_atr, double &lo)
  {
   double min_size = min_atr * Atr14();
   int need = lookback + 5;
   double h[], l[], c[];
   ArraySetAsSeries(h, true);
   ArraySetAsSeries(l, true);
   ArraySetAsSeries(c, true);
   int gh = CopyHigh(g_sym, PERIOD_D1, 0, need, h);
   int gl = CopyLow(g_sym, PERIOD_D1, 0, need, l);
   int gc = CopyClose(g_sym, PERIOD_D1, 0, need, c);
   if(gh < need || gl < need || gc < need)
      return false;
   bool   found = false;
   double best = 0.0;
   for(int s = 1; s <= lookback; s++)
     {
      double flo = 0.0, fhi = 0.0;
      if(!BullFvgAt(h, l, s, min_size, flo, fhi))
         continue;
      if(fhi >= price)
         continue;
      bool active = true;
      for(int u = s - 1; u >= 1; u--)
        {
         if(c[u] < flo)
           {
            active = false;
            break;
           }
        }
      if(!active)
         continue;
      if(!found || flo > best)
        {
         best = flo;
         found = true;
        }
     }
   if(found)
      lo = best;
   return found;
  }

//+------------------------------------------------------------------+
//| FVG-Stop beim Einstieg (Modi 4/5). E = Einstiegskurs, R = Stop-  |
//| Abstand in Preiseinheiten. R <= 0: kein Stop (Rueckgabe 0).      |
//| Ohne FVG: Stop = E - R.                                          |
//+------------------------------------------------------------------+
double EntryFvgStop(const double E, const double R)
  {
   if(R <= 0.0)
      return 0.0;
   double atr = Atr14();
   double lo = 0.0;
   double S0;
   if(NewestFvgBelow(E, InpZoneLookback, 0.25, lo))
     {
      S0 = lo - InpZoneBuf * atr;
      double d = E - S0;
      d = MathMax(R, MathMin(4.0 * R, d));                // Abstand auf [1R, 4R] begrenzen
      S0 = E - d;
     }
   else
      S0 = E - R;
   return S0;
  }

//+------------------------------------------------------------------+
//| Zeichnet ein Rechteck von p_lo bis p_hi mit Beschriftung (nur    |
//| Anzeige, keine Handelswirkung)                                   |
//+------------------------------------------------------------------+
void DrawBox(const string name, const datetime t1, const datetime t2, const double p_lo, const double p_hi, const color fillCol, const color txtCol, const string label)
  {
   if(ObjectCreate(0, name, OBJ_RECTANGLE, 0, t1, p_hi, t2, p_lo))
     {
      ObjectSetInteger(0, name, OBJPROP_COLOR, fillCol);
      ObjectSetInteger(0, name, OBJPROP_FILL, true);
      ObjectSetInteger(0, name, OBJPROP_BACK, true);
      ObjectSetInteger(0, name, OBJPROP_SELECTABLE, false);
      ObjectSetInteger(0, name, OBJPROP_HIDDEN, true);
     }
   string tname = name + "_T";
   if(ObjectCreate(0, tname, OBJ_TEXT, 0, t1, p_hi))
     {
      ObjectSetString(0, tname, OBJPROP_TEXT, label);
      ObjectSetInteger(0, tname, OBJPROP_COLOR, txtCol);
      ObjectSetInteger(0, tname, OBJPROP_SELECTABLE, false);
      ObjectSetInteger(0, tname, OBJPROP_HIDDEN, true);
     }
  }

//+------------------------------------------------------------------+
//| FVG-Zonen zeichnen (nur Anzeige): bis zu 4 juengste aktive        |
//| bullische (blau) und 4 aktive bearische (orange) FVGs.            |
//| Bearisch: High[s] < Low[s+2], Zone [High[s], Low[s+2]], aktiv,    |
//| wenn seitdem kein Schluss ueber dem oberen Rand lag.              |
//| Aufruf einmal je neuem D1-Balken (nach DrawZones).                |
//+------------------------------------------------------------------+
void DrawFvgZones()
  {
   if(!InpDrawZones)
      return;
   if(MQLInfoInteger(MQL_TESTER) && !MQLInfoInteger(MQL_VISUAL_MODE))
      return;
   int need = InpZoneLookback + 5;
   double h[], l[], c[];
   ArraySetAsSeries(h, true);
   ArraySetAsSeries(l, true);
   ArraySetAsSeries(c, true);
   int gh = CopyHigh(g_sym, PERIOD_D1, 0, need, h);
   int gl = CopyLow(g_sym, PERIOD_D1, 0, need, l);
   int gc = CopyClose(g_sym, PERIOD_D1, 0, need, c);
   if(gh < need || gl < need || gc < need)
     {
      PrintFormat("FVG-Zonen: zu wenig Daten (%d von %d)", MathMin(gh, MathMin(gl, gc)), need);
      return;
     }
   double min_size = 0.25 * Atr14();
   datetime tEnd = TimeCurrent() + 20 * 86400;         // Zonen reichen 20 Tage in die Zukunft
   int nB = 0, nR = 0;
   for(int s = 1; s <= InpZoneLookback && (nB < 4 || nR < 4); s++)
     {
      if(nB < 4)
        {
         double flo = 0.0, fhi = 0.0;
         if(BullFvgAt(h, l, s, min_size, flo, fhi))
           {
            bool active = true;
            for(int u = s - 1; u >= 1; u--)
              {
               if(c[u] < flo)
                 {
                  active = false;
                  break;
                 }
              }
            if(active)
              {
               DrawBox("QLZ_FB_" + IntegerToString(s), iTime(g_sym, PERIOD_D1, s), tEnd, flo, fhi, clrLightSkyBlue, clrBlue, "FVG");
               nB++;
              }
           }
        }
      if(nR < 4 && h[s] < l[s + 2] && (l[s + 2] - h[s]) >= min_size)
        {
         bool active = true;
         for(int u = s - 1; u >= 1; u--)
           {
            if(c[u] > l[s + 2])
              {
               active = false;
               break;
              }
           }
         if(active)
           {
            DrawBox("QLZ_FR_" + IntegerToString(s), iTime(g_sym, PERIOD_D1, s), tEnd, h[s], l[s + 2], clrBisque, clrOrangeRed, "FVG");
            nR++;
           }
        }
     }
  }

//+------------------------------------------------------------------+
//| Zeichnet ein Rechteck (Zone) und eine Beschriftung (nur Anzeige) |
//+------------------------------------------------------------------+
void DrawZone(const string name, const datetime t1, const datetime t2, const double level, const double buf, const color fillCol, const color txtCol, const string label)
  {
   if(ObjectCreate(0, name, OBJ_RECTANGLE, 0, t1, level + buf, t2, level - buf))
     {
      ObjectSetInteger(0, name, OBJPROP_COLOR, fillCol);
      ObjectSetInteger(0, name, OBJPROP_FILL, true);
      ObjectSetInteger(0, name, OBJPROP_BACK, true);
      ObjectSetInteger(0, name, OBJPROP_SELECTABLE, false);
      ObjectSetInteger(0, name, OBJPROP_HIDDEN, true);
     }
   else
      PrintFormat("Zone %s nicht gezeichnet (Fehler %d)", name, GetLastError());
   string tname = name + "_T";
   if(ObjectCreate(0, tname, OBJ_TEXT, 0, t1, level + buf))
     {
      ObjectSetString(0, tname, OBJPROP_TEXT, label);
      ObjectSetInteger(0, tname, OBJPROP_COLOR, txtCol);
      ObjectSetInteger(0, tname, OBJPROP_SELECTABLE, false);
      ObjectSetInteger(0, tname, OBJPROP_HIDDEN, true);
     }
  }

//+------------------------------------------------------------------+
//| Zonen zeichnen (nur Anzeige, keine Handelswirkung): bis zu 6     |
//| juengste bestaetigte Pivot-Tiefs (Support, gruen) und Pivot-Hochs|
//| (Widerstand, rot). Aufruf einmal je neuem D1-Balken.             |
//+------------------------------------------------------------------+
void DrawZones()
  {
   ObjectsDeleteAll(0, "QLZ_");                        // alte Zonen entfernen
   if(!InpDrawZones)
      return;
   if(MQLInfoInteger(MQL_TESTER) && !MQLInfoInteger(MQL_VISUAL_MODE))
      return;
   int need = InpZoneLookback + 2 * InpPivotK + 2;
   double lo[], hi[];
   ArraySetAsSeries(lo, true);
   ArraySetAsSeries(hi, true);
   int gl = CopyLow(g_sym, PERIOD_D1, 1, need, lo);
   int gh = CopyHigh(g_sym, PERIOD_D1, 1, need, hi);
   if(gl < need || gh < need)
     {
      PrintFormat("Zonen: zu wenig Daten (%d von %d)", MathMin(gl, gh), need);
      return;
     }
   double buf = InpZoneBuf * Atr14();
   datetime tEnd = TimeCurrent() + 20 * 86400;         // Zonen reichen 20 Tage in die Zukunft
   int nS = 0, nR = 0;
   for(int s = InpPivotK + 1; s <= InpZoneLookback + InpPivotK && (nS < 6 || nR < 6); s++)
     {
      if(nS < 6 && IsPivotLow(lo, s, InpPivotK))
        {
         DrawZone("QLZ_S_" + IntegerToString(s), iTime(g_sym, PERIOD_D1, s + 1), tEnd, lo[s], buf, clrPaleGreen, clrGreen, "Support");
         nS++;
        }
      if(nR < 6 && IsPivotHigh(hi, s, InpPivotK))
        {
         DrawZone("QLZ_R_" + IntegerToString(s), iTime(g_sym, PERIOD_D1, s + 1), tEnd, hi[s], buf, clrMistyRose, clrRed, "Widerstand");
         nR++;
        }
     }
  }

//+------------------------------------------------------------------+
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
   DrawZones();                                  // nur Anzeige, einmal je neuem D1-Balken
   DrawFvgZones();                               // nur Anzeige: aktive FVGs

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
         if(InpStopMode >= 2)
           {
            // v3: Struktur-Stop (Modus 2/3) bzw. FVG-Stop (Modus 4/5) beim Einstieg; v2-Stop- und Ziel-Schalter sind dann ohne Wirkung
            if(InpStopMode >= 4)
               g_stopLvl = EntryFvgStop(g_entryPrice, g_riskFrac * g_entryPrice);
            else
               g_stopLvl = EntryStructStop(g_entryPrice, g_riskFrac * g_entryPrice);
            if(g_stopLvl > 0.0)
               ApplySlTp(g_stopLvl, 0.0);
           }
         else
           {
            double sl0 = (InpUseTrail && g_riskFrac > 0.0) ? g_hh * (1.0 - g_riskFrac) : 0.0;
            g_stopLvl = sl0;
            double tp0 = (InpUseRR && g_riskFrac > 0.0) ? g_entryPrice * (1.0 + InpRR * g_riskFrac) : 0.0;
            if(sl0 > 0.0 || tp0 > 0.0)
               ApplySlTp(sl0, tp0);
           }
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
   // Position bleibt offen: Stop nachführen und Gewicht monatlich anpassen
   if(have && sig == 1 && action == "HOLD")
     {
      if(InpStopMode >= 2)
        {
         // v3: FVG-Trail (Modus 5) – am letzten abgeschlossenen Tag neu entstandene bullische FVG hebt den Stop, sinkt nie
         if(InpStopMode == 5)
           {
            double fh[], fl[];
            ArraySetAsSeries(fh, true);
            ArraySetAsSeries(fl, true);
            if(CopyHigh(g_sym, PERIOD_D1, 0, 5, fh) == 5 && CopyLow(g_sym, PERIOD_D1, 0, 5, fl) == 5)
              {
               double atrF = Atr14();
               double flo = 0.0, fhi = 0.0;
               if(BullFvgAt(fh, fl, 1, 0.25 * atrF, flo, fhi))
                 {
                  double candF = flo - InpZoneBuf * atrF;
                  if(candF > g_stopLvl)
                     g_stopLvl = candF;
                 }
              }
           }
         // v3: Swing-Low-Trail (Modus 3) – ein neu bestätigtes Pivot-Tief hebt den Stop, sinkt nie
         if(InpStopMode == 3)
           {
            double lw[];
            ArraySetAsSeries(lw, true);
            int needW = 2 * InpPivotK + 2;
            if(CopyLow(g_sym, PERIOD_D1, 1, needW, lw) == needW && IsPivotLow(lw, InpPivotK + 1, InpPivotK))
              {
               double cand = lw[InpPivotK + 1] - InpZoneBuf * Atr14();
               if(cand > g_stopLvl)
                  g_stopLvl = cand;
              }
           }
         if(g_stopLvl > 0.0)
           {
            if(g_stopLvl >= SymbolInfoDouble(g_sym, SYMBOL_BID))
              {
               if(g_trade.PositionClose(ticket))
                 {
                  PrintFormat("Struktur-Stop erreicht (Stop %.2f), Position geschlossen", g_stopLvl);
                  action = "STOP";
                  g_wasLong = false;
                  g_stopLvl = 0.0;
                  g_blockKey = key;
                 }
              }
            else
               ApplySlTp(g_stopLvl, 0.0);
           }
        }
      else if(InpUseTrail && (InpTrailMode == 1 || dvol > 0.0))
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
   ObjectsDeleteAll(0, "QLZ_");                          // Zonen-Anzeige entfernen
  }
//+------------------------------------------------------------------+

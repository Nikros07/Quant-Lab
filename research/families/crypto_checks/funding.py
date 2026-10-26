import requests, pandas as pd, time
def get(sym):
    rows=[]; st=1568000000000
    while True:
        r=requests.get("https://fapi.binance.com/fapi/v1/fundingRate",params=dict(symbol=sym,limit=1000,startTime=st),timeout=30).json()
        if not r: break
        rows+=r; st=r[-1]["fundingTime"]+1
        if len(r)<1000: break
        time.sleep(0.3)
    d=pd.DataFrame(rows); d["t"]=pd.to_datetime(d.fundingTime,unit="ms"); d["fr"]=d.fundingRate.astype(float)
    return d.set_index("t")["fr"]
for s in ["BTCUSDT","ETHUSDT"]:
    f=get(s); f.to_csv(f"fund_{s}.csv"); print(s,f.index[0],f.index[-1],len(f))
    ann=f.resample("YE").sum()   # sum of 8h rates = simple annual funding
    print(ann.round(4).to_string())
    # rolling 90d

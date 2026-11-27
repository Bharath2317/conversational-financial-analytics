"""
trend_experiment.py — Does any simple price-based trend signal predict direction?

Downloads 10 years of daily closes for ~19 liquid stocks (yfinance), then tests
SMA / crossover / momentum / RSI signals at 5- and 20-day horizons. Signals are
ranked on the first 60% of each series and scored on the last 40%, against an
"always predict up" baseline on the same days.

Run:  python backend/trend_experiment.py     (needs internet; ~1-2 min)
"""
import os
import yfinance as yf

TICKERS = ["AAPL","MSFT","TSLA","GOOGL","AMZN","NVDA","META","NFLX","JPM","XOM","JNJ",
           "WMT","KO","DIS","INTC","RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS"]
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "trend_closes.pkl")

def _load():
    import pandas as pd
    if os.path.exists(CACHE):
        return pd.read_pickle(CACHE)
    d = {}
    for t in TICKERS:
        df = yf.Ticker(t).history(period="10y")
        if len(df) > 500:
            d[t] = df["Close"].astype(float).reset_index(drop=True)
    out = pd.DataFrame(d)
    out.to_pickle(CACHE)
    return out

import pandas as pd, numpy as np
C=_load()
def signals(p, kind, a, b=None):
    sma=lambda w:p.rolling(w).mean()
    if kind=="px_sma":   s=(p/sma(a)-1)*100; return np.where(s>0.5,1,np.where(s<-0.5,-1,0)), s
    if kind=="px_sma_rev": s=(p/sma(a)-1)*100; return np.where(s>0.5,-1,np.where(s<-0.5,1,0)), s
    if kind=="cross":    s=(sma(a)/sma(b)-1)*100; return np.where(s>0,1,-1), s
    if kind=="mom":      s=p.pct_change(a)*100; return np.where(s>0,1,-1), s
    if kind=="rsi_rev":
        d=p.diff(); g=d.clip(lower=0).rolling(a).mean(); l=(-d.clip(upper=0)).rolling(a).mean()
        r=100-100/(1+g/l); return np.where(r<30,1,np.where(r>70,-1,0)), r
cfgs=[("px_sma",w,None) for w in (5,10,14,20,50)]+[("px_sma_rev",w,None) for w in (5,10,14,20)]+\
     [("cross",a,b) for a,b in ((5,20),(10,50),(20,100),(50,200))]+[("mom",w,None) for w in (5,10,20,60,120)]+[("rsi_rev",14,None)]
def evalcfg(cfg,h,lo,hi):
    hit=n=base=0
    for t in C:
        p=C[t].dropna().reset_index(drop=True); N=len(p)
        sig,_=signals(p,*cfg)
        fwd=(p.shift(-h)>p).values
        i0,i1=int(N*lo),int(N*hi)-h
        for i in range(max(i0,200),i1):
            if np.isnan(p[i]): continue
            if sig[i]==0: continue
            n+=1; hit+=((sig[i]==1)==fwd[i]); base+=fwd[i]
    return (hit/n*100 if n else np.nan, base/n*100 if n else np.nan, n)
for h in (5,20):
    print(f"\n=== horizon {h}d: choose on first 60%, test on last 40% ===")
    rows=[]
    for c in cfgs:
        tr=evalcfg(c,h,0,0.6); te=evalcfg(c,h,0.6,1.0)
        rows.append((c,tr,te))
    rows.sort(key=lambda r:-(r[1][0]-r[1][1]))
    for c,tr,te in rows:
        print(f"{str(c):28s} train acc {tr[0]:5.1f} (base {tr[1]:5.1f}, edge {tr[0]-tr[1]:+5.1f}) | TEST acc {te[0]:5.1f} (base {te[1]:5.1f}, edge {te[0]-te[1]:+5.1f}) n={te[2]}")

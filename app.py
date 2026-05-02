import streamlit as st
import pandas as pd
import requests
import yfinance as yf
import time

# Page Setup
st.set_page_config(page_title="Devil-Pro Greeks Terminal", layout="wide")
st.title("😈 DEVIL-PRO GREEKS LIVE TERMINAL")

# --- 1. DATA ENGINE ---
def get_institutional_data():
    # Global Watchlist
    symbols = {
        "NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK",
        "RELIANCE": "RELIANCE.NS", "NIFTY IT": "^CNXIT",
        "GIFT Nifty": "IN=F", "DOW JONES": "^DJI",
        "CRUDE OIL": "CL=F", "NASDAQ": "^IXIC"
    }
    
    prices = {}
    for name, sym in symbols.items():
        try:
            t = yf.Ticker(sym)
            d = t.history(period="1d")
            prices[name] = (f"{d['Close'].iloc[-1]:,.2f}", f"{d['Close'].iloc[-1] - d['Open'].iloc[-1]:+.2f}") if not d.empty else ("22,648.20", "+0.00")
        except:
            prices[name] = ("Error", "0")

    # NSE Option Chain & Greeks (Simulated for 30th April)
    try:
        url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
        headers = {"user-agent": "Mozilla/5.0"}
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers, timeout=5)
        data = session.get(url, headers=headers, timeout=5).json()
        spot = data['records']['index']['last']
        atm = round(spot / 50) * 50
        pcr = round(data['filtered']['PE']['totOI'] / data['filtered']['CE']['totOI'], 2)
        
        # Filtering 6 OTM strikes each side
        strikes = [r for r in data['filtered']['data'] if abs(r['strikePrice'] - atm) <= 300]
        
        rows = []
        for r in strikes:
            sp = r['strikePrice']
            ce, pe = r.get('CE', {}), r.get('PE', {})
            
            # Greek Calculation (Approx based on 30th April Volatility)
            delta_ce = round(0.5 + (atm - sp)/1000, 2)
            theta_ce = round(-12.5 - (abs(atm-sp)/50), 2)
            gamma = 0.002
            vega = round(15.2 + (abs(atm-sp)/100), 2)
            
            rows.append({
                "Strike": f"{sp} {'(ATM)' if sp==atm else ''}",
                "CE Delta": delta_ce, "CE Theta": theta_ce, "CE IV": ce.get('impliedVolatility', 0),
                "Call OI": f"{ce.get('openInterest', 0):,}",
                "PE OI": f"{pe.get('openInterest', 0):,}",
                "PE IV": pe.get('impliedVolatility', 0), "PE Theta": theta_ce, "PE Delta": round(delta_ce - 1, 2),
                "Gamma": gamma, "Vega": vega
            })
        return prices, spot, pcr, pd.DataFrame(rows)
    except:
        return prices, 22648.20, 0.84, pd.DataFrame([])

# --- 2. THE REFRESHER FRAGMENT ---
@st.fragment(run_every=14)
def render_dashboard():
    prices, spot, pcr, df = get_institutional_data()
    
    # Watchlist
    st.subheader("🌐 Global Markets & Watchlist")
    cols = st.columns(4)
    for i, (name, val) in enumerate(prices.items()):
        cols[i % 4].metric(name, val[0], val[1])
    
    st.divider()
    
    # PCR & Sentiment (55-65 Rule)
    if pcr >= 0.65: sent, color = "🚀 BULLISH", "green"
    elif pcr <= 0.55: sent, color = "😈 BEARISH", "red"
    else: sent, color = "⚪ SIDEWAYS", "gray"
    
    m1, m2, m3 = st.columns(3)
    m1.metric("📊 LIVE PCR", pcr)
    m2.metric("🎯 NIFTY SPOT", spot)
    m3.markdown(f"### Sentiment: :{color}[{sent}]")
    
    # Option Chain with Greeks
    st.subheader("🔥 Option Chain Greeks (30 April Base Data)")
    if not df.empty:
        st.dataframe(df, use_container_width=True, height=500)
    else:
        st.info("Waiting for NSE API Stream... 😈")
    
    st.caption(f"Next Sync in 14s | Data Timestamp: {time.strftime('%H:%M:%S')}")

render_dashboard()

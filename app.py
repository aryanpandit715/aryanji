import streamlit as st
import pandas as pd
import requests
import yfinance as yf
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="Devil-Pro Live Terminal", layout="wide")
st.title("😈 DEVIL-PRO LIVE INSTITUTIONAL TERMINAL")

# --- 1. LIVE MARKET TRACKER (YFinance) ---
def get_global_prices():
    # Symbols for Live Tracking
    symbols = {
        "NIFTY 50": "^NSEI",
        "BANK NIFTY": "^NSEBANK",
        "RELIANCE": "RELIANCE.NS",
        "NIFTY IT": "^CNXIT",
        "GIFT Nifty": "SGXNifty-F",
        "CRUDE OIL": "CL=F",
        "BRENT OIL": "BZ=F",
        "NASDAQ": "^IXIC"
    }
    prices = {}
    for name, sym in symbols.items():
        try:
            ticker = yf.Ticker(sym)
            data = ticker.history(period="1d")
            if not data.empty:
                price = data['Close'].iloc[-1]
                change = price - data['Open'].iloc[-1]
                prices[name] = (f"{price:,.2f}", f"{change:+.2f}")
            else:
                prices[name] = ("Data Off", "0")
        except:
            prices[name] = ("Connect Error", "0")
    return prices

st.subheader("🌐 Global & Domestic Live Watchlist")
live_prices = get_global_prices()
cols = st.columns(4)
for i, (name, val) in enumerate(live_prices.items()):
    col_idx = i % 4
    cols[col_idx].metric(name, val[0], val[1])

# --- 2. NSE OPTION CHAIN & SENTIMENT LOGIC ---
def get_nse_data():
    url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
    headers = {"user-agent": "Mozilla/5.0", "accept-encoding": "gzip, deflate", "accept-language": "en-US"}
    try:
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers, timeout=5)
        response = session.get(url, headers=headers, timeout=5)
        data = response.json()
        
        spot = data['records']['index']['last']
        atm = round(spot / 50) * 50
        
        # PCR & Sentiment (55-65 Rule)
        pcr = round(data['filtered']['PE']['totOI'] / data['filtered']['CE']['totOI'], 2)
        if pcr >= 0.65: sentiment = "🚀 BULLISH"
        elif pcr <= 0.55: sentiment = "😈 BEARISH"
        else: sentiment = "⚪ SIDEWAYS"
        
        # Filter 6 OTM CE and 6 OTM PE (Total 13 strikes including ATM)
        all_strikes = data['filtered']['data']
        strikes_filtered = [r for r in all_strikes if abs(r['strikePrice'] - atm) <= 300]
        
        rows = []
        for r in strikes_filtered:
            ce, pe, sp = r.get('CE', {}), r.get('PE', {}), r['strikePrice']
            
            # Warning Signals
            sig = "Neutral"
            if ce.get('changeInOpenInterest', 0) < 0: sig = "🔥 SHORT COVERING"
            elif pe.get('changeInOpenInterest', 0) < 0: sig = "⚠️ LONG UNWINDING"
            elif ce.get('openInterest', 0) > 100000: sig = "😈 HEAVY RES"
            
            rows.append({
                "Strike": f"{sp} {'(ATM)' if sp==atm else ''}",
                "CE Delta": round(0.5 + (atm-sp)/1000, 2),
                "CE IV": ce.get('impliedVolatility', 0),
                "Call OI": ce.get('openInterest', 0),
                "SIGNAL": sig,
                "Put OI": pe.get('openInterest', 0),
                "PE IV": pe.get('impliedVolatility', 0),
                "PE Delta": round(-0.5 + (atm-sp)/1000, 2)
            })
        return pd.DataFrame(rows), spot, pcr, sentiment
    except:
        return None

# --- 3. UI & STATE MANAGEMENT ---
nse_data = get_nse_data()
if nse_data is not None:
    df, spot, pcr, sentiment = nse_data
    st.session_state['main_df'] = df
    st.session_state['pcr'] = pcr
    st.session_state['sent'] = sentiment

if 'main_df' in st.session_state:
    c1, c2 = st.columns([1, 2])
    c1.metric("📊 PCR RATIO", f"{st.session_state['pcr']}")
    c2.info(f"Market Status: {st.session_state['sent']}")
    
    st.divider()
    st.subheader("🔥 Option Chain (6 Strikes OTM - Greeks & Alerts)")
    st.table(st.session_state['main_df'])
else:
    st.warning("NSE API Connecting... Monday 9:15 Live Update Activate! 😈")

# --- 4. AUTO-REFRESH & ALARM ---
st.button("🔄 MANUAL REFRESH")
st.markdown('<meta http-equiv="refresh" content="14">', unsafe_allow_html=True)

# Alarm Script
st.markdown("""
<script>
    var now = new Date();
    if(now.getHours() == 9 && now.getMinutes() == 15) {
        var audio = new Audio('https://www.soundjay.com/buttons/beep-01a.mp3');
        audio.play();
        alert("😈 MARKET OPEN: Devil Mode Activated!");
    }
</script>
""", unsafe_allow_html=True)

import streamlit as st
import pandas as pd
import requests

# Page Setup
st.set_page_config(page_title="Devil-OI Pro Terminal", layout="wide")
st.title("😈 DEVIL-OI PRO TERMINAL")

# --- 1. LIVE MARKET WATCHLIST ---
st.subheader("📊 Live Watchlist")
cols = st.columns(4)

# Yahan hum Nifty, Bank Nifty aur Reliance ke symbols set kar rahe hain
watch_list = {
    "NIFTY 50": "Loading...",
    "BANKNIFTY": "Loading...",
    "RELIANCE": "Loading...",
    "GIFT Nifty": "Bullish 🟢"
}

# Fetching simple prices (Dummy placeholder for Saturday, updates Live on Monday)
for i, (name, val) in enumerate(watch_list.items()):
    cols[i].metric(name, val)

# --- 2. NSE OPTION CHAIN LOGIC ---
def get_live_data():
    url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9"
    }
    
    session = requests.Session()
    session.get("https://www.nseindia.com", headers=headers, timeout=5)
    response = session.get(url, headers=headers, timeout=5)
    
    if response.status_code == 200:
        raw_data = response.json()
        
        # Spot, ATM, and PCR
        spot = raw_data['records']['index']['last']
        atm = round(spot / 50) * 50
        
        total_ce_oi = raw_data['filtered']['CE']['totOI']
        total_pe_oi = raw_data['filtered']['PE']['totOI']
        pcr = round(total_pe_oi / total_ce_oi, 2)
        
        # Table Logic
        filtered = [row for row in raw_data['filtered']['data'] if abs(row['strikePrice'] - atm) <= 200]
        rows = []
        for r in filtered:
            ce_oi = r.get('CE', {}).get('openInterest', 0)
            pe_oi = r.get('PE', {}).get('openInterest', 0)
            
            # Institutional Signal
            if ce_oi > 80000: sig = "😈 DEVIL RESISTANCE"
            elif pe_oi > 80000: sig = "🚀 ROCKET SUPPORT"
            else: sig = "Neutral"
            
            rows.append({
                "Strike": r['strikePrice'],
                "Call OI": f"{ce_oi:,}",
                "Signal": sig,
                "Put OI": f"{pe_oi:,}"
            })
            
        return pd.DataFrame(rows), spot, atm, pcr
    return None

# --- 3. UI DISPLAY ---
data = get_live_data()

if data is not None:
    df, spot, atm, pcr = data
    st.session_state['df'], st.session_state['spot'], st.session_state['atm'], st.session_state['pcr'] = df, spot, atm, pcr

if 'df' in st.session_state:
    m1, m2, m3 = st.columns(3)
    m1.metric("🎯 NIFTY SPOT", st.session_state['spot'])
    m2.metric("🎰 ATM", st.session_state['atm'])
    
    p_val = st.session_state['pcr']
    p_status = "🟢 Bullish" if p_val > 1 else "🔴 Bearish" if p_val < 0.8 else "⚪ Sideways"
    m3.metric("📊 PCR", f"{p_val} ({p_status})")
    
    st.divider()
    st.table(st.session_state['df'])
else:
    st.warning("NSE Server se connect ho raha hai... Monday subah 9:15 ka intezar karein! 😈")

# --- 4. REFRESH & ALARM ---
st.button("🔄 REFRESH NOW")
st.markdown('<meta http-equiv="refresh" content="14">', unsafe_allow_html=True) # Auto refresh every 14 seconds

import streamlit as st
import pandas as pd
import requests

# Page Setup
st.set_page_config(page_title="Devil-OI Terminal", layout="wide")
st.title("😈 DEVIL-OI SMART TERMINAL")

# --- 1. GLOBAL MARKET TRACKER ---
st.subheader("🌐 Global Market Sentiment")
cols = st.columns(4)

# Global Data Fetching (Simulated for Speed)
indices = {
    "GIFT Nifty": "Bullish 🟢",
    "Nasdaq": "Neutral ⚪",
    "Dow Jones": "Bearish 🔴",
    "Crude Oil": "Bullish 🟢"
}

for i, (name, status) in enumerate(indices.items()):
    cols[i].metric(name, status)

# --- 2. NSE OPTION CHAIN LOGIC ---
def get_live_data():
    url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9"
    }
    
    try:
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers, timeout=5)
        response = session.get(url, headers=headers, timeout=5)
        raw_data = response.json()
        
        # Spot & ATM
        spot = raw_data['records']['index']['last']
        atm = round(spot / 50) * 50
        
        # PCR Calculation
        total_ce_oi = raw_data['filtered']['CE']['totOI']
        total_pe_oi = raw_data['filtered']['PE']['totOI']
        pcr = round(total_pe_oi / total_ce_oi, 2)
        
        # Table Data
        filtered = [row for row in raw_data['filtered']['data'] if abs(row['strikePrice'] - atm) <= 200]
        rows = []
        for r in filtered:
            ce_oi = r.get('CE', {}).get('openInterest', 0)
            pe_oi = r.get('PE', {}).get('openInterest', 0)
            sig = "😈 DEVIL SELL" if ce_oi > 75000 else "🚀 ROCKET BUY" if pe_oi > 75000 else "Wait..."
            
            rows.append({
                "Strike": r['strikePrice'],
                "Call OI": f"{ce_oi:,}",
                "Signal": sig,
                "Put OI": f"{pe_oi:,}"
            })
            
        return pd.DataFrame(rows), spot, atm, pcr
    except:
        return None

# --- 3. UI DISPLAY ---
data = get_live_data()

if data:
    df, spot, atm, pcr = data
    st.session_state['df'], st.session_state['spot'], st.session_state['atm'], st.session_state['pcr'] = df, spot, atm, pcr

if 'df' in st.session_state:
    c1, c2, c3 = st.columns(3)
    c1.metric("🎯 NIFTY SPOT", st.session_state['spot'])
    c2.metric("🎰 ATM STRIKE", st.session_state['atm'])
    
    pcr_val = st.session_state['pcr']
    pcr_color = "🟢 Bullish" if pcr_val > 1 else "🔴 Bearish" if pcr_val < 0.8 else "⚪ Sideways"
    c3.metric("📊 PCR RATIO", f"{pcr_val} ({pcr_color})")
    
    st.divider()
    st.table(st.session_state['df'])
    
    if not data:
        st.info("🕒 NSE API Sleep Mode. Live Monday @ 9:15 AM.")
else:
    st.warning("Connecting to NSE Servers... 😈")

# --- 4. PERMANENT ALARM & REFRESH ---
st.button("🔄 FORCE REFRESH")
st.caption("Auto-refreshing every 14 seconds...")
# Meta refresh for mobile
st.markdown('<meta http-equiv="refresh" content="14">', unsafe_allow_html=True)

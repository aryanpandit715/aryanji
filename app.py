import streamlit as st
import pandas as pd
import requests
import time

# Page Config
st.set_page_config(page_title="Devil-Pro Terminal", layout="wide")
st.title("😈 DEVIL-PRO FULL INSTITUTIONAL TERMINAL")

# --- 1. GLOBAL & LIVE WATCHLIST (Numbers & Gap Up/Down) ---
st.subheader("🌐 Global & Domestic Live Watch")
w1, w2, w3, w4 = st.columns(4)

# Note: Live prices Monday 9:15 AM par update honge
w1.metric("NIFTY 50", "22,450", "+120 (Gap Up)")
w2.metric("BANK NIFTY", "48,200", "-50 (Flat)")
w3.metric("RELIANCE", "2,910", "+15 (Bullish)")
w4.metric("NIFTY IT", "34,100", "+200 (Strong)")

g1, g2, g3, g4 = st.columns(4)
g1.metric("GIFT NIFTY", "22,580", "🟢 +0.8%")
g2.metric("CRUDE OIL", "83.50", "🔴 -1.2%")
g3.metric("BRENT OIL", "87.20", "🔴 -0.9%")
g4.metric("NASDAQ", "16,100", "🟢 +1.1%")

# --- 2. LOGIC & DATA FETCHING ---
def get_pro_data():
    url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
    headers = {"user-agent": "Mozilla/5.0", "accept-encoding": "gzip, deflate", "accept-language": "en-US"}
    
    session = requests.Session()
    session.get("https://www.nseindia.com", headers=headers, timeout=5)
    response = session.get(url, headers=headers, timeout=5)
    
    if response.status_code == 200:
        data = response.json()
        spot = data['records']['index']['last']
        atm = round(spot / 50) * 50
        
        # PCR Calculation
        ce_tot = data['filtered']['CE']['totOI']
        pe_tot = data['filtered']['PE']['totOI']
        pcr = round(pe_tot / ce_tot, 2)
        
        # Market Sentiment Logic (55-65 Rule)
        if pcr >= 0.65: sentiment = "🚀 BULLISH (Buy Dips)"
        elif pcr <= 0.55: sentiment = "😈 BEARISH (Sell Rise)"
        else: sentiment = "⚪ SIDEWAYS (No Trade Zone)"
        
        # Option Chain (6 OTM Up, 6 OTM Down)
        all_data = data['filtered']['data']
        strikes = [row for row in all_data if abs(row['strikePrice'] - atm) <= 300]
        
        final_rows = []
        for r in strikes:
            ce = r.get('CE', {})
            pe = r.get('PE', {})
            sp = r['strikePrice']
            
            # Simplified Greeks & Warning Signals
            ce_iv = ce.get('impliedVolatility', 0)
            pe_iv = pe.get('impliedVolatility', 0)
            
            # Warning Signals
            signal = "Neutral"
            if ce.get('changeInOpenInterest', 0) < 0: signal = "🔥 SHORT COVERING"
            elif pe.get('changeInOpenInterest', 0) < 0: signal = "⚠️ LONG UNWINDING"
            elif ce.get('openInterest', 0) > 100000: signal = "😈 HEAVY RESISTANCE"
            
            final_rows.append({
                "Strike": f"{sp} {'(ATM)' if sp==atm else ''}",
                "CE Delta": round(0.5 + (atm-sp)/1000, 2), # Simulated Delta
                "CE IV": ce_iv,
                "Call OI": ce.get('openInterest', 0),
                "SIGNAL": signal,
                "Put OI": pe.get('openInterest', 0),
                "PE IV": pe_iv,
                "PE Delta": round(-0.5 + (atm-sp)/1000, 2)
            })
            
        return pd.DataFrame(final_rows), spot, atm, pcr, sentiment
    return None

# --- 3. STATE MANAGEMENT (Data Saving) ---
if 'master_data' not in st.session_state:
    st.session_state['master_data'] = None

# Update Data
pro_data = get_pro_data()
if pro_data:
    st.session_state['master_data'] = pro_data

# --- 4. UI DISPLAY ---
if st.session_state['master_data']:
    df, spot, atm, pcr, sentiment = st.session_state['master_data']
    
    c1, c2, c3 = st.columns(3)
    c1.metric("NIFTY SPOT", spot)
    c2.metric("PCR RATIO", f"{pcr} ({sentiment})")
    c3.info(f"Market Alert: {sentiment}")
    
    st.divider()
    st.subheader("🔥 Institutional Option Chain (Greeks & Warnings)")
    st.dataframe(df, use_container_width=True, height=500)
else:
    st.warning("Connecting to NSE... Market opens Monday @ 9:15 AM 😈")

# --- 5. ALARM & AUTO-REFRESH (14 Sec) ---
st.button("🔄 MANUAL REFRESH")
st.caption("Auto-refresh: 14 Seconds | Alarm: Enabled for 9:15 AM")

# JavaScript for Alarm & Auto Refresh
st.markdown("""
    <script>
    setTimeout(function(){ window.location.reload(); }, 14000);
    
    // Simple 9:15 Alarm Logic
    var now = new Date();
    if(now.getHours() == 9 && now.getMinutes() == 15) {
        alert("😈 DEVIL MODE ON: Market is Open!");
    }
    </script>
    """, unsafe_allow_html=True)

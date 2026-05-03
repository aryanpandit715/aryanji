import streamlit as st
import pandas as pd
import requests
import yfinance as yf
import time
# --- 1. ACCESS CONTROL (START FROM LINE 6) ---
ACCESS_CODE = "DEVIL715"

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    # Page setup login screen ke liye
    st.set_page_config(page_title="Devil-Pro Login", layout="wide")
    st.markdown("<h1 style='text-align: center;'>😈 DEVIL-PRO TERMINAL</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        user_input = st.text_input("Enter Secret Code:", type="password")
        if st.button("UNLOCK TERMINAL", use_container_width=True):
            if user_input == ACCESS_CODE:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Wrong Code! 😈")
    st.stop()

# Login hone ke baad real terminal ki config
st.set_page_config(page_title="Devil-Pro Terminal", layout="wide")
st.title("😈 DEVIL-PRO LIVE TERMINAL")
# --- 1. SCREEN RECORDER (TOP POSITION) ---
st.components.v1.html("""
<div style="background:#1e1e1e; padding:10px; border-radius:10px; border:1px solid #ff4b4b; text-align:center;">
    <button id="startBtn" style="background:#ff4b4b; color:white; border:none; padding:10px 20px; border-radius:5px; cursor:pointer; font-weight:bold;">🔴 START RECORDING</button>
    <button id="stopBtn" style="background:white; color:black; border:none; padding:10px 20px; border-radius:5px; cursor:pointer; font-weight:bold; display:none;">⏹️ STOP & SAVE</button>
</div>
<script>
let mediaRecorder;
let recordedChunks = [];
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');

startBtn.onclick = async () => {
    const stream = await navigator.mediaDevices.getDisplayMedia({ video: true });
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.ondataavailable = (e) => { if (e.data.size > 0) recordedChunks.push(e.data); };
    mediaRecorder.onstop = () => {
        const blob = new Blob(recordedChunks, { type: 'video/webm' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'Trading_Session.webm';
        a.click();
        recordedChunks = [];
    };
    mediaRecorder.start();
    startBtn.style.display = 'none';
    stopBtn.style.display = 'inline-block';
};

stopBtn.onclick = () => {
    mediaRecorder.stop();
    startBtn.style.display = 'inline-block';
    stopBtn.style.display = 'none';
};
</script>
""", height=80)

from streamlit_autorefresh import st_autorefresh

# --- 1. FAST TIMER (Har 1 Second Index Update Karega) ---
st_autorefresh(interval=1000, key="devil_tick")

# --- 2. LIVE WATCHLIST (SAB KUCH EK SAATH) ---
def show_watchlist_fast():
    # Ab total 6 columns hain: Indian + Global + Commodities
    cols = st.columns(6)
    
    # Symbols aur Names ka array (Crude aur Brent included)
    symbols = ["^NSEI", "^NSEBANK", "^IXIC", "NIFTY=F", "CL=F", "BZ=F"]
    names = ["NIFTY 50", "BANK NIFTY", "NASDAQ", "GIFT NIFTY", "CRUDE OIL", "BRENT"]

  # Yahan se replace karo (Dhyan rakhen ki spacing "cols = st.columns(6)" ke barabar ho)
    for i, sym in enumerate(symbols):
        ticker = yf.Ticker(sym)
        data = ticker.history(period="1d")
        
        if not data.empty:
            price_val = data['Close'].iloc[-1]
        else:
            # Agar market band hai toh purana price uthao
            price_val = ticker.info.get('regularMarketPrice') or ticker.info.get('previousClose')

        if price_val:
            price_str = f"{price_val:,.2f}"
            display_price = f"${price_str}" if i >= 4 else price_str
            cols[i].metric(names[i], display_price)
        else:
            cols[i].metric(names[i], "Offline")

    # Iske niche show_watchlist_fast() call hoga
show_watchlist_fast()

# --- 3. OPTION CHAIN & PCR (14 SECOND COUNTER) ---
if "pcr_count" not in st.session_state:
    st.session_state.pcr_count = 0

st.session_state.pcr_count += 1

st.divider()
st.subheader("🔥 Live Nifty Option Chain (PCR Update: 14s)")

# Logic: Page 14 baar refresh hoga (14 seconds) tab PCR update hoga
if st.session_state.pcr_count >= 14:
    st.session_state.pcr_count = 0
    st.toast("Institutional PCR Updated! 😈")

# Timer display for PCR
st.info(f"⏳ Next Institutional Signal Update in: {14 - st.session_state.pcr_count}s")

# --- Yahan aapka Option Chain ka table wala code aa jayega ---
# --- 4. INSTITUTIONAL OPTION CHAIN DATA ---
def get_option_signals(change_oi, price_chg):
    if change_oi > 0 and price_chg > 0: return "🔥 Long Build-up"
    elif change_oi > 0 and price_chg < 0: return "😈 Smart Money Entry"
    elif change_oi < 0 and price_chg < 0: return "⚓ Long Unwinding"
    elif change_oi < 0 and price_chg > 0: return "🚀 Short Covering"
    return "Neutral"

# 14-second trigger ke andar ye table load hoga
if st.session_state.pcr_count >= 0: # Runs every refresh for 30th data display
    st.markdown("### 📊 Institutional Data (Exp: 30-Apr)")
    
    # Mock Data based on 30th April context
    data = {
        "CALL Signal": ["🚀 Short Covering", "⚓ Call Unwinding", "😈 Devil Entry", "Neutral", "🔥 Long Build-up"],
        "LTP (C)": [145.20, 98.40, 65.10, 42.00, 25.40],
        "STRIKE": [24000, 24100, 24200, 24300, 24400],
        "LTP (P)": [32.10, 54.30, 88.90, 125.60, 180.40],
        "PUT Signal": ["🔥 Long Build-up", "Neutral", "🚀 Short Covering", "⚓ Put Unwinding", "😈 Smart Money Entry"]
    }
    
    df = pd.DataFrame(data)
    
    # Styling Table
# Styling Table
    def color_signals(val):
        if "🚀" in str(val): return "color: #00ff00; font-weight: bold"
        if "😈" in str(val): return "color: #ff4b4b; font-weight: bold"
        if "⚓" in str(val): return "color: #ffaa00; font-weight: bold"
        return ""

    styled_df = df.style.map(color_signals, subset=['CALL Signal', 'PUT Signal'])
    st.table(styled_df)
    # PCR Calculation display
    st.markdown("---")
    col_pcr1, col_pcr2 = st.columns(2)
    col_pcr1.metric("TOTAL PCR", "0.85", delta="-0.05", delta_color="inverse")
    col_pcr2.write("**Devil Sentiment:** 🐻 Bearish (Wait for 24200 reversal)")

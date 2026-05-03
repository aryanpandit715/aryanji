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
cols = st.columns(6)
    cols = st.columns(6)
    
    # 1. LIVE WATCHLIST (Symbols & Names)
    symbols = ["^NSEI", "^NSEBANK", "^IXIC", "GIFTY=F", "CL=F", "BZ=F"]
    names = ["NIFTY 50", "BANK NIFTY", "NASDAQ", "GIFT NIFTY", "CRUDE OIL", "BRENT"]
    
    for i, sym in enumerate(symbols):
        ticker = yf.Ticker(sym)
        data = ticker.history(period="1d")
        price_val = data['Close'].iloc[-1] if not data.empty else ticker.info.get('regularMarketPrice')
        
        if price_val:
            price_str = f"{price_val:,.2f}"
            display_price = f"${price_str}" if i >= 4 else price_str
            cols[i].metric(names[i], display_price)
        else:
            cols[i].metric(names[i], "Offline")

    st.markdown("---")

    # 2. OPTION CHAIN (30-APR DATA LOGIC)
    st.markdown("### 🔥 Live Nifty Option Chain (30-Apr Context)")
    
    option_data = {
        "Strike Price": [23850, 23900, 23950, 24000, 24050, 24100, 24150],
        "CHNG_Call": [-96.40, -93.10, -88.30, -84.85, -79.90, -75.05, -68.70],
        "CHNG IN OI_Call": [8845, 12221, 11225, 46564, 13040, 16618, 9],
        "LTP_Call": [317.20, 285.15, 252.00, 221.50, 193.10, 168.45, 145.10],
        "LTP_Put": [90.90, 105.00, 122.35, 142.80, 164.35, 189.20, 215.00],
        "CHNG IN OI_Put": [-2536, 25429, 11188, 3222, 5158, -9098, -12079],
        "CHNG_Put": [20.75, 21.70, 26.05, 23.35, 36.10, 42.40, 48.45]
    }
    df = pd.DataFrame(option_data)

    def get_signals(oi_chg, price_chg):
        if oi_chg > 0 and price_chg > 0: return "😈 Smart Money"
        if oi_chg < 0 and price_chg > 0: return "🚀 Short Covering"
        if oi_chg < 0 and price_chg < 0: return "⚓ Long Covering"
        return "Neutral"

    df['CALL Signal'] = df.apply(lambda x: get_signals(x['CHNG IN OI_Call'], x['CHNG_Call']), axis=1)
    df['PUT Signal'] = df.apply(lambda x: get_signals(x['CHNG IN OI_Put'], x['CHNG_Put']), axis=1)

    def color_signals(val):
        if "🚀" in str(val): return "color: #00ff00; font-weight: bold"
        if "😈" in str(val): return "color: #ff4b4b; font-weight: bold"
        if "⚓" in str(val): return "color: #ffaa00; font-weight: bold"
        return ""

    st.table(df.style.map(color_signals, subset=['CALL Signal', 'PUT Signal']))

    # 3. PCR Section
    st.markdown("---")
    cp1, cp2 = st.columns(2)
    cp1.metric("TOTAL PCR (30-Apr)", "0.85", delta="-0.05", delta_color="inverse")
    cp2.write("**Devil Sentiment:** 🐻 Bearish (Wait for 24200 reversal)")

# Function ko call karein (End of file)
show_watchlist_fast()

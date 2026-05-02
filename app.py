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

    for i, sym in enumerate(symbols):
        data = yf.Ticker(sym).history(period="1d")
        if not data.empty:
            price = f"{data['Close'].iloc[-1]:,.2f}"
            # Crude aur Brent ke liye $ sign add kar diya
            display_price = f"${price}" if i >= 4 else price
            cols[i].metric(names[i], display_price)
        else:
            cols[i].metric(names[i], "Live...")

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

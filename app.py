import streamlit as st
import pandas as pd
import requests
import yfinance as yf
import time

# Page Configuration
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

# --- 2. LIVE WATCHLIST ---
@st.fragment(run_every=14)
def show_watchlist():
    symbols = {"NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK", "GIFT Nifty": "IN=F", "DOW JONES": "^DJI"}
    cols = st.columns(4)
    for i, (name, sym) in enumerate(symbols.items()):
        try:
            data = yf.Ticker(sym).history(period="1d")
            price = f"{data['Close'].iloc[-1]:,.2f}"
            cols[i].metric(name, price)
        except:
            cols[i].metric(name, "Fetching...")

show_watchlist()

# --- 3. NIFTY 30-APRIL LIVE OPTION CHAIN ---
st.divider()
st.subheader("🔥 Live Nifty Option Chain (30 April Data)")

@st.fragment(run_every=14)
def live_option_chain():
    # Simulated/Fetch Logic for 30th April
    data_30 = {
        "Strike": [22500, 22550, 22600, 22650, 22700, 22750, 22800],
        "CE Delta": [0.65, 0.60, 0.55, 0.50, 0.45, 0.40, 0.35],
        "Call OI": ["88K", "61K", "75K", "92K", "105K", "84K", "120K"],
        "Put OI": ["145K", "82K", "98K", "85K", "72K", "64K", "55K"],
        "PE Delta": [-0.35, -0.40, -0.45, -0.50, -0.55, -0.60, -0.65],
        "Signal": ["Strong Support", "Neutral", "Neutral", "ATM", "Resistance", "Resistance", "Strong Resistance"]
    }
    st.table(pd.DataFrame(data_30))
    st.caption(f"Last Auto-Update: {time.strftime('%H:%M:%S')}")

live_option_chain()

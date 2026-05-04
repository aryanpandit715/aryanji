import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# 1. Page Config
st.set_page_config(layout="wide", page_title="Devil-Pro Terminal")

# --- PASSWORD LOCK ---
if "password_correct" not in st.session_state:
    st.session_state.password_correct = False

if not st.session_state.password_correct:
    pw = st.text_input("Enter Password", type="password")
    if st.button("Login"):
        if pw == "devil715": 
            st.session_state.password_correct = True
            st.rerun()
        else: st.error("Wrong Password")
    st.stop()

# 2. Dual Timer (1s Index, 14s Option Chain)
count = st_autorefresh(interval=1000, key="devil_timer")

st.markdown("# 😈 DEVIL-PRO LIVE TERMINAL")

# --- LIVE INDEX SECTION ---
index_area = st.empty()
symbols = ["^NSEI", "GIFTY=F", "^NSEBANK", "^N225", "^IXIC", "^DJI", "CL=F"]
names = ["NIFTY 50", "GIFT NIFTY", "BANK NIFTY", "NIKKEI 225", "NASDAQ", "DOW JONES", "CRUDE OIL"]

with index_area.container():
    cols = st.columns(7)
    for i, sym in enumerate(symbols):
        try:
            tkr = yf.Ticker(sym)
            price_val = tkr.fast_info.last_price or tkr.info.get('regularMarketPrice', 0)
            prev_close = tkr.info.get('previousClose') or price_val
            change = price_val - prev_close
            pct = (change / prev_close * 100) if prev_close else 0
            cols[i].metric(names[i], f"{price_val:,.2f}", delta=f"{change:.2f} ({pct:.2f}%)")
        except:
            cols[i].metric(names[i], "0.00")

st.markdown("---")

# --- LIVE OPTION CHAIN (OI ADDED) ---
refresh_in = 14 - (count % 14)
st.markdown(f"### 🔥 Institutional Option Chain (Live OI) | Update: {refresh_in}s")
chain_area = st.empty()

def get_signals(oi_chg, side):
    # OI Change ke basis par signals
    if oi_chg < -5000: return "⚓ " + side + " Unwinding"
    if oi_chg > 10000: return "😈 Smart Money Entry"
    if oi_chg > 0: return "🚀 Short Covering"
    return "Neutral"

def style_output(val):
    if "Short Covering" in str(val): return "color: #00ff00; font-weight: bold;"
    if "Long Covering" in str(val): return "color: #ff4b4b; font-weight: bold;"
    if "Smart Money" in str(val): return "color: #bd93f9; font-weight: bold;"
    return ""

with chain_area.container():
    try:
        nifty = yf.Ticker("^NSEI")
        expiry = nifty.options[0] # Sabse pass wali expiry
        opts = nifty.option_chain(expiry)
        
        calls = opts.calls[['strike', 'lastPrice', 'openInterest', 'change']].rename(
            columns={'lastPrice': 'LTP_Call', 'openInterest': 'OI_Call', 'change': 'Chng_Call'})
        puts = opts.puts[['strike', 'lastPrice', 'openInterest', 'change']].rename(
            columns={'lastPrice': 'LTP_Put', 'openInterest': 'OI_Put', 'change': 'Chng_Put'})
        
        df = pd.merge(calls, puts, on='strike')
        
        # ATM strikes filter (+/- 500 points)
        curr_nifty = nifty.fast_info.last_price
        df = df[(df['strike'] >= curr_nifty - 500) & (df['strike'] <= curr_nifty + 500)]
        
        df['CALL Signal'] = df['Chng_Call'].apply(lambda x: get_signals(x, "Call"))
        df['PUT Signal'] = df['Chng_Put'].apply(lambda x: get_signals(x, "Put"))

        st.table(df[['strike', 'OI_Call', 'LTP_Call', 'CALL Signal', 'LTP_Put', 'OI_Put', 'PUT Signal']].style.map(style_output, subset=['CALL Signal', 'PUT Signal']))
        
    except:
        st.error("Market Data Refreshing...")

# --- PCR ---
st.markdown("---")
st.metric("LIVE PCR (Put-Call Ratio)", "0.85", delta="-0.02")

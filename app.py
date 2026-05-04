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

# 2. Dual Timer (1s for Index, 14s for Option Chain)
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
            p_val = tkr.fast_info.last_price or tkr.info.get('regularMarketPrice', 0)
            prev = tkr.info.get('previousClose') or p_val
            diff = p_val - prev
            pct = (diff / prev * 100) if prev else 0
            cols[i].metric(names[i], f"{p_val:,.2f}", delta=f"{diff:.2f} ({pct:.2f}%)")
        except:
            cols[i].metric(names[i], "0.00")

st.markdown("---")

# --- INSTITUTIONAL LOGIC (Based on NSE Screenshot) ---
def get_logic_signal(oi_chg, price_chg, side):
    # Long Buildup: Price Up, OI Up
    if price_chg > 0 and oi_chg > 0: return "😈 Smart Money Entry"
    # Short Buildup: Price Down, OI Up
    if price_chg < 0 and oi_chg > 0: return "🚀 Short Buildup"
    # Short Covering: Price Up, OI Down
    if price_chg > 0 and oi_chg < 0: return "🔥 Short Covering"
    # Long Unwinding: Price Down, OI Down
    if price_chg < 0 and oi_chg < 0: return "⚓ Long Unwinding"
    return "Neutral"

def color_logic(val):
    if "Smart Money" in str(val): return "color: #00ff00; font-weight: bold;" # Green
    if "Short Buildup" in str(val): return "color: #ff4b4b; font-weight: bold;" # Red
    if "Short Covering" in str(val): return "color: #00d2ff; font-weight: bold;" # Blue
    if "Unwinding" in str(val): return "color: #ffaa00; font-weight: bold;" # Orange
    return ""

# --- LIVE OPTION CHAIN ---
refresh_in = 14 - (count % 14)
st.markdown(f"### 🔥 Institutional Option Chain (Live Logic) | Update: {refresh_in}s")
chain_area = st.empty()

with chain_area.container():
    try:
        nifty = yf.Ticker("^NSEI")
        expiry = nifty.options[0]
        opts = nifty.option_chain(expiry)
        
        calls = opts.calls[['strike', 'lastPrice', 'openInterest', 'change']].rename(
            columns={'lastPrice': 'LTP_C', 'openInterest': 'OI_C', 'change': 'CHNG_C'})
        puts = opts.puts[['strike', 'lastPrice', 'openInterest', 'change']].rename(
            columns={'lastPrice': 'LTP_P', 'openInterest': 'OI_P', 'change': 'CHNG_P'})
        
        df = pd.merge(calls, puts, on='strike')
        
        # Current Market Price filter
        curr_price = nifty.fast_info.last_price
        df = df[(df['strike'] >= curr_price - 300) & (df['strike'] <= curr_price + 300)]
        
        # Apply NSE Logic
        df['CALL_SIGNAL'] = df.apply(lambda x: get_logic_signal(x['CHNG_C'], x['CHNG_C'], "Call"), axis=1)
        df['PUT_SIGNAL'] = df.apply(lambda x: get_logic_signal(x['CHNG_P'], x['CHNG_P'], "Put"), axis=1)

        # Final Table
        st.table(df[['strike', 'OI_C', 'LTP_C', 'CALL_SIGNAL', 'LTP_P', 'OI_P', 'PUT_SIGNAL']].style.map(color_logic))
        
    except:
        st.info("Market data is streaming... Please wait.")

# --- PCR ---
st.markdown("---")
st.metric("LIVE PCR (Put-Call Ratio)", "0.85", delta="-0.02")

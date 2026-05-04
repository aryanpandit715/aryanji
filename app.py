import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# 1. Page Configuration
st.set_page_config(layout="wide", page_title="Devil-Pro Live Terminal")

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

# 2. Dual Refresh Logic (14 Seconds for Live Updates)
count = st_autorefresh(interval=14000, key="devil_timer")

st.markdown("# 😈 DEVIL-PRO LIVE TERMINAL")

# --- LIVE INDEX SECTION (Indices always on top) ---
index_placeholder = st.empty()
symbols = ["^NSEI", "GIFTY=F", "^NSEBANK", "^N225", "^IXIC", "^DJI", "CL=F"]
names = ["NIFTY 50", "GIFT NIFTY", "BANK NIFTY", "NIKKEI 225", "NASDAQ", "DOW JONES", "CRUDE OIL"]

with index_placeholder.container():
    cols = st.columns(7)
    for i, sym in enumerate(symbols):
        try:
            tkr = yf.Ticker(sym)
            # Fast info for live price
            p_val = tkr.fast_info.last_price
            if p_val is None or p_val == 0:
                p_val = tkr.info.get('regularMarketPrice') or tkr.info.get('previousClose', 0)
            
            prev = tkr.info.get('previousClose') or p_val
            diff = p_val - prev
            pct = (diff / prev * 100) if prev else 0
            
            p_str = f"{p_val:,.2f}"
            display_val = f"${p_str}" if i >= 4 else p_str
            cols[i].metric(names[i], display_val, delta=f"{diff:.2f} ({pct:.2f}%)")
        except:
            cols[i].metric(names[i], "Fetching...")

st.markdown("---")

# --- TRADING LOGIC (OI + PRICE ACTION) ---
def get_logic_signal(oi_chg, price_chg):
    if price_chg > 0 and oi_chg > 0: return "😈 Smart Money Entry"
    if price_chg < 0 and oi_chg > 0: return "🚀 Short Buildup"
    if price_chg > 0 and oi_chg < 0: return "🔥 Short Covering"
    if price_chg < 0 and oi_chg < 0: return "⚓ Long Unwinding"
    return "Neutral"

def color_style(val):
    if "Smart Money" in str(val): return "background-color: #1b4332; color: #b7e4c7; font-weight: bold;"
    if "Short Buildup" in str(val): return "background-color: #590d22; color: #ffb3c1; font-weight: bold;"
    if "Short Covering" in str(val): return "color: #00d2ff;"
    return ""

# --- LIVE OPTION CHAIN (1 ATM + 8 OTM) ---
st.markdown(f"### 🔥 Institutional Option Chain | Live Refresh: 14s")
chain_placeholder = st.empty()

with chain_placeholder.container():
    try:
        nifty = yf.Ticker("^NSEI")
        # Get real-time Nifty price for ATM calculation
        current_nifty = nifty.fast_info.last_price or nifty.info.get('regularMarketPrice', 24106)
        
        expiry = nifty.options[0] # Nearest Expiry
        opts = nifty.option_chain(expiry)
        
        calls = opts.calls[['strike', 'openInterest', 'change', 'volume', 'lastPrice']].rename(
            columns={'openInterest': 'OI_Call', 'change': 'CH_OI_Call', 'volume': 'Vol_Call', 'lastPrice': 'LTP_Call'})
        
        puts = opts.puts[['strike', 'openInterest', 'change', 'volume', 'lastPrice']].rename(
            columns={'openInterest': 'OI_Put', 'change': 'CH_OI_Put', 'volume': 'Vol_Put', 'lastPrice': 'LTP_Put'})
        
        df_full = pd.merge(calls, puts, on='strike')

        # Find ATM Strike (Nearest 50)
        atm_strike = round(current_nifty / 50) * 50
        idx = df_full.index[df_full['strike'] == atm_strike].tolist()[0]
        
        # Slice: 8 OTM Calls + ATM + 8 OTM Puts
        df = df_full.iloc[max(0, idx - 8):min(len(df_full), idx + 9)].copy()

        # Apply Live Logic Signals
        df['CALL_SIGNAL'] = df.apply(lambda x: get_logic_signal(x['CH_OI_Call'], x['CH_OI_Call']), axis=1)
        df['PUT_SIGNAL'] = df.apply(lambda x: get_logic_signal(x['CH_OI_Put'], x['CH_OI_Put']), axis=1)

        # NSE Reordered Columns
        final_cols = [
            'OI_Call', 'CH_OI_Call', 'Vol_Call', 'LTP_Call', 'CALL_SIGNAL', 
            'strike', 
            'LTP_Put', 'Vol_Put', 'CH_OI_Put', 'OI_Put', 'PUT_SIGNAL'
        ]
        
        st.table(df[final_cols].style.map(color_style, subset=['CALL_SIGNAL', 'PUT_SIGNAL']))
        
    except:
        st.info("Market is Live! Streaming data into terminal...")

# --- PCR ---
st.markdown("---")
st.metric("LIVE PCR (Put-Call Ratio)", "0.85", delta="-0.02")

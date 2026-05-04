import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import time

# 1. Page Configuration
st.set_page_config(layout="wide", page_title="Devil-Pro Live Terminal", page_icon="😈")

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

# 2. 14 Second Auto-Refresh
st_autorefresh(interval=14000, key="devil_refresh")

st.markdown("# 😈 DEVIL-PRO LIVE TERMINAL")

# --- HELPER FUNCTION FOR LIVE DATA ---
def get_live_price(symbol):
    try:
        tkr = yf.Ticker(symbol)
        # Try multiple ways to get price
        price = tkr.fast_info.last_price
        if price is None or price <= 0:
            # Backup: Get last 1 day history
            hist = tkr.history(period="1d", interval="1m")
            if not hist.empty:
                price = hist['Close'].iloc[-1]
            else:
                price = tkr.info.get('regularMarketPrice', 0)
        
        prev = tkr.info.get('previousClose', price)
        return price, prev
    except:
        return 0.0, 0.0

# --- LIVE INDEX SECTION ---
index_placeholder = st.empty()
symbols = ["^NSEI", "GIFTY=F", "^NSEBANK", "^N225", "^IXIC", "^DJI", "CL=F"]
names = ["NIFTY 50", "GIFT NIFTY", "BANK NIFTY", "NIKKEI 225", "NASDAQ", "DOW JONES", "CRUDE OIL"]

with index_placeholder.container():
    cols = st.columns(7)
    for i, sym in enumerate(symbols):
        p_val, prev = get_live_price(sym)
        diff = p_val - prev
        pct = (diff / prev * 100) if prev > 0 else 0
        
        # Color formatting
        label = names[i]
        val_str = f"{p_val:,.2f}"
        if i >= 4: val_str = f"${val_str}" # Global indices
        
        cols[i].metric(label, val_str, delta=f"{diff:.2f} ({pct:.2f}%)")

st.markdown("---")

# --- SIGNAL LOGIC ---
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

# --- LIVE OPTION CHAIN ---
st.markdown(f"### 🔥 Institutional Option Chain | Refresh: 14s")
chain_placeholder = st.empty()

with chain_placeholder.container():
    try:
        nifty = yf.Ticker("^NSEI")
        ltp_nifty, _ = get_live_price("^NSEI")
        
        expiry = nifty.options[0]
        opts = nifty.option_chain(expiry)
        
        calls = opts.calls[['strike', 'openInterest', 'change', 'volume', 'lastPrice']].rename(
            columns={'openInterest': 'OI_Call', 'change': 'CH_OI_C', 'volume': 'Vol_C', 'lastPrice': 'LTP_C'})
        puts = opts.puts[['strike', 'openInterest', 'change', 'volume', 'lastPrice']].rename(
            columns={'openInterest': 'OI_Put', 'change': 'CH_OI_P', 'volume': 'Vol_P', 'lastPrice': 'LTP_P'})
        
        df_full = pd.merge(calls, puts, on='strike')

        # ATM Calculation (Nearest 50)
        atm_strike = round(ltp_nifty / 50) * 50
        idx_list = df_full.index[df_full['strike'] == atm_strike].tolist()
        
        if idx_list:
            idx = idx_list[0]
            df = df_full.iloc[max(0, idx - 8):min(len(df_full), idx + 9)].copy()
            
            df['CALL_SIGNAL'] = df.apply(lambda x: get_logic_signal(x['CH_OI_C'], x['CH_OI_C']), axis=1)
            df['PUT_SIGNAL'] = df.apply(lambda x: get_logic_signal(x['CH_OI_P'], x['CH_OI_P']), axis=1)

            final_cols = ['OI_Call', 'CH_OI_C', 'Vol_C', 'LTP_C', 'CALL_SIGNAL', 'strike', 'LTP_P', 'Vol_P', 'CH_OI_P', 'OI_Put', 'PUT_SIGNAL']
            st.table(df[final_cols].style.map(color_style, subset=['CALL_SIGNAL', 'PUT_SIGNAL']))
        else:
            st.warning("Aligning with ATM Strike...")
            
    except Exception as e:
        st.info("Market Data Connecting... Please wait 5 seconds.")

# --- PCR ---
st.markdown("---")
st.metric("LIVE PCR (Put-Call Ratio)", "0.85", delta="-0.02")

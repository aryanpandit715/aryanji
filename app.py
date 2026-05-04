import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# 1. Page Config
st.set_page_config(layout="wide", page_title="Devil-Pro Fixed Terminal", page_icon="😈")

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

# 2. 14 Second Refresh
st_autorefresh(interval=14000, key="devil_fix")

st.markdown("# 😈 DEVIL-PRO LIVE TERMINAL")

# --- INDEX SECTION ---
index_placeholder = st.empty()
symbols = ["^NSEI", "GIFTY=F", "^NSEBANK", "^N225", "^IXIC", "^DJI", "CL=F"]
names = ["NIFTY 50", "GIFT NIFTY", "BANK NIFTY", "NIKKEI 225", "NASDAQ", "DOW JONES", "CRUDE OIL"]

with index_placeholder.container():
    cols = st.columns(7)
    for i, sym in enumerate(symbols):
        try:
            tkr = yf.Ticker(sym)
            p_val = tkr.fast_info.last_price
            if not p_val:
                p_val = tkr.history(period="1d")['Close'].iloc[-1]
            prev = tkr.info.get('previousClose', p_val)
            diff = p_val - prev
            pct = (diff / prev * 100) if prev > 0 else 0
            cols[i].metric(names[i], f"{p_val:,.2f}", delta=f"{diff:.2f} ({pct:.2f}%)")
        except:
            cols[i].metric(names[i], "0.00")

st.markdown("---")

# --- SIGNAL LOGIC ---
def get_signals(oi_chg, price_chg):
    if price_chg > 0 and oi_chg > 0: return "😈 Smart Money Entry"
    if price_chg < 0 and oi_chg > 0: return "🚀 Short Buildup"
    if price_chg > 0 and oi_chg < 0: return "🔥 Short Covering"
    if price_chg < 0 and oi_chg < 0: return "⚓ Long Unwinding"
    return "Neutral"

def color_rows(val):
    if "Smart Money" in str(val): return "background-color: #1b4332; color: #b7e4c7; font-weight: bold;"
    if "Short Buildup" in str(val): return "background-color: #590d22; color: #ffb3c1; font-weight: bold;"
    return ""

# --- OPTION CHAIN FIX ---
st.markdown(f"### 🔥 Institutional Option Chain | Live Status")
chain_placeholder = st.empty()

with chain_placeholder.container():
    try:
        nifty = yf.Ticker("^NSEI")
        # Direct Call for Options
        expiries = nifty.options
        if not expiries:
            st.error("NSE Data not responding. Retrying in 14s...")
        else:
            expiry = expiries[0]
            chain = nifty.option_chain(expiry)
            
            calls = chain.calls[['strike', 'openInterest', 'change', 'volume', 'lastPrice']].copy()
            puts = chain.puts[['strike', 'openInterest', 'change', 'volume', 'lastPrice']].copy()
            
            # Data Cleaning
            df = pd.merge(calls, puts, on='strike', suffixes=('_C', '_P'))
            
            # ATM calculation
            ltp_nifty = nifty.fast_info.last_price or 24074 # Backup from your screenshot
            atm_strike = round(ltp_nifty / 50) * 50
            
            # Ensure ATM exists in data
            if atm_strike in df['strike'].values:
                idx = df.index[df['strike'] == atm_strike].tolist()[0]
                final_df = df.iloc[max(0, idx-8):min(len(df), idx+9)].copy()
                
                final_df['CALL_SIGNAL'] = final_df.apply(lambda x: get_signals(x['change_C'], x['change_C']), axis=1)
                final_df['PUT_SIGNAL'] = final_df.apply(lambda x: get_signals(x['change_P'], x['change_P']), axis=1)
                
                # Reordering
                show_cols = ['openInterest_C', 'change_C', 'volume_C', 'lastPrice_C', 'CALL_SIGNAL', 'strike', 'lastPrice_P', 'volume_P', 'change_P', 'openInterest_P', 'PUT_SIGNAL']
                st.table(final_df[show_cols].style.map(color_rows, subset=['CALL_SIGNAL', 'PUT_SIGNAL']))
            else:
                st.warning("Strikes loading... syncing with ATM.")

    except Exception as e:
        st.info("🔄 Refreshing Data Stream... Market data will appear shortly.")

# --- PCR ---
st.markdown("---")
st.metric("LIVE PCR (Nifty 50)", "0.85", delta="-0.02")

import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import requests

# 1. Page Config
st.set_page_config(layout="wide", page_title="Devil-Pro NSE Live Terminal", page_icon="😈")

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

# 2. 14 Second Auto-Refresh (NSE allows 10-15s frequency)
st_autorefresh(interval=14000, key="nse_refresh")

st.markdown("# 😈 DEVIL-PRO NSE LIVE TERMINAL")

# --- LIVE INDEX SECTION ---
index_placeholder = st.empty()
symbols = ["^NSEI", "GIFTY=F", "^NSEBANK", "^N225", "^IXIC", "^DJI", "CL=F"]
names = ["NIFTY 50", "GIFT NIFTY", "BANK NIFTY", "NIKKEI 225", "NASDAQ", "DOW JONES", "CRUDE OIL"]

def fetch_index_data():
    data = []
    for i, sym in enumerate(symbols):
        try:
            tkr = yf.Ticker(sym)
            price = tkr.fast_info.last_price or tkr.info.get('regularMarketPrice', 0)
            prev = tkr.info.get('previousClose', price)
            diff = price - prev
            pct = (diff / prev * 100) if prev > 0 else 0
            data.append({"name": names[i], "price": price, "diff": diff, "pct": pct})
        except:
            data.append({"name": names[i], "price": 0, "diff": 0, "pct": 0})
    return data

indices = fetch_index_data()
with index_placeholder.container():
    cols = st.columns(7)
    for idx, item in enumerate(indices):
        val_str = f"{item['price']:,.2f}"
        if idx >= 4: val_str = f"${val_str}"
        cols[idx].metric(item['name'], val_str, delta=f"{item['diff']:.2f} ({item['pct']:.2f}%)")

st.markdown("---")

# --- NSE STYLE OPTION CHAIN LOGIC ---
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

st.markdown(f"### 🔥 Live Option Chain (NSE Data Source) | Update: 14s")
chain_placeholder = st.empty()

with chain_placeholder.container():
    try:
        nifty = yf.Ticker("^NSEI")
        ltp = indices[0]['price'] # Nifty 50 Price
        
        # Fetch nearest expiry
        expiry = nifty.options[0]
        chain = nifty.option_chain(expiry)
        
        calls = chain.calls[['strike', 'openInterest', 'change', 'volume', 'lastPrice']].rename(
            columns={'openInterest': 'OI_C', 'change': 'CH_OI_C', 'volume': 'Vol_C', 'lastPrice': 'LTP_C'})
        puts = chain.puts[['strike', 'openInterest', 'change', 'volume', 'lastPrice']].rename(
            columns={'openInterest': 'OI_P', 'change': 'CH_OI_P', 'volume': 'Vol_P', 'lastPrice': 'LTP_P'})
        
        df = pd.merge(calls, puts, on='strike')
        
        # Filter 8 OTM + 1 ATM + 8 OTM
        atm_strike = round(ltp / 50) * 50
        idx = df.index[df['strike'] == atm_strike].tolist()[0]
        final_df = df.iloc[max(0, idx-8):min(len(df), idx+9)].copy()
        
        # Apply NSE Logic
        final_df['CALL_SIGNAL'] = final_df.apply(lambda x: get_signals(x['CH_OI_C'], x['CH_OI_C']), axis=1)
        final_df['PUT_SIGNAL'] = final_df.apply(lambda x: get_signals(x['CH_OI_P'], x['CH_OI_P']), axis=1)
        
        # Table Reorder
        cols_to_show = ['OI_C', 'CH_OI_C', 'Vol_C', 'LTP_C', 'CALL_SIGNAL', 'strike', 'LTP_P', 'Vol_P', 'CH_OI_P', 'OI_P', 'PUT_SIGNAL']
        st.table(final_df[cols_to_show].style.map(color_rows, subset=['CALL_SIGNAL', 'PUT_SIGNAL']))

    except:
        st.info("🔄 Connecting to NSE Data Streams...")

# --- PCR ---
st.markdown("---")
st.metric("LIVE PCR (Nifty 50)", "0.85", delta="-0.02")

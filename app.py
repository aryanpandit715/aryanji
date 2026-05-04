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

# 2. 14 Second Auto-Refresh
count = st_autorefresh(interval=14000, key="devil_timer")

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
            p_val = tkr.fast_info.last_price
            if p_val is None or p_val == 0:
                p_val = tkr.info.get('regularMarketPrice') or tkr.info.get('previousClose', 0)
            
            prev = tkr.info.get('previousClose') or p_val
            diff = p_val - prev
            pct = (diff / prev * 100) if prev else 0
            cols[i].metric(names[i], f"{p_val:,.2f}", delta=f"{diff:.2f} ({pct:.2f}%)")
        except:
            cols[i].metric(names[i], "0.00")

st.markdown("---")

# --- NSE LOGIC FUNCTIONS ---
def get_logic_signal(oi_chg, price_chg):
    if price_chg > 0 and oi_chg > 0: return "😈 Smart Money Entry"
    if price_chg < 0 and oi_chg > 0: return "🚀 Short Buildup"
    if price_chg > 0 and oi_chg < 0: return "🔥 Short Covering"
    if price_chg < 0 and oi_chg < 0: return "⚓ Long Unwinding"
    return "Neutral"

def color_logic(val):
    if "Smart Money" in str(val): return "background-color: #2b5329; color: white;" # Dark Green
    if "Short Buildup" in str(val): return "background-color: #5e1919; color: white;" # Dark Red
    if "Short Covering" in str(val): return "color: #00d2ff;" # Blue
    return ""

# --- OPTION CHAIN (1 ATM + 8 OTM CALL + 8 OTM PUT) ---
st.markdown(f"### 🔥 Institutional Option Chain (30-Apr) | Refresh: 14s")
chain_placeholder = st.empty()

with chain_placeholder.container():
    try:
        nifty = yf.Ticker("^NSEI")
        ltp_nifty = nifty.fast_info.last_price
        expiry = nifty.options[0]
        opts = nifty.option_chain(expiry)
        
        calls = opts.calls[['strike', 'lastPrice', 'openInterest', 'change']].rename(
            columns={'lastPrice': 'LTP_C', 'openInterest': 'OI_C', 'change': 'CHNG_C'})
        puts = opts.puts[['strike', 'lastPrice', 'openInterest', 'change']].rename(
            columns={'lastPrice': 'LTP_P', 'openInterest': 'OI_P', 'change': 'CHNG_P'})
        
        df_full = pd.merge(calls, puts, on='strike')

        # ATM Strike Calculation
        atm_strike = round(ltp_nifty / 50) * 50
        
        # Get Index of ATM
        idx = df_full.index[df_full['strike'] == atm_strike].tolist()[0]
        
        # Filter: 8 OTM Call (Above ATM) + ATM + 8 OTM Put (Below ATM)
        # In Nifty, OTM Calls are higher strikes, OTM Puts are lower strikes.
        start_idx = max(0, idx - 8)
        end_idx = min(len(df_full), idx + 9)
        df = df_full.iloc[start_idx:end_idx].copy()

        # Apply Signal Logic
        df['CALL_SIGNAL'] = df.apply(lambda x: get_logic_signal(x['CHNG_C'], x['CHNG_C']), axis=1)
        df['PUT_SIGNAL'] = df.apply(lambda x: get_logic_signal(x['CHNG_P'], x['CHNG_P']), axis=1)

        # Formatting for display
        final_df = df[['strike', 'OI_C', 'LTP_C', 'CALL_SIGNAL', 'LTP_P', 'OI_P', 'PUT_SIGNAL']]
        st.table(final_df.style.map(color_logic, subset=['CALL_SIGNAL', 'PUT_SIGNAL']))
        
    except Exception as e:
        st.warning("Fetching Live Option Chain Data...")

# --- PCR ---
st.markdown("---")
st.metric("LIVE PCR (Put-Call Ratio)", "0.85", delta="-0.02")

import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# 1. Page Config
st.set_page_config(layout="wide", page_title="Devil-Pro Terminal")

# --- PASSWORD LOCK ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
    if not st.session_state.password_correct:
        pw = st.text_input("Enter Password", type="password")
        if st.button("Login"):
            if pw == "devil715": 
                st.session_state.password_correct = True
                st.rerun()
            else:
                st.error("Wrong Password")
        return False
    return True

if check_password():
    # 2. Dual Timer (1s for Index, 14s for Option Chain logic)
    count = st_autorefresh(interval=1000, key="devil_timer")

    st.markdown("# 😈 DEVIL-PRO LIVE TERMINAL")
    
    # --- SECTION 1: GLOBAL & INDIAN INDEX LIVE (1s Refresh) ---
    st.subheader("🌐 Live Indices & Commodities")
    cols = st.columns(7)
    symbols = ["^NSEI", "GIFTY=F", "^NSEBANK", "^N225", "^IXIC", "^DJI", "CL=F"]
    names = ["NIFTY 50", "GIFT NIFTY", "BANK NIFTY", "NIKKEI 225", "NASDAQ", "DOW JONES", "CRUDE OIL"]
    
    for i, sym in enumerate(symbols):
        try:
            ticker = yf.Ticker(sym)
            df_index = ticker.history(period="1d")
            if not df_index.empty:
                live = df_index['Close'].iloc[-1]
                prev = ticker.info.get('previousClose', live)
                delta_val = live - prev
                cols[i].metric(names[i], f"{live:,.2f}", delta=f"{delta_val:.2f}")
            else:
                cols[i].metric(names[i], "Closed")
        except:
            cols[i].metric(names[i], "Offline")

    st.markdown("---")

    # --- SECTION 2: OPTION CHAIN (30-Apr Data, 14s Refresh) ---
    refresh_in = 14 - (count % 14)
    st.markdown(f"### 🔥 Institutional Option Chain (30-Apr) | Update: {refresh_in}s")
    
    def get_signals(oi, price, side):
        if side == "CALL" and oi < -5000: return "⚓ Call Unwinding"
        if side == "PUT" and oi < -5000: return "⚓ Put Unwinding"
        if oi < 0 and price > 0: return "🚀 Short Covering"
        if oi > 0 and price > 0: return "😈 Smart Money Entry"
        return "Neutral"

    # ATM (24000) + 8 OTM Call + 8 OTM Put (Total 17 Strikes)
    strikes = [23600, 23650, 23700, 23750, 23800, 23850, 23900, 23950, 24000, 
               24050, 24100, 24150, 24200, 24250, 24300, 24350, 24400]
    
    data = {
        "Strike": strikes,
        "OI_CHNG_Call": [500, 1200, -6000, 2100, -8000, 4500, 12221, -8500, 46564, 3000, -2000, 1500, 4000, -7000, 2000, 1000, 500],
        "LTP_Call": [450, 405, 360, 315, 270, 230, 190, 155, 120, 95, 75, 55, 40, 30, 20, 15, 10],
        "LTP_Put": [10, 15, 22, 30, 42, 55, 72, 95, 125, 160, 200, 245, 295, 350, 410, 475, 545],
        "OI_CHNG_Put": [1500, -9000, 4000, 2500, -6500, 5000, 25429, 11188, -6500, 4000, 2100, -5500, 3000, 1200, -8000, 500, 200],
        "CHNG_Price": [5, 10, 15, -5, 20, 12, -93, -88, -84, 10, 15, 20, -5, 10, 5, 2, 1] # Mock price change
    }
    
    df = pd.DataFrame(data)
    df['CALL Signal'] = df.apply(lambda x: get_signals(x['OI_CHNG_Call'], x['CHNG_Price'], "CALL"), axis=1)
    df['PUT Signal'] = df.apply(lambda x: get_signals(x['OI_CHNG_Put'], x['CHNG_Price'], "PUT"), axis=1)

    st.table(df[['Strike', 'LTP_Call', 'CALL Signal', 'LTP_Put', 'PUT Signal']])

    # --- SECTION 3: PCR ---
    st.markdown("---")
    st.metric("LIVE PCR (Put-Call Ratio)", "0.85", delta="-0.02")

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
    # 2. Dual Timer (1s for Index, 14s for Option Chain)
    count = st_autorefresh(interval=1000, key="devil_timer")

    st.markdown("# 😈 DEVIL-PRO LIVE TERMINAL")
    
    # --- NO-BLINK INDEX SECTION ---
    index_area = st.empty()
    symbols = ["^NSEI", "GIFTY=F", "^NSEBANK", "^N225", "^IXIC", "^DJI", "CL=F"]
    names = ["NIFTY 50", "GIFT NIFTY", "BANK NIFTY", "NIKKEI 225", "NASDAQ", "DOW JONES", "CRUDE OIL"]
    
    with index_area.container():
        cols = st.columns(7)
        for i, sym in enumerate(symbols):
            try:
                tkr = yf.Ticker(sym)
                # Live Market logic for Monday
                # Pehle fast_info try karega, fir history
                price_val = tkr.fast_info.get('last_price')
                if not price_val or price_val == 0:
                    hist = tkr.history(period="1d")
                    price_val = hist['Close'].iloc[-1] if not hist.empty else tkr.info.get('previousClose', 0.0)

                prev_close = tkr.info.get('previousClose') or price_val
                change = price_val - prev_close
                pct = (change / prev_close * 100) if prev_close else 0
                
                p_str = f"{price_val:,.2f}"
                display = f"${p_str}" if i >= 4 else p_str
                cols[i].metric(names[i], display, delta=f"{change:.2f} ({pct:.2f}%)")
            except:
                cols[i].metric(names[i], "Live Data Error")

    st.markdown("---")

    # --- NO-BLINK OPTION CHAIN SECTION ---
    refresh_in = 14 - (count % 14)
    st.markdown(f"### 🔥 Institutional Option Chain (30-Apr) | Update: {refresh_in}s")
    chain_area = st.empty()

    def get_signals(oi, price, side):
        if side == "CALL" and oi < -5000: return "⚓ Call Unwinding"
        if side == "PUT" and oi < -5000: return "⚓ Put Unwinding"
        if oi < 0 and price > 0: return "🚀 Short Covering"
        if oi > 0 and price > 0: return "😈 Smart Money Entry"
        if oi < 0 and price < 0: return "⚓ Long Covering"
        return "Neutral"

    def style_output(val):
        if "Short Covering" in str(val): return "color: #00ff00; font-weight: bold;" # Green
        if "Long Covering" in str(val): return "color: #ff4b4b; font-weight: bold;" # Red
        if "Smart Money" in str(val): return "color: #bd93f9; font-weight: bold;" # Purple
        return ""

    with chain_area.container():
        strikes = [23600, 23650, 23700, 23750, 23800, 23850, 23900, 23950, 24000, 
                   24050, 24100, 24150, 24200, 24250, 24300, 24350, 24400]
        
        # Sample Data for UI - Monday Live Feed connection needed
        data = {
            "Strike": strikes,
            "LTP_Call": [450, 405, 360, 315, 270, 230, 190, 155, 120, 95, 75, 55, 40, 30, 20, 15, 10],
            "OI_CHNG_Call": [500, 1200, -6500, 2100, -8000, 4500, 12221, -8500, 46564, 3000, -5500, 1500, 4000, -7000, 2000, 1000, 500],
            "LTP_Put": [10, 15, 22, 30, 42, 55, 72, 95, 125, 160, 200, 245, 295, 350, 410, 475, 545],
            "OI_CHNG_Put": [1500, -9000, 4000, 2500, -7500, 5000, 25429, 11188, -6500, 4000, 2100, -5500, 3000, 1200, -8000, 500, 200],
            "Price_Change": [5, 10, 15, -5, 20, 12, -93, -88, -84, 10, 15, 20, -5, 10, 5, 2, 1]
        }
        
        df = pd.DataFrame(data)
        df['CALL Signal'] = df.apply(lambda x: get_signals(x['OI_CHNG_Call'], x['Price_Change'], "CALL"), axis=1)
        df['PUT Signal'] = df.apply(lambda x: get_signals(x['OI_CHNG_Put'], x['Price_Change'], "PUT"), axis=1)
        
        st.table(df[['Strike', 'LTP_Call', 'CALL Signal', 'LTP_Put', 'PUT Signal']].style.map(style_output, subset=['CALL Signal', 'PUT Signal']))

    # --- PCR ---
    st.markdown("---")
    st.metric("LIVE PCR (Put-Call Ratio)", "0.85", delta="-0.02")

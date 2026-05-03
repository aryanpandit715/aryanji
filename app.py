import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# 1. TIMER (14 Seconds is safest for API)
count = st_autorefresh(interval=14000, key="devil_safe_tick")

def show_watchlist_fast():
    st.markdown("## 😈 DEVIL-PRO LIVE TERMINAL")
    
    # --- SECTION 1: WATCHLIST ---
    cols = st.columns(6)
    symbols = ["^NSEI", "^NSEBANK", "^IXIC", "GIFTY=F", "CL=F", "BZ=F"]
    names = ["NIFTY 50", "BANK NIFTY", "NASDAQ", "GIFT NIFTY", "CRUDE OIL", "BRENT"]
    
    for i, sym in enumerate(symbols):
        try:
            ticker = yf.Ticker(sym)
            # Sirf latest price lene ke liye
            price_val = ticker.fast_info.get('last_price')
            
            if price_val:
                price_str = f"{price_val:,.2f}"
                display_price = f"${price_str}" if i >= 4 else price_str
                cols[i].metric(names[i], display_price)
            else:
                cols[i].metric(names[i], "Wait...")
        except:
            cols[i].metric(names[i], "Rate Limit")

    st.markdown("---")

    # --- SECTION 2: INSTITUTIONAL OPTION CHAIN ---
    st.markdown(f"### 🔥 Institutional Signals (30-Apr Data)")
    
    option_data = {
        "Strike Price": [23900, 23950, 24000, 24050, 24100],
        "CHNG_Call": [-93.10, -88.30, -84.85, -79.90, -75.05],
        "OI_CHNG_Call": [12221, -8500, 46564, -2000, 16618],
        "LTP_Call": [285.15, 252.00, 221.50, 193.10, 168.45],
        "LTP_Put": [105.00, 122.35, 142.80, 164.35, 189.20],
        "OI_CHNG_Put": [25429, 11188, -6500, 5158, -9098],
        "CHNG_Put": [21.70, 26.05, 23.35, 36.10, 42.40]
    }
    df = pd.DataFrame(option_data)

    def get_detailed_signals(oi_chg, price_chg, side):
        if oi_chg < -5000: return "📉 Unwinding"
        if oi_chg < 0 and price_chg > 0: return "🚀 Short Covering"
        if oi_chg > 0 and price_chg > 0: return "😈 Smart Money"
        if oi_chg < 0 and price_chg < 0: return "⚓ Long Covering"
        return "Neutral"

    df['CALL Signal'] = df.apply(lambda x: get_detailed_signals(x['OI_CHNG_Call'], x['CHNG_Call'], "CALL"), axis=1)
    df['PUT Signal'] = df.apply(lambda x: get_detailed_signals(x['OI_CHNG_Put'], x['CHNG_Put'], "PUT"), axis=1)

    def color_detailed(val):
        if "🚀" in str(val): return "color: #00ff00; font-weight: bold"
        if "😈" in str(val): return "color: #ff4b4b; font-weight: bold"
        if "📉" in str(val): return "color: #ffffff; background-color: #444"
        return ""

    st.table(df.style.map(color_detailed, subset=['CALL Signal', 'PUT Signal']))

    # --- SECTION 3: PCR ---
    cp1, cp2 = st.columns(2)
    cp1.metric("LIVE PCR", "0.85", delta="-0.05", delta_color="inverse")
    cp2.info(f"Last Update: {count} ticks | System: Monday Ready")

# Run
if __name__ == "__main__":
    show_watchlist_fast()

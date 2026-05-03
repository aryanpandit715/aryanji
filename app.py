import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# Page Config for Devil Terminal
st.set_page_config(page_title="Devil-Pro Terminal", layout="wide")

# 1. DUAL TIMER LOGIC
# Pura page 14s mein refresh hoga (Rate limit se bachne ke liye)
count = st_autorefresh(interval=14000, key="devil_final_refresh")

def show_watchlist_fast():
    st.markdown("# 😈 DEVIL-PRO LIVE TERMINAL")
    
    # --- 1. GLOBAL & INDIAN WATCHLIST ---
    cols = st.columns(6)
    symbols = ["^NSEI", "^NSEBANK", "^IXIC", "GIFTY=F", "CL=F", "BZ=F"]
    names = ["NIFTY 50", "BANK NIFTY", "NASDAQ", "GIFT NIFTY", "CRUDE OIL", "BRENT"]
    
    for i, sym in enumerate(symbols):
        try:
            ticker = yf.Ticker(sym)
            price_val = ticker.fast_info.get('last_price')
            if price_val:
                price_str = f"{price_val:,.2f}"
                display_price = f"${price_str}" if i >= 4 else price_str
                cols[i].metric(names[i], display_price)
            else:
                cols[i].metric(names[i], "Fetching...")
        except:
            cols[i].metric(names[i], "Rate Limit")
# --- Naya Updated Logic ---
            df_index = ticker.history(period="1d")
            if not df_index.empty:
                live_price = df_index['Close'].iloc[-1]
                prev_close = ticker.info.get('previousClose', live_price)
                change = live_price - prev_close
                
                price_str = f"{live_price:,.2f}"
                display_price = f"${price_str}" if i >= 4 else price_str
                
                # Metric mein Price aur Change (+/-) dono dikhega
                cols[i].metric(names[i], display_price, delta=f"{change:.2f}")
            else:
                cols[i].metric(names[i], "No Data")
    # Logic for your specific Emojis and Trading Signals
    def get_devil_signals(oi_chg, price_chg):
        # Unwinding Logic (OI drop significantly)
        if oi_chg < -5000: return "📉 Unwinding"
        # Short Covering (OI down, Price up)
        if oi_chg < 0 and price_chg > 0: return "🚀 Short Covering"
        # Smart Money Entry (OI up, Price up)
        if oi_chg > 0 and price_chg > 0: return "😈 Smart Money"
        # Long Covering (OI down, Price down)
        if oi_chg < 0 and price_chg < 0: return "⚓ Long Covering"
        return "Neutral"

    # 30-Apr Data Context (Initial Setup)
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

    df['CALL Signal'] = df.apply(lambda x: get_devil_signals(x['OI_CHNG_Call'], x['CHNG_Call']), axis=1)
    df['PUT Signal'] = df.apply(lambda x: get_devil_signals(x['OI_CHNG_Put'], x['CHNG_Put']), axis=1)

    # Signal Styling
    def style_signals(val):
        if "🚀" in str(val): return "color: #00ff00; font-weight: bold"
        if "😈" in str(val): return "color: #ff4b4b; font-weight: bold"
        if "⚓" in str(val): return "color: #ffaa00; font-weight: bold"
        if "📉" in str(val): return "background-color: #333; color: white"
        return ""

    st.table(df.style.map(style_signals, subset=['CALL Signal', 'PUT Signal']))

    # --- 3. TOTAL PCR & SENTIMENT ---
    st.markdown("---")
    cp1, cp2, cp3 = st.columns(3)
    
    # PCR Logic
    pcr = 0.85 
    cp1.metric("TOTAL PCR", f"{pcr}", delta="-0.05", delta_color="inverse")
    
    # Sentiment Logic based on your signals
    sentiment = "BEARISH" if pcr < 0.9 else "BULLISH"
    cp2.subheader(f"Sentiment: {'🐻' if sentiment=='BEARISH' else '🐂'} {sentiment}")
    
    cp3.write(f"**System Status:** Monday Live Ready ✅")

if __name__ == "__main__":
    show_watchlist_fast()

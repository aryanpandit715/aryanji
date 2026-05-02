import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Smart-OI Live", layout="wide")
st.title("😈 SMART-OI LIVE TERMINAL")

def get_live_nse():
    url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
    headers = {"user-agent": "Mozilla/5.0", "accept-encoding": "gzip, deflate", "accept-language": "en-US"}
    try:
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers, timeout=10)
        response = session.get(url, headers=headers, timeout=10)
        data = response.json()
        records = data.get('records', {})
        spot = records.get('index', {}).get('last', 0)
        atm = round(spot / 50) * 50
        
        filtered_data = [row for row in data.get('filtered', {}).get('data', []) if abs(row['strikePrice'] - atm) <= 250]
        final_rows = []
        for row in filtered_data:
            ce, pe, sp = row.get('CE', {}), row.get('PE', {}), row['strikePrice']
            # Smart Money Signal
            sig = "😈 DEVIL" if ce.get('openInterest', 0) > 80000 else "🚀 ROCKET" if pe.get('openInterest', 0) > 80000 else "Neutral"
            final_rows.append({"Strike": sp, "Call OI": ce.get('openInterest', 0), "Signal": sig, "Put OI": pe.get('openInterest', 0)})
        return pd.DataFrame(final_rows), spot, atm
    except: return None

data = get_live_nse()

if data:
    df, spot, atm = data
    st.session_state['d'], st.session_state['s'], st.session_state['a'] = df, spot, atm

if 'd' in st.session_state:
    st.markdown(f"### 🎯 SPOT: `{st.session_state['s']}` | ATM: `{st.session_state['a']}`")
    st.table(st.session_state['d'])
    if not data: st.info("Market Closed. Showing last data.")
else:
    st.warning("Connecting to NSE... 😈")

if st.button('🔄 REFRESH NOW'): st.rerun()

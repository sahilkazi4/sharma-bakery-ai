import streamlit as st
import pandas as pd
from groq import Groq
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import requests
import re

# ========================================================
# MAGIC TRICK: HIDE ALL LOGOS & BADGES
# ========================================================
st.set_page_config(page_title="Sharma Bakery AI", page_icon="🍞", initial_sidebar_state="expanded")

hide_st_style = """
            <style>[data-testid="stToolbar"] {visibility: hidden !important;}
            footer {visibility: hidden !important;}
            iframe[title="streamlitAppViewerBadge"] {display: none !important;}
            iframe[src*="badge"] {display: none !important;}
            [data-testid="collapsedControl"] {display: flex !important; visibility: visible !important;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)


# ========================================================
# DISTANCE CALCULATOR FUNCTION
# ========================================================
def get_distance(customer_address):
    try:
        geolocator = Nominatim(user_agent="sharma_bakery_app")
        bakery_loc = (15.5606, 73.9431) # Sanquelim, Goa
        location = geolocator.geocode(customer_address + ", Sanquelim, Goa", timeout=5)
        if location:
            customer_loc = (location.latitude, location.longitude)
            dist = geodesic(bakery_loc, customer_loc).km
            return round(dist, 2)
        else:
            return None
    except:
        return None

# ========================================================
# LIVE MENU FETCH
# ========================================================
@st.cache_data(ttl=60)
def get_live_menu():
    try:
        sheet_url = "https://docs.google.com/spreadsheets/d/1KIKX4Jm79Y2KwF75HG80uQflNpfOnU1b5hz4MgDRrz8/export?format=csv"
        df = pd.read_csv(sheet_url)
        df.columns = df.columns.str.strip()
        menu_text = ""
        for index, row in df.iterrows():
            if pd.notna(row.get('Item Name')) and pd.notna(row.get('Price')):
                menu_text += f"{index + 1}. {row['Item Name']}: ₹{row['Price']}\n"
        return menu_text
    except Exception as e:
        return f"🚨 Error: {str(e)}"

LIVE_MENU = get_live_menu()

# ========================================================
# AI SETUP & RULES
# ========================================================
API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=API_KEY)

# Yaha WhatsApp link me 'Rs.' specify kiya gaya hai taaki '%u20b9' bug na aaye.
business_rules = f"""
Aap 'Sharma Bakery' ke official AI order manager ho.

Business Details:
- Shop Name: Sharma Bakery
- Location: Sanquelim, Goa

Menu & Prices:
{LIVE_MENU}

DELIVERY RULES:
1. Free Delivery: If items total >= ₹500.
2. Paid Delivery: Within 1km = ₹20, Above 1km = ₹30. (System will provide distance).

ORDER PROCESSING:
1. Collect NAME, ADDRESS, and PHONE NUMBER.
2. Order confirm hone par aapko 2 cheezein karni hain:

PEHLA KAAM: Customer ko sirf ek Shop Owner ka WhatsApp link dena hai.
🚨 STRICT RULE: WhatsApp link me ₹ symbol BILKUL USE NAHI KARNA HAI. Sirf 'Rs.' use karein warna link toot jayega!
Link Format:[👉 Click Here to Send Order to Shop Owner](https://wa.me/919765070870?text=NEW%20ORDER%20RECEIVED!%0A%0A*Customer%20Name:*%20[Name]%0A*Phone:*%20[Phone]%0A*Address:*%20[Address]%0A%0A*Order%20Details:*%0A[Items]%0A%0A*Subtotal:*%20Rs.[Subtotal]%0A*Delivery:*%20Rs.[Delivery]%0A*Total:*%20Rs.[Total])

DOOSRA KAAM: App Admin ke Database ke liye ek Hidden Log generate karna hai. Apne response ke sabse aakhir me bilkul is format me likhein:
===ORDER_LOG===
Name: [Name]
Phone: [Phone]
Address: [Address]
Items: [Item list]
Total Amount: Rs. [Total]
===END_LOG===
"""

# ========================================================
# UI & CHAT LOGIC
# ========================================================
with st.sidebar:
    st.markdown("### 📋 Today's Live Menu")
    st.text(LIVE_MENU)
    if st.button("🔄 Refresh Menu / Clear Chat"):
        st.cache_data.clear()
        st.session_state.messages = [{"role": "system", "content": business_rules}]
        st.rerun()

st.title("🍞 Sharma Bakery AI Assistant")
st.write("Swagat hai! Humari bakery ya menu ke baare me kuch bhi puchiye.")

if "messages" not in st.session_state:
    st.session_state.messages =[{"role": "system", "content": business_rules}]
else:
    st.session_state.messages[0]["content"] = business_rules

for msg in st.session_state.messages:
    if msg["role"] not in["system", "hidden_log"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

user_input = st.chat_input("Apna sawaal yaha type karein...")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
    
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    dist = get_distance(user_input)
    hidden_context = ""
    if dist is not None:
         hidden_context = f"\n\n[SYSTEM NOTE: Distance is {dist} km. Add delivery charge.]"
    
    api_messages =[m for m in st.session_state.messages if m["role"] != "hidden_log"]
    if hidden_context:
        api_messages[-1] = {"role": "user", "content": user_input + hidden_context}

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=api_messages,
            temperature=0.3,
            max_tokens=1024,
        )
        
        response_text = completion.choices[0].message.content
        
        # -------------------------------------------------------------
        # THE MAGIC: Extracting Hidden Log & Sending to Google Sheets
        # -------------------------------------------------------------
        display_text = response_text
        
        if "===ORDER_LOG===" in response_text:
            # AI ke response me se hidden log dhundo
            match = re.search(r"===ORDER_LOG===(.*?)===END_LOG===", response_text, re.DOTALL)
            if match:
                order_info = match.group(1).strip()
                
                # Google Sheet par data bhejna
                webhook_url = st.secrets.get("WEBHOOK_URL", "")
                if webhook_url:
                    try:
                        requests.post(webhook_url, json={"order_details": order_info})
                    except Exception as e:
                        pass # Agar error aaye toh customer ko na dikhe
                        
            # Customer ko dikhne wale message se log ko mita dena
            display_text = re.sub(r"===ORDER_LOG===.*?===END_LOG===", "", response_text, flags=re.DOTALL).strip()
        # -------------------------------------------------------------
        
        with st.chat_message("assistant"):
            st.markdown(display_text)
            
        st.session_state.messages.append({"role": "assistant", "content": display_text})
        
    except Exception as e:
        st.error(f"Error aagaya: {e}")
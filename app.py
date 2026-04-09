import streamlit as st
import pandas as pd
from groq import Groq
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# ========================================================
# MAGIC TRICK: HIDE ALL LOGOS & BADGES
# ========================================================
st.set_page_config(page_title="Sharma Bakery AI", page_icon="🍞")

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            [data-testid="stToolbar"] {visibility: hidden !important;}
            iframe[title="streamlitAppViewerBadge"] {display: none !important;}
            iframe[src*="badge"] {display: none !important;}
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
# FUNCTION: GOOGLE SHEET SE LIVE MENU LAANA (1 Min Timer)
# ========================================================
@st.cache_data(ttl=30)  # Har 30 sec me sheet ko check karega
def get_live_menu():
    try:
        # Aapka exact Google Sheet CSV link
        sheet_url = "https://docs.google.com/spreadsheets/d/1KIKX4Jm79Y2KwF75HG80uQflNpfOnU1b5hz4MgDRrz8/export?format=csv"
        df = pd.read_csv(sheet_url)
        
        menu_text = ""
        for index, row in df.iterrows():
            # Check kar rahe hain ki Item Name aur Price columns sheet me hain ya nahi
            menu_text += f"{index + 1}. {row['Item Name']}: ₹{row['Price']}\n"
        return menu_text
    except Exception as e:
        # Agar error aaye toh app crash na ho
        return f"[Error in Sheet: Check column names 'Item Name' and 'Price'.]\nBackup Menu:\n1. Black Forest Cake: ₹500"

LIVE_MENU = get_live_menu()


# ========================================================
# 1. GROQ AI INTEGRATION & SETUP
# ========================================================
API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=API_KEY)


# ========================================================
# 2. AI TRAINING PART (System Prompt with LIVE MENU)
# ========================================================
business_rules = f"""
Aap 'Sharma Bakery' ke official AI customer support agent aur order manager ho.
Aapka kaam customers ki help karna aur professionally unka order book karna hai.

Business Details:
- Shop Name: Sharma Bakery
- Timings: Subah 9:00 AM se Raat 10:00 PM (Mon-Sun)
- Location: Sanquelim, Goa
- Owner WhatsApp Number: 919765070870 

Menu & Prices (Sirf yahi items bechne hain):
{LIVE_MENU}

DELIVERY CHARGES RULES (Strictly Follow):
1. Free Delivery: Agar items ka total ₹500 ya usse zyada hai.
2. Paid Delivery (Agar items ka total ₹500 se kam hai):
   - Agar distance 1km ya usse kam hai: ₹20 extra charge.
   - Agar distance 1km se zyada hai: ₹30 extra charge.
   (Note: System aapko backend se distance calculate karke batayega. Agar distance na mile, toh default ₹30 charge lagana.)

Order Processing Rules:
1. NAAM, ADDRESS, aur PHONE NUMBER zaroor lein.
2. Bill me "Subtotal" aur "Delivery Charge" alag dikhayein.
3. Order confirm hone par ye exact WhatsApp link dein:
[👉 Click Here to Send Order to Bakery](https://wa.me/919765070870?text=NEW%20ORDER%20RECEIVED!%0A%0A*Customer%20Name:*%20[Customer_Ka_Naam]%0A*Phone:*%20[Customer_Ka_Number]%0A*Address:*%20[Customer_Ka_Address]%0A%0A*Order%20Details:*%0A[Item_1]%20-%20Rs.[Price]%0A[Item_2]%20-%20Rs.[Price]%0A%0A*Subtotal:*%20Rs.[Subtotal]%0A*Delivery%20Charge:*%20Rs.[Delivery_Fee]%0A*Total%20Amount:*%20Rs.[Total_Amount])

General Rules:
- Hamesha Hinglish me aur politely baat karein.
"""

# ========================================================
# 3. APPLICATION UI & CHAT LOGIC
# ========================================================
# Sidebar me Live Menu dikhana (Customer & Owner dono ke liye helpful)
with st.sidebar:
    st.markdown("### 📋 Today's Live Menu")
    st.text(LIVE_MENU)
    if st.button("🔄 Refresh Menu / Clear Chat"):
        st.cache_data.clear()
        st.session_state.messages = [{"role": "system", "content": business_rules}]
        st.rerun()

st.title("🍞 Sharma Bakery AI Assistant")
st.write("Swagat hai! Humari bakery ya menu ke baare me kuch bhi puchiye.")

# Session state handle karna (Yahi sabse zaroori fix tha)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": business_rules}
    ]
else:
    # Agar chat chal rahi hai aur piche se menu update ho, toh AI ko naya menu mil jayega
    st.session_state.messages[0]["content"] = business_rules

# Purane messages screen par dikhana
for msg in st.session_state.messages:
    if msg["role"] != "system":
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
         hidden_context = f"\n\n[SYSTEM NOTE: Customer ka bakery se distance {dist} km calculate hua hai. Bill me isi distance ke hisaab se delivery charge lagao.]"
    
    api_messages = st.session_state.messages.copy()
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
        
        with st.chat_message("assistant"):
            st.markdown(response_text)
            
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        
    except Exception as e:
        st.error(f"Error aagaya: {e}")
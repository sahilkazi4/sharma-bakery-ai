import streamlit as st
import os
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
# NAYA FUNCTION: GOOGLE SHEET SE MENU LAANA
# ========================================================
@st.cache_data(ttl=600)
def get_live_menu():
    try:
        # Yaha apna Publish to web wala CSV link paste karein
        sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaHxTZYbFjTGCSCE5kNLyTuUc4vUkY3V43tHSFxG2y3cbwyn9r3vRLWL42Bw6MricPgK7eoXae7rux/pub?gid=0&single=true&output=csv"
        df = pd.read_csv(sheet_url)
        
        menu_text = ""
        # Sheet ke har row ko padh kar AI ke samajhne layak text banayenge
        for index, row in df.iterrows():
            menu_text += f"{index + 1}. {row['Item Name']}: ₹{row['Price']}\n"
        return menu_text
    except Exception as e:
        # Agar net band ho ya sheet fail ho jaye, toh ye backup menu chalega
        return "1. Black Forest Cake: ₹500\n2. Pineapple Cake: ₹400\n3. Veg Patties: ₹25\n4. Paneer Patties: ₹40\n5. Cold Coffee: ₹80"

# Live menu ko variable me store karna
LIVE_MENU = get_live_menu()


# ========================================================
# 1. GROQ AI INTEGRATION & SETUP
# ========================================================
API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=API_KEY)


# ========================================================
# 2. AI TRAINING PART (System Prompt with LIVE MENU)
# ========================================================
# Yaha dhyan dijiye: Maine hardcoded menu hata kar {LIVE_MENU} laga diya hai
business_rules = f"""
Aap 'Sharma Bakery' ke official AI customer support agent aur order manager ho.
Aapka kaam customers ki help karna aur professionally unka order book karna hai.

Business Details:
- Shop Name: Sharma Bakery
- Timings: Subah 9:00 AM se Raat 10:00 PM (Mon-Sun)
- Location: Sanquelim, Goa
- Owner WhatsApp Number: 919765070870 

Menu & Prices (Aapko sirf yahi items bechne hain):
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
st.title("🍞 Sharma Bakery AI Assistant")
st.write("Swagat hai! Humari bakery ya menu ke baare me kuch bhi puchiye.")

# Session state me messages list setup karna
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": business_rules}
    ]

# Purane messages screen par dikhana (System prompt ko chhod kar)
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

user_input = st.chat_input("Apna sawaal yaha type karein...")

if user_input:
    # 1. User message ko UI me dikhana
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # 2. User message ko history me save karna
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # 3. Distance calculate karna aur hidden context banana
    dist = get_distance(user_input)
    hidden_context = ""
    if dist is not None:
         hidden_context = f"\n\n[SYSTEM NOTE: Customer ka bakery se distance {dist} km calculate hua hai. Bill me isi distance ke hisaab se delivery charge lagao.]"
    
    # 4. API call ke liye temporary messages list banana
    api_messages = st.session_state.messages.copy()
    if hidden_context:
        api_messages[-1] = {"role": "user", "content": user_input + hidden_context}

    # 5. Groq AI se response lena
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=api_messages,
            temperature=0.3,
            max_tokens=1024,
        )
        
        response_text = completion.choices[0].message.content
        
        # 6. Response screen pe dikhana
        with st.chat_message("assistant"):
            st.markdown(response_text)
            
        # 7. Response history me save karna
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        
    except Exception as e:
        st.error(f"Error aagaya: {e}")
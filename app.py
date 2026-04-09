import streamlit as st
import google.generativeai as genai
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# ========================================================
# MAGIC TRICK (NUCLEAR OPTION): HIDE ALL LOGOS & BADGES
# ========================================================
st.set_page_config(page_title="Sharma Bakery AI", page_icon="🍞")

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            /* Deploy aur Toolbar buttons hide karne ke liye */[data-testid="stToolbar"] {visibility: hidden !important;}
            /* Hosted with Streamlit badge (niche right corner) hide karne ke liye */
            iframe[title="streamlitAppViewerBadge"] {display: none !important;}
            iframe[src*="badge"] {display: none !important;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)


# ========================================================
# DISTANCE CALCULATOR FUNCTION (Python Backend)
# ========================================================
def get_distance(customer_address):
    try:
        # Nominatim free geocoding map service hai
        geolocator = Nominatim(user_agent="sharma_bakery_app")
        # Bakery Location (Sanquelim, Goa ke coordinates)
        bakery_loc = (15.5606, 73.9431) 
        
        # User ke text me se address dhoondna Goa ke andar
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
# 1. AI INTEGRATION PART (API ko app se jodna)
# ========================================================
API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY)


# ========================================================
# 2. AI TRAINING PART (Upgraded Rules with Delivery Logic)
# ========================================================
business_rules = """
Aap 'Sharma Bakery' ke official AI customer support agent aur order manager ho.
Aapka kaam customers ki help karna aur professionally unka order book karna hai.

Business Details:
- Shop Name: Sharma Bakery
- Timings: Subah 9:00 AM se Raat 10:00 PM (Mon-Sun)
- Location: Sanquelim, Goa
- Owner WhatsApp Number: 919765070870 

Menu & Prices:
1. Black Forest Cake: ₹500
2. Pineapple Cake: ₹400
3. Veg Patties: ₹25
4. Paneer Patties: ₹40
5. Cold Coffee: ₹80

DELIVERY CHARGES RULES (Strictly Follow):
1. Free Delivery: Agar items ka total ₹500 ya usse zyada hai.
2. Paid Delivery (Agar items ka total ₹500 se kam hai):
   - Agar distance 1km ya usse kam hai: ₹20 extra charge.
   - Agar distance 1km se zyada hai: ₹30 extra charge.
   (Note: System aapko backend se distance calculate karke batayega. Agar backend fail ho jaye ya distance na mile, toh default ₹30 delivery charge lagana.)

Order Processing Rules:
1. Acknowledge with Price: Item order karne par acknowledge karein aur Price batayein.
2. Mandatory Details: NAAM, ADDRESS, aur 10-digit PHONE NUMBER.
3. Order Summary & Total Amount: Confirmation se pehle Bill dikhayein. Bill me "Subtotal" (items ka price) aur "Delivery Charge" alag-alag dikhayein, aur fir "Total Amount" batayein.
4. OTP Verification & WhatsApp Link: 
   Jab order confirm ho jaye toh OTP generate karein aur ye WhatsApp link dein:[👉 Click Here to Send Order to Bakery](https://wa.me/919765070870?text=NEW%20ORDER%20RECEIVED!%0A%0A*Customer%20Name:*%20[Customer_Ka_Naam]%0A*Phone:*%20[Customer_Ka_Number]%0A*Address:*%20[Customer_Ka_Address]%0A%0A*Order%20Details:*%0A[Item_1]%20-%20Rs.[Price]%0A[Item_2]%20-%20Rs.[Price]%0A%0A*Subtotal:*%20Rs.[Subtotal]%0A*Delivery%20Charge:*%20Rs.[Delivery_Fee]%0A*Total%20Amount:*%20Rs.[Total_Amount]%0A*Delivery%20OTP:*%20[Aapne_Jo_OTP_Diya])

General Rules:
- Hamesha Hinglish me aur politely baat karein.
"""

model = genai.GenerativeModel('gemini-2.5-flash-lite', system_instruction=business_rules)


# ========================================================
# 3. APPLICATION KA USER INTERFACE
# ========================================================
st.title("🍞 Sharma Bakery AI Assistant")
st.write("Swagat hai! Humari bakery ya menu ke baare me kuch bhi puchiye.")

if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

for message in st.session_state.chat_session.history:
    # Hum hidden system note ko screen par nahi dikhana chahte, isliye usko filter kar lenge
    display_text = message.parts[0].text
    if "[SYSTEM NOTE:" not in display_text:
        role = "user" if message.role == "user" else "assistant"
        with st.chat_message(role):
            st.markdown(display_text)

user_input = st.chat_input("Apna sawaal yaha type karein...")

if user_input:
    # Customer ka message screen pe dikhana
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # ---------------------------------------------------------
    # INTELLIGENT BACKEND LOGIC (Distance Calculation)
    # ---------------------------------------------------------
    hidden_context = ""
    dist = get_distance(user_input)
    
    if dist is not None:
        # Agar python ko distance mil gaya, toh hum AI ko chupke se ek 'System Note' bhejenge
        hidden_context = f"\n\n[SYSTEM NOTE: Customer ka bakery se distance {dist} km calculate hua hai. Bill me isi distance ke hisaab se delivery charge lagao aur fir batao.]"
    
    # AI se answer mangwana (User message + Hidden Context)
    response = st.session_state.chat_session.send_message(user_input + hidden_context)
    
    # AI ka answer screen pe dikhana (Hidden context hata kar)
    clean_response = response.text.replace(hidden_context, "")
    with st.chat_message("assistant"):
        st.markdown(clean_response)
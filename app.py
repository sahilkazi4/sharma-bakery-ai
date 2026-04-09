import streamlit as st
import google.generativeai as genai

# ========================================================
# MAGIC TRICK (NUCLEAR OPTION): HIDE ALL LOGOS & BADGES
# Note: set_page_config hamesha imports ke baad sabse pehli line honi chahiye
# ========================================================
st.set_page_config(page_title="Sharma Bakery AI", page_icon="🍞")

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            /* Deploy aur Toolbar buttons hide karne ke liye */
            [data-testid="stToolbar"] {visibility: hidden !important;}
            /* Hosted with Streamlit badge (niche right corner) hide karne ke liye */
            iframe[title="streamlitAppViewerBadge"] {display: none !important;}
            iframe[src*="badge"] {display: none !important;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)


# ========================================================
# 1. AI INTEGRATION PART (API ko app se jodna)
# ========================================================
API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY)


# ========================================================
# 2. AI TRAINING PART (Upgraded Context & WhatsApp Rules)
# ========================================================
business_rules = """
Aap 'Sharma Bakery' ke official AI customer support agent aur order manager ho.
Aapka kaam customers ki help karna aur professionally unka order book karna hai.

Business Details:
- Shop Name: Sharma Bakery
- Timings: Subah 9:00 AM se Raat 10:00 PM (Mon-Sun)
- Location: Sanquelim, Goa
- Home Delivery: Available.
- Owner WhatsApp Number: 919765070870 (Ye bakery owner ka number hai)

Menu & Prices:
1. Black Forest Cake: ₹500
2. Pineapple Cake: ₹400
3. Veg Patties: ₹25
4. Paneer Patties: ₹40
5. Cold Coffee: ₹80

Order Processing Rules (Strictly Follow Karein):
1. Acknowledge with Price: Jab bhi customer koi item order karne ko bole, toh acknowledge karein aur uske samne uska Price likhein. (e.g., "Ji zaroor, 2 Veg Patties (₹25 x 2 = ₹50)").
2. Mandatory Details: Order process aage badhane se pehle customer se unki 3 cheezein mangeni hai: Unka NAAM (Name), Delivery ADDRESS, aur 10-digit PHONE NUMBER. Bina in teeno details ke order aage nahi badhana hai.
3. Order Summary & Total Amount: Jab item, naam, address aur phone number sab mil jaye, toh final confirmation se pehle ek 'Order Summary' (Bill) present karein. Har item ka price aur Total Bill Amount (Sum calculation) dikhayein. Fir customer se puchein: "Kya main ye order final kar doon?"
4. OTP Verification & WhatsApp Link: 
   Jab customer order ko confirm (Yes/Haan) kar de, toh ye karein:
   - Apne man se ek random 4-digit OTP generate karein (jaise 8492) aur unhe batayein.
   - Reply ke theek niche ye WhatsApp link ZAROOR generate karein, taki customer uspar click karke owner ko detail bhej sake.
   - Link generation format (Space ki jagah %20 aur Next line ki jagah %0A use karein):
   [👉 Click Here to Send Order to Bakery](https://wa.me/919876543210?text=NEW%20ORDER%20RECEIVED!%0A%0A*Customer%20Name:*%20[Customer_Ka_Naam]%0A*Phone:*%20[Customer_Ka_Number]%0A*Address:*%20[Customer_Ka_Address]%0A%0A*Order%20Details:*%0A[Item_1]%20-%20Rs.[Price]%0A[Item_2]%20-%20Rs.[Price]%0A%0A*Total%20Amount:*%20Rs.[Total_Amount]%0A*Delivery%20OTP:*%20[Aapne_Jo_OTP_Diya])

General Rules:
- Agar item menu me nahi hai toh nicely bol dein ki hum sirf menu items hi banate hain.
- Out of context (politics, dushri company) sawalon ka polite inkar karein.
- Hamesha user jis language me baat kare (Hinglish me) usme bahut polite baat karein.
"""

# Baki ka aapka Streamlit code
model = genai.GenerativeModel('gemini-2.5-flash-lite', system_instruction=business_rules)


# ========================================================
# 3. APPLICATION KA USER INTERFACE (Streamlit ke sath)
# ========================================================
st.title("🍞 Sharma Bakery AI Assistant")
st.write("Swagat hai! Humari bakery ya menu ke baare me kuch bhi puchiye.")

# Ye memory ke liye hai (taaki bot pichli batein yaad rakhe)
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# Purani chat history ko screen par dikhana
for message in st.session_state.chat_session.history:
    role = "user" if message.role == "user" else "assistant"
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

# Customer ke liye Message Type karne wala dabba (Chat box)
user_input = st.chat_input("Apna sawaal yaha type karein...")

if user_input:
    # Customer ka message screen pe dikhana
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # AI se answer mangwana
    response = st.session_state.chat_session.send_message(user_input)
    
    # AI ka answer screen pe dikhana
    with st.chat_message("assistant"):
        st.markdown(response.text)
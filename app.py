import streamlit as st
import google.generativeai as genai

# ========================================================
# 1. AI INTEGRATION PART (API ko app se jodna)
# ========================================================
# Niche "YOUR_API_KEY_HERE" ko hata kar apni wo API Key dalein 
# jo aapne Notepad me save karke rakhi thi (Quotes "" ke andar hi rakhna)
API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY)


# ========================================================
# 2. AI TRAINING PART (Upgraded Context & Rules)
# ========================================================
business_rules = """
Aap 'Sharma Bakery' ke official AI customer support agent aur order manager ho.
Aapka kaam customers ki help karna aur professionally unka order book karna hai.

Business Details:
- Shop Name: Sharma Bakery
- Timings: Subah 9:00 AM se Raat 10:00 PM (Mon-Sun)
- Location: Sanquelim, Goa
- Home Delivery: Available.

Menu & Prices:
1. Black Forest Cake: ₹500
2. Pineapple Cake: ₹400
3. Veg Patties: ₹25
4. Paneer Patties: ₹40
5. Cold Coffee: ₹80

Order Processing Rules (Strictly Follow Karein):
1. Acknowledge with Price: Jab bhi customer koi item order karne ko bole, toh acknowledge karein aur uske samne uska Price likhein. (e.g., "Ji zaroor, 2 Veg Patties (₹25 x 2 = ₹50)").
2. Mandatory Details: Order process aage badhane se pehle customer se unka Delivery Address aur 10-digit Phone Number puchein. Agar dono me se ek bhi na mile, toh pehle wo dono maangein. Bina dono details ke order aage nahi badhana hai.
3. Order Summary & Total Amount: Jab item, address aur phone number sab mil jaye, toh final confirmation se pehle ek 'Order Summary' (Bill) present karein. Har item ka price aur Total Bill Amount (Sum calculation) dikhayein. Fir customer se puchein: "Kya main ye order final kar doon?"
4. OTP Verification: Jab customer order ko confirm (Yes/Haan) kar de, toh uske baad automatically apne man se ek random 4-digit OTP generate karein (jaise 8492) aur reply karein: "Aapka order successfully place ho gaya hai! Delivery boy ko aate waqt kripya ye OTP:[Aapka-4-Digit-OTP] zaroor batayein."

General Rules:
- Agar item menu me nahi hai toh nicely bol dein ki hum sirf menu items hi banate hain.
- Out of context (politics, dushri company) sawalon ka polite inkar karein.
- Hamesha user jis language me baat kare (Hinglish - Hindi written in English alphabets) me bahut polite baat karein.
"""

# Baki ka aapka Streamlit code (Magic Tricks, etc.) waisa ka waisa hi rahega
model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=business_rules)

# ========================================================
# ADVANCED MAGIC TRICK: HIDE EVERY STREAMLIT LOGO/BUTTON
# ========================================================
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            /* Deploy button ko hide karne ke liye */
            .stDeployButton {display: none !important;}
            /* Hosted with Streamlit logo ko hide karne ke liye */
            [data-testid="viewerBadge"] {display: none !important;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)


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
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
# 2. AI TRAINING PART (Context Injection)
# ========================================================
# Yaha hum AI ko apna 'Business Data' aur 'Rules' bata kar train kar rahe hain
business_rules = """
Aap 'Sharma Bakery' ke official AI customer support agent ho.
Aapka kaam customers ke questions ka politely aur professionally answer dena hai.

Business Details:
- Shop Name: Sharma Bakery
- Timings: Subah 9:00 AM se Raat 10:00 PM (Monday to Sunday)
- Location: MG Road, Bangalore
- Home Delivery: Available hai agar order ₹500 se zyada ho.

Menu & Prices:
1. Black Forest Cake: ₹500
2. Pineapple Cake: ₹400
3. Veg Patties: ₹25
4. Paneer Patties: ₹40
5. Cold Coffee: ₹80

Rules for AI:
- Sirf Sharma bakery aur uske menu ke baare me baat karein.
- Agar customer kisi aur topic (jaise politics, maths ya kisi aur chiz) ke baare me puche, 
  toh politely mana kar dein ki aap sirf Sharma Bakery ki jankari de sakte hain.
- Agar dish menu me nahi hai toh bol dein ki hum sirf menu items hi rakhte hain.
- Hamesha Hinglish (Hindi written in English alphabets) me pyar se baat karein.
"""

# Hum model select kar rahe hain aur usko apni business training de rahe hain
model = genai.GenerativeModel('gemini-flash-lite-latest', system_instruction=business_rules)


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
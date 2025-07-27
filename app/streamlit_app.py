import os

import streamlit as st
import requests

from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="MindMate", page_icon="🧠")

API_URL= os.getenv("API_URL", "http://localhost:8000")

# Initialize session state
if "email" not in st.session_state:
    st.session_state.email = None
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🧠 MindMate")
st.subheader("Mental Health Companion")

# --- Login/Register Section ---
with st.sidebar:
    st.header("👤 User")
    if st.session_state.email:
        st.success(f"Logged in as {st.session_state.email}")
        if st.button("Logout"):
            st.session_state.email = None
            st.session_state.messages = []
    else:
        choice = st.radio("Choose Action", ["Login", "Register"])
        email = st.text_input("Your Email")
        name = st.text_input("Name (only for registration)") if choice == "Register" else ""

        if st.button(choice):
            if not email:
                st.error("Please enter an email")
            elif choice == "Register":
                res = requests.post(f"{API_URL}/register_user", json={"email": email, "name": name})
                if res.status_code == 200:
                    st.success("Registered & logged in!")
                    st.session_state.email = email
                else:
                    st.error(res.json().get("detail", "Registration failed"))
            elif choice == "Login":
                if not email:
                    st.error("Please enter an email")
                else:
                    # try to ping the backend using /chat (or create a /get_user later)
                    check = requests.post(f"{API_URL}/user_exists", json={
                        "email": email,
                     })
                    if check.status_code == 200:
                        st.session_state.email = email
                        st.success("Logged in!")
                    else:
                        st.error("This email is not registered. Please register first.")

# --- Chat Section ---
if st.session_state.email:
    st.divider()
    st.header("💬 Chat with MindMate")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("How are you feeling today?")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Call backend
        res = requests.post(f"{API_URL}/chat", json={
            "email": st.session_state.email,
            "message": prompt
        })
        if res.status_code == 200:
            reply = res.json()["response"]
        else:
            reply = "⚠️ Error from server."

        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)

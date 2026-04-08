import streamlit as st
from supabase import create_client

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]

supabase = create_client(url, key)


def login_ui():
    st.subheader("登入 / 註冊")

    email = st.text_input("輸入你的 Email")

    if st.button("寄送登入連結"):
        if email:
            supabase.auth.sign_in_with_otp(
                {
                    "email": email,
                    "options": {
                        "email_redirect_to": st.secrets["APP_URL"]
                    },
                }
            )
            st.success("已寄出登入信，請去信箱點擊")
        else:
            st.error("請輸入 email")


def get_user():
    try:
        session = supabase.auth.get_session()
        if session and session.user:
            return session.user
    except Exception:
        pass
    return None


def logout():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
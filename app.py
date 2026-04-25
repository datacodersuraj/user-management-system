# app.py
import streamlit as st
from db import init_db
import auth

# Initialize DB table (safe to call on every run)
init_db()

st.set_page_config(page_title="User Management", layout="centered")

# -------- session-state defaults (important) --------
st.session_state.setdefault("page", "home")    # current page: home/signup/login/welcome
st.session_state.setdefault("user", None)      # logged-in username

def go_to(page_name: str):
    st.session_state.page = page_name
    st.rerun()   # force immediate rerun so page changes

# ------------ HOME ------------
if st.session_state.page == "home":
    st.title("🔐 User Management System")
    st.write("Choose an action:")
    c1, c2 = st.columns(2)
    with c1:
        st.button("Signup", on_click=go_to, args=("signup",), key="btn_home_signup")
    with c2:
        st.button("Login", on_click=go_to, args=("login",), key="btn_home_login")

# ------------ SIGNUP ------------
elif st.session_state.page == "signup":
    st.title("📝 Signup")
    username = st.text_input("Username", key="su_username")
    password = st.text_input("Password", type="password", key="su_password")
    confirm  = st.text_input("Retype Password", type="password", key="su_confirm")

    if st.button("Create account"):
        if len(username) < 5:
            st.error("Username must be at least 5 characters.")
        elif not auth.is_strong_password(password):
            st.error("Password must have uppercase, lowercase, digit, special char and be at least 8 characters.")
        elif password != confirm:
            st.error("Passwords do not match.")
        else:
            ok, err = auth.create_user(username, password)
            if ok:
                st.success("Account created — please login.")
                st.button("Go to Login", on_click=go_to, args=("login",))
            else:
                if err == "username_exists":
                    st.error("Username already exists — choose another.")
                else:
                    st.error(f"Error: {err}")

    st.button("Back", on_click=go_to, args=("home",))

# ------------ LOGIN ------------
elif st.session_state.page == "login":
    st.title("🔑 Login")
    username = st.text_input("Username", key="li_username")
    password = st.text_input("Password", type="password", key="li_password")

    if st.button("Login"):
        row = auth.get_user(username)
        if row is None:
            st.error("Username does not exist")
        else:
            if auth.check_password(password, row[2]):
                st.session_state.user = username
                go_to("welcome")
            else:
                st.error("Incorrect password")

    st.button("Back", on_click=go_to, args=("home",))

# ------------ WELCOME (after login) ------------
elif st.session_state.page == "welcome":
    if not st.session_state.user:
        st.error("Not signed in. Please login.")
        st.button("Go to Login", on_click=go_to, args=("login",))
    else:
        st.title(f"Welcome, {st.session_state.user} 👋")
        st.write("Choose an action:")

        action = st.radio("", ["Update account", "Delete account", "Logout"], key="welcome_action")

        if action == "Update account":
            new_username = st.text_input("New username", key="up_username")
            new_password = st.text_input("New password", type="password", key="up_password")
            confirm = st.text_input("Confirm new password", type="password", key="up_confirm")
            if st.button("Apply update"):
                if len(new_username) < 5:
                    st.error("Username must be at least 5 characters.")
                elif not auth.is_strong_password(new_password):
                    st.error("New password doesn't meet strength requirements.")
                elif new_password != confirm:
                    st.error("Passwords do not match.")
                else:
                    ok, err = auth.update_user(st.session_state.user, new_username, new_password)
                    if ok:
                        st.success("Account updated.")
                        st.session_state.user = new_username
                    else:
                        if err == "new_username_exists":
                            st.error("That username is already taken.")
                        else:
                            st.error(f"Error: {err}")

        elif action == "Delete account":
            st.warning("This will permanently delete your account.")
            if st.button("Confirm delete"):
                auth.delete_user(st.session_state.user)
                st.success("Account deleted.")
                st.session_state.user = None
                go_to("home")

        else:  # Logout
            if st.button("Logout"):
                st.session_state.user = None
                go_to("home")

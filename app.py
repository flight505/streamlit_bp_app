import streamlit as st

from modules import about, home  # Import your custom page modules here
from multiapp import MultiApp

app = MultiApp()

# Add all the pages to the app using their respective function names
# app.add_app("About", about.app)
app.add_app("🏠 Home", home.app)

if __name__ == "__main__":
    st.set_page_config(
        page_title="Age-based Blood Pressure Reference",
        page_icon="🩺",
        layout="centered",
        initial_sidebar_state="collapsed",
        menu_items={
            "Get Help": "https://github.com/flight505/streamlit_bp_app",
            "Report a bug": "https://github.com/flight505/streamlit_bp_app/issues",
            "About": "Designed to determine hypertension stages and percentiles based on input blood pressure data",
        },
    )
app.run()

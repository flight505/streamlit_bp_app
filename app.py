import streamlit as st
from multiapp import MultiApp
from modules import home, about  # Import your custom page modules here

app = MultiApp()

# Add all the pages to the app using their respective function names
# app.add_app("About", about.app)
app.add_app("🏠 Home", home.app)

# if __name__ == "__main__":
#     st.set_page_config(
#         page_title="Age-based Blood Pressure Reference",
#         page_icon="🩺",
#         layout="wide",
#         initial_sidebar_state="collapsed",
#         menu_items={
#             'Get Help': 'https://www.extremelycoolapp.com/help',
#             'Report a bug': "https://www.extremelycoolapp.com/bug",
#      ßß       'About': "# This is a header. This is an *extremely* cool app!"
#         }
#     )
app.run()

import streamlit as st
import requests



# Upload Page
st.title("Upload JSON File")
uploaded_json = st.file_uploader("Choose a JSON file")

if st.button("Submit"):
    # Process the uploaded JSON file (you can add your processing logic here)
    st.success("JSON file processed successfully")
    st.session_state.page = "home"

st.button("Back", on_click=lambda: st.session_state.pop("page", None))

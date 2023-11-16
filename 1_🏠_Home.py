import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


api_endpoint = os.environ.get('API_ENDPOINT')
                              
st.set_page_config(
    page_title="JSON-to-DB",
    page_icon="👋",
)
                              
st.title("JSON-to-DB Web Application")

# st.title("Upload JSON")
# File upload section
st.subheader("Upload a JSON File")
uploaded_json = st.file_uploader("Choose a JSON file")
uploaded_keys=[]
# Table name input
st.subheader("Enter the Table Name")
table_name = st.text_input("Table Name")

# Display JSON keys
selected_keys = []
if uploaded_json is not None:
    st.subheader("JSON Keys in the Uploaded File")
    uploaded_data = json.loads(uploaded_json.read())
    uploaded_keys = list(uploaded_data[0].keys())
    selected_keys = st.multiselect("Select keys to make unique", uploaded_keys)

# Submit button
if st.button("Submit"):
    if uploaded_json is None:
        st.warning("Please upload a JSON file.")
    elif not table_name:
        st.warning("Please enter a table name.")
    elif not selected_keys:
        st.warning("Please select at least one key to make it unique.")
    else:
        try:
            # try:
            #     json_data = uploaded_json.read()
            #     data = json.loads(json_data)
            #     # Process data
            # except json.JSONDecodeError as e:
            #     st.error(f"Invalid JSON format: {uploaded_data}")

            response = requests.post(
                f'{api_endpoint}/api/v1/json?table_name={table_name}',
                json=uploaded_data,
                params={"unique_keys": selected_keys}
            )
            data= response.json()
            if data.get('message'):
                st.success(data["message"])
            else:
                st.error(data['error'])
        except Exception as e:
            st.error(f"An error occurred: {str(e)} - Error {x}")

import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
st.set_page_config(
    page_title="JSON-to-DB",
    page_icon="👋",
)


api_endpoint = os.environ.get('API_ENDPOINT')
                              

# Function to generate API key with specified permissions
def generate_api_key(permissions):
    data = {"permissions": permissions}
    response = requests.post(f'{api_endpoint}/api/v1/generate_api_key', json=data)
    result = response.json()
    return result.get("api_key"), result.get("permissions")

# Streamlit app

st.title("Generate API Key")

# Checkbox to select permissions
read_permission = st.checkbox("Read Permission")
write_permission = st.checkbox("Write Permission")

if st.button("Generate API Key"):
    # Determine the selected permissions
    permissions = []
    if read_permission:
        permissions.append("read")
    if write_permission:
        permissions.append("write")

    # Generate API key
    api_key, selected_permissions = generate_api_key(permissions)

    # Display the generated API key and permissions
    st.success(f"API Key: {api_key}")
    st.info(f"Note : Key=Authorization and Value={api_key}")
    st.success(f"Permissions: {', '.join(selected_permissions)}")

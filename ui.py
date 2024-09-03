import streamlit as st
import requests
import json

st.title("JSON-to-DB Web Application")

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
                f'http://localhost:5000/api/v1/json?table_name={table_name}',
                json=uploaded_data,
                params={"unique_keys": selected_keys}
            )
            st.success(response.json()["message"])
        except Exception as e:
            import traceback
            x= str(traceback.format_exc())
            st.error(f"An error occurred: {str(e)} - Error {x}")


# Search and Filter section
st.subheader("Search and Filter Table")
search_table_name = st.text_input("Enter the Table Name for Search and Filter")
selected_column = st.selectbox("Select a column for filtering", uploaded_keys if uploaded_keys else [])
search_string = st.text_input("Enter the search string")
if st.button("Search and Filter"):
    if not search_table_name:
        st.warning("Please enter a table name for searching and filtering.")
    elif not selected_column:
        st.warning("Please select a column for filtering.")
    elif not search_string:
        st.warning("Please enter a search string.")
    else:
        # Send a request to the backend for searching and filtering
        response = requests.get(
            f'http://localhost:5000/api/v1/filter?table_name={search_table_name}&column={selected_column}&search_string={search_string}'
        )
        search_results = response.json()
        st.subheader("Search Results")
        if not search_results:
            st.info("No matching records found.")
        else:
            for result in search_results:
                st.write(result)

st.write("\n---")
# Other sections of your Streamlit app (CRUD, search, and more) can be added below

st.write("\n---")
# Other sections of your Streamlit app (CRUD, search, and more) can be added below

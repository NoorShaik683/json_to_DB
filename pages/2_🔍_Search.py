import streamlit as st
import requests
import pandas as pd
import base64
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


api_endpoint = os.environ.get('API_ENDPOINT')
ADMIN_KEY = 'admin_123'

def get_csv_download_link(df):
    csv_file = df.to_csv(index=False)
    b64 = base64.b64encode(csv_file.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="search_results.csv">Download CSV File</a>'


# Function to get all table names from the backend
def get_table_names():
    response = requests.get(f'{api_endpoint}/api/v1/tables')
    table_names = response.json()
    return table_names

# Function to get columns for a given table name
def get_table_columns(table_name):
    response = requests.get(f'{api_endpoint}/api/v1/columns/{table_name}')
    columns = response.json()
    return columns

# Function to search and filter records
def search_and_filter(table_name, selected_column, search_string):
    response = requests.get(
        f'{api_endpoint}/api/v1/filter?table_name={table_name}&column={selected_column}&search_string={search_string}',
        headers={'Authorization':ADMIN_KEY}
    )
    search_results = response.json()
    return search_results

# Streamlit app
st.set_page_config(
    page_title="JSON-to-DB",
    page_icon="👋",
)

# st.title("Upload JSON")
st.title("Search and Filter Table")

# Dropdown for table names with search option
table_names = get_table_names()
selected_table = st.selectbox("Select a Table", table_names, key="table_names")

# Get columns based on the selected table
if selected_table:
    columns = get_table_columns(selected_table)
    selected_column = st.selectbox("Select a Column", columns, key="columns")
    search_string = st.text_input("Enter the search string")

    if st.button("Search and Filter"):
        # Call the search_and_filter function
        search_results = search_and_filter(selected_table, selected_column, search_string)
        # Display search results
        if not search_results:
            st.info("No matching records found.")
        elif not type(search_results) is list and search_results.get('error'):
            st.error(search_results.get('error'))
        else:
            df = pd.DataFrame(search_results, columns=columns)
            df.index+=1
            st.dataframe(df)
            # page_number = st.selectbox("Select Page", range(1, (len(df) // 20) + 2))
            # start_index = (page_number - 1) * 2
            # end_index = min(len(df), start_index + 20)
            # st.dataframe(df.iloc[start_index:end_index])

                        # st.write(df)  # Use st.write() to ensure the column names are displayed

            # Add a button to download the search results as CSV
            st.markdown(get_csv_download_link(df), unsafe_allow_html=True)

# Function to generate a download link for CSV file

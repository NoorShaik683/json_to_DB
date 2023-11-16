import streamlit as st
import requests
import pandas as pd
import base64
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


api_endpoint = os.environ.get('API_ENDPOINT')
                              
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
def search_and_filter(table_name, selected_column, search_condition, search_value):
    response = requests.get(
        f'{api_endpoint}/api/v1/filter_advanced?table_name={table_name}&column={selected_column}&condition={search_condition}&value={search_value}', 
        headers={"Authorization": 'admin_123'}
    )
    search_results = response.json()
    return search_results

# Function to generate a download link for CSV file
def get_csv_download_link(df):
    csv_file = df.to_csv(index=False)
    b64 = base64.b64encode(csv_file.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="search_results.csv">Download CSV File</a>'


# Streamlit app
st.set_page_config(
    page_title="JSON-to-DB",
    page_icon="👋",
)

st.title("Report Generation")

# Dropdown for table names with search option
table_names = get_table_names()
selected_table = st.selectbox("Select a Table", table_names, key="table_names")

# Get columns based on the selected table
if selected_table:
    columns = get_table_columns(selected_table)
    selected_column = st.selectbox("Select a Column", columns, key="columns")
    search_condition = st.selectbox("Select a Condition", ["Equal to", "Greater than", "Less than", "Greater than or Equal to","Less than or Equal to","Not Equal to"], key="conditions")
    search_value = st.text_input("Enter the search value")

    if st.button("Search and Filter"):
        # Call the search_and_filter function
        search_results = search_and_filter(selected_table, selected_column, search_condition, search_value)

        # Display search results in a table
        # st.write(search_results)
        if not search_results:
            st.info("No matching records found.")
        elif not type(search_results) is list and search_results.get('error'):
            st.error(search_results.get('error'))
        else:
            # Convert the search results to a DataFrame for better display
            df = pd.DataFrame(search_results, columns=columns)
            df.index+=1
            st.dataframe(df)
            # st.write(df)  # Use st.write() to ensure the column names are displayed

            # Add a button to download the search results as CSV
            st.markdown(get_csv_download_link(df), unsafe_allow_html=True)


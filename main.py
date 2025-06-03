import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
import pandas as pd
import os

# Authenticate and connect to Google Sheets
def connect_to_gsheet(creds_json, spreadsheet_name, sheet_name):
    try:
        if not os.path.exists(creds_json):
            raise FileNotFoundError(f"Credentials file not found: {creds_json}")
        
        scope = ["https://spreadsheets.google.com/feeds", 
                 'https://www.googleapis.com/auth/spreadsheets',
                 "https://www.googleapis.com/auth/drive.file", 
                 "https://www.googleapis.com/auth/drive"]
        
        credentials = Credentials.from_service_account_file(creds_json, scopes=scope)
        client = gspread.authorize(credentials)
        
        try:
            spreadsheet = client.open(spreadsheet_name)  # Access the spreadsheet
        except gspread.exceptions.APIError as e:
            st.error("Google Drive API is not enabled or permissions are missing. "
                     "Enable the API at https://console.developers.google.com/apis/api/drive.googleapis.com/overview "
                     "and ensure the service account has access to the spreadsheet.")
            raise e
        
        try:
            worksheet = spreadsheet.worksheet(sheet_name)  # Access specific sheet by name
        except gspread.exceptions.WorksheetNotFound:
            raise ValueError(f"Worksheet '{sheet_name}' not found in spreadsheet '{spreadsheet_name}'.")
        
        return worksheet
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {e}")
        raise

# Google Sheet credentials and details
SPREADSHEET_NAME = 'Streamlit'
SHEET_NAME = 'Sheet1'
CREDENTIALS_FILE = './credentials.json'

# Connect to the Google Sheet
sheet_by_name = connect_to_gsheet(CREDENTIALS_FILE, SPREADSHEET_NAME, sheet_name=SHEET_NAME)

st.title("Simple Data Entry using Streamlit")

# Read Data from Google Sheets
def read_data():
    data = sheet_by_name.get_all_records()  # Get all records from Google Sheet
    return pd.DataFrame(data)

# Add Data to Google Sheets
def add_data(row):
    sheet_by_name.append_row(row)  # Append the row to the Google Sheet

# Sidebar form for data entry
with st.sidebar:
    st.header("Enter New Amount given to Mother")
    with st.form(key="data_form"):
        name = st.text_input("Name")
        money = st.number_input("Money", min_value=0, max_value=8000)
        
        date = st.date_input("Date", value=None)  # Use date picker for selecting the date
        comment = st.text_input("Comments")
        submitted = st.form_submit_button("Submit")
        # Handle form submission
        if submitted:
            if name and date:  # Basic validation to check if required fields are filled
                formatted_date = date.strftime('%Y-%m-%d')  # Convert date to string
                add_data([name, money, formatted_date, comment])  # Append the row to the sheet
                st.success("Data added successfully!")
            else:
                st.error("Please fill out the form correctly.")

# Display data in the main view
st.header("Money Given to mother")
df = read_data()
st.dataframe(df, width=800, height=500)
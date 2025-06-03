import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
import pandas as pd
import os
import sys
import subprocess

# Ensure required dependencies are installed
required_packages = ["streamlit", "gspread", "google-auth", "pandas"]
for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Authenticate and connect to Google Sheets
def connect_to_gsheet(spreadsheet_name, sheet_name):
    try:
        # Load credentials from Streamlit secrets
        creds_dict = {
            "type": st.secrets["type"],
            "project_id": st.secrets["project_id"],
            "private_key_id": st.secrets["private_key_id"],
            "private_key": st.secrets["private_key"].replace("\\n", "\n"),
            "client_email": st.secrets["client_email"],
            "client_id": st.secrets["client_id"],
            "auth_uri": st.secrets["auth_uri"],
            "token_uri": st.secrets["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["client_x509_cert_url"]
        }
        
        scope = ["https://spreadsheets.google.com/feeds", 
                 'https://www.googleapis.com/auth/spreadsheets',
                 "https://www.googleapis.com/auth/drive.file", 
                 "https://www.googleapis.com/auth/drive"]
        
        credentials = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(credentials)
        
        try:
            spreadsheet = client.open(spreadsheet_name)  # Access the spreadsheet
        except gspread.exceptions.SpreadsheetNotFound:
            raise ValueError(f"Spreadsheet '{spreadsheet_name}' not found. Check the name.")
        
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

# Connect to the Google Sheet
sheet_by_name = connect_to_gsheet(SPREADSHEET_NAME, sheet_name=SHEET_NAME)

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
        
        date = st.date_input("Date")  # Use date picker for selecting the date
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
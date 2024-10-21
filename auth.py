import streamlit as st
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import os

# Define the client secret file and scopes
CLIENT_SECRET_FILE = 'path_to_your_client_secret_file.json'
SCOPES = ['https://www.googleapis.com/auth/calendar']


def get_calendar_service():
    # Set up the OAuth flow for authentication
    flow = Flow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'

    # Check if the credentials are stored in the session state
    if 'credentials' not in st.session_state:
        # Generate authorization URL and display instructions
        auth_url, _ = flow.authorization_url(prompt='consent')
        st.write("Please follow these steps to authorize the application:")
        st.write("1. Click on the link below to open Google's authorization page.")
        st.write("2. Sign in with your Google account and grant the requested permissions.")
        st.write("3. After granting permissions, you will see a page with a long code.")
        st.write("4. Copy that entire code and paste it in the text box below.")
        st.write(f"[Click here to authorize]({auth_url})")

        # Take the authorization code input
        auth_code = st.text_input("Enter the authorization code:")

        # If the authorization code is provided, fetch the credentials
        if auth_code:
            flow.fetch_token(code=auth_code)
            st.session_state.credentials = flow.credentials
            st.success("Authorization successful! You can now use Google Calendar integration.")

    # Use the credentials from session state
    credentials = st.session_state.credentials

    # Build the Google Calendar service
    return build('calendar', 'v3', credentials=credentials)
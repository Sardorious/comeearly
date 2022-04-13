import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials


def get_sheet():
    scopes = ["https://spreadsheets.google.com/feeds"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        "./credential.json", scopes
    )
    client = gspread.authorize(credentials)
    sheet = client.open_by_key(os.getenv("GOOGLE_SHEET_KEY")).sheet1
    return sheet

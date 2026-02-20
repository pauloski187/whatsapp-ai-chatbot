"""Google Sheets helper functions for lead storage."""

from typing import List

import gspread
from google.oauth2.service_account import Credentials

from config import settings


def _get_client() -> gspread.Client:
    """Build an authenticated gspread client using a service account JSON key."""
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_file(
        settings.GOOGLE_SERVICE_ACCOUNT_JSON,
        scopes=scopes,
    )
    return gspread.authorize(credentials)


def append_row(sheet_id: str, values_list: List[str]) -> None:
    """Append a single row of values to the first worksheet in the target sheet."""
    client = _get_client()
    spreadsheet = client.open_by_key(sheet_id)
    worksheet = spreadsheet.sheet1
    worksheet.append_row(values_list, value_input_option="USER_ENTERED")

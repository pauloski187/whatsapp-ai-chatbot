"""Lead detection and persistence services."""

import re
from datetime import datetime, timezone
from typing import Dict, Optional

from config import settings
from sheets import append_row


class LeadService:
    """Extract potential lead data from user text and store it."""

    EMAIL_REGEX = re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b")
    PHONE_REGEX = re.compile(r"\b(?:\+?\d{1,3})?[-.\s()]?\d{3,4}[-.\s()]?\d{3}[-.\s()]?\d{3,4}\b")
    NAME_REGEX = re.compile(r"\b(?:my name is|i am|i'm)\s+([a-zA-Z][a-zA-Z\s'-]{1,40})\b", re.IGNORECASE)

    def detect_lead_info(self, message: str) -> Optional[Dict[str, str]]:
        """Extract name, email, and phone from a message if any are present."""
        email_match = self.EMAIL_REGEX.search(message)
        phone_match = self.PHONE_REGEX.search(message)
        name_match = self.NAME_REGEX.search(message)

        data: Dict[str, str] = {}
        if name_match:
            data["name"] = name_match.group(1).strip().title()
        if email_match:
            data["email"] = email_match.group(0).strip()
        if phone_match:
            data["phone"] = phone_match.group(0).strip()

        return data or None

    def save_lead(self, platform: str, user_id: str, data_dict: Dict[str, str]) -> None:
        """Save lead data as a row in Google Sheets."""
        timestamp = datetime.now(timezone.utc).isoformat()
        values = [
            timestamp,
            platform,
            user_id,
            data_dict.get("name", ""),
            data_dict.get("email", ""),
            data_dict.get("phone", ""),
        ]
        append_row(settings.GOOGLE_SHEET_ID, values)


lead_service = LeadService()

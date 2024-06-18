import datetime
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class GoogleCalendarAPI:
    SCOPES = ["https://www.googleapis.com/auth/calendar.readonly", "https://www.googleapis.com/auth/calendar"]

    def __init__(self, credentials_file="credentials.json", token_file="token.json"):
        self.credentials_file = credentials_file
        self.token_file = token_file

    def authenticate(self):
        """Authenticates the user and generates or loads credentials."""
        creds = None
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, self.SCOPES)
                creds = flow.run_local_server(port=0)
            with open(self.token_file, "w") as token:
                token.write(creds.to_json())
        return creds

    def get_busy_times(self):
        """Gets the busy times on the user's calendar for the next 24 hours."""
        creds = self.authenticate()
        service = build("calendar", "v3", credentials=creds)

        now = datetime.datetime.utcnow()
        start_time = now.isoformat() + "Z"  # 'Z' indicates UTC time
        end_time = (now + datetime.timedelta(days=1)).isoformat() + "Z"

        body = {
            "timeMin": start_time,
            "timeMax": end_time,
            "items": [{"id": "primary"}]
        }

        try:
            events_result = service.freebusy().query(body=body).execute()
            calendars = events_result.get("calendars", {})
            for calendar_id, info in calendars.items():
                busy_times = info.get("busy", [])
                if not busy_times:
                    print(f"No busy times found for calendar {calendar_id}.")
                else:
                    print(f"Busy times for calendar {calendar_id}:")
                    for busy_time in busy_times:
                        print(f" - Start: {busy_time['start']}, End: {busy_time['end']}")
        except HttpError as error:
            print(f"An error occurred: {error}")

if __name__ == "__main__":
    calendar_api = GoogleCalendarAPI()
    calendar_api.get_busy_times()
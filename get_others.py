import datetime
import os
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class GoogleCalendarAPI:
    def __init__(self, calendar_id, token_path="token.json"):
        self.calendar_id = calendar_id
        self.token_path = token_path
        self.scopes = ["https://www.googleapis.com/auth/calendar.readonly"]
        self.creds = self._get_credentials()

    def _get_credentials(self):
        creds = None
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.scopes)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials/credentials.json", self.scopes
                )
                creds = flow.run_local_server(port=0)
            with open(self.token_path, "w") as token:
                token.write(creds.to_json())
        return creds

    def get_next_events(self, max_results=10):
        try:
            service = build("calendar", "v3", credentials=self.creds)
            now = datetime.datetime.utcnow().isoformat() + "Z"
            events_result = service.events().list(
                calendarId=self.calendar_id,
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            ).execute()
            events = events_result.get("items", [])
            if not events:
                print("Nenhum evento futuro encontrado.")
                return []
            return events
        except HttpError as error:
            print(f"Ocorreu um erro: {error}")
            return []

if __name__ == "__main__":
    load_dotenv()
    calendar_id = 'youremail@gmail.com'
    api = GoogleCalendarAPI(calendar_id)
    next_events = api.get_next_events()
    for event in next_events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        print(start, event["summary"])

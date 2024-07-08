import datetime
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.exceptions import RefreshError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import base64

class GoogleCalendarAPI:
    SCOPES = ["https://www.googleapis.com/auth/calendar.readonly", 
              "https://www.googleapis.com/auth/calendar",
              "https://www.googleapis.com/auth/gmail.send"]

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
                try:
                    creds.refresh(Request())
                except RefreshError as e:
                    print(f"Error refreshing credentials: {e}")
                    return None
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, self.SCOPES)
                creds = flow.run_local_server(port=0)
            with open(self.token_file, "w") as token:
                token.write(creds.to_json())
        return creds

    def get_busy_times(self):
        """Gets the busy times on the user's calendar for the next 24 hours."""
        creds = self.authenticate()
        if not creds:
            print("Failed to authenticate.")
            return
        
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

    def create_event(self, email, summary, description, start_datetime, end_datetime):
        """Creates an event on the user's calendar and sends an invite via email."""
        creds = self.authenticate()
        if not creds:
            print("Failed to authenticate.")
            return

        service = build("calendar", "v3", credentials=creds)

        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': 'UTC',
            },
            'attendees': [
                {'email': email},
            ],
        }

        try:
            event = service.events().insert(calendarId='primary', body=event).execute()
            print(f"Event created: {event.get('htmlLink')}")
            self.send_event_invite(email, summary, description, start_datetime, end_datetime)
        except HttpError as error:
            print(f"An error occurred: {error}")

    def send_event_invite(self, email, summary, description, start_datetime, end_datetime):
        """Sends an event invitation to the specified email via Gmail."""
        creds = self.authenticate()
        if not creds:
            print("Failed to authenticate.")
            return

        service = build("gmail", "v1", credentials=creds)

        message = self.create_message(email, summary, description, start_datetime, end_datetime)
        
        try:
            message = service.users().messages().send(userId="me", body=message).execute()
            print(f"Invite sent. Message ID: {message['id']}")
        except HttpError as error:
            print(f"An error occurred: {error}")

    def create_message(self, email, summary, description, start_datetime, end_datetime):
        """Creates a message for sending event invite via Gmail."""
        message = MIMEMultipart('alternative')
        message['to'] = email
        message['subject'] = f"Invite: {summary}"
        
        html = f"<p>You are invited to '{summary}'.</p>"
        text = f"You are invited to '{summary}'."

        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

        message.attach(part1)
        message.attach(part2)

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return {'raw': raw}

if __name__ == "__main__":
    calendar_api = GoogleCalendarAPI()
    calendar_api.get_busy_times()  # Optional: Print busy times

    # Example usage of sending event invite
    email = "email convidado"
    summary = "Meeting"
    description = "Discuss project details"
    start_datetime = datetime.datetime(2024, 7, 10, 10, 0, 0)  # Year, Month, Day, Hour, Minute, Second
    end_datetime = datetime.datetime(2024, 7, 10, 11, 0, 0)    # Year, Month, Day, Hour, Minute, Second
    
    calendar_api.create_event(email, summary, description, start_datetime, end_datetime)

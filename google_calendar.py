import datetime
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly", "https://www.googleapis.com/auth/calendar"]

def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)

        # Define the time period to check availability
        now = datetime.datetime.utcnow()
        start_time = now.isoformat() + "Z"  # 'Z' indicates UTC time
        end_time = (now + datetime.timedelta(days=1)).isoformat() + "Z"

        # Make a FreeBusy request
        body = {
            "timeMin": start_time,
            "timeMax": end_time,
            "items": [{"id": "primary"}]
        }

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
    main()
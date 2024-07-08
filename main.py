import time
import schedule
import pandas as pd
from supabase import create_client, Client
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload

# Configurações do Supabase
supabase_url = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlsZHVtYmFmeHd6dWtkcG1qdHZpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTk5NTU2OTEsImV4cCI6MjAzNTUzMTY5MX0.FhdrVt3TqJb79TXyIhRiXi3BYklkIhYXbehFwI52j-o'
supabase_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlsZHVtYmFmeHd6dWtkcG1qdHZpIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcxOTk1NTY5MSwiZXhwIjoyMDM1NTMxNjkxfQ.Zei1zrRDC93Hea3Ea95ZO6czvitspOXS13MktQm_cxg'

# Configurações do Google
SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_authorized_user_file('./credentials.json', SCOPES)
calendar_service = build('calendar', 'v3', credentials=creds)
drive_service = build('drive', 'v3', credentials=creds)

# Função para conectar ao Supabase e obter dados dos produtos
def get_product_data():
    supabase: Client = create_client(supabase_url, supabase_key)
    response = supabase.table('products').select('*').execute()
    return response.data

# Função para atualizar os dados dos produtos a cada 5 minutos
def update_product_data():
    product_data = get_product_data()
    generate_csv(product_data)
    print("Dados dos produtos atualizados.")
    
schedule.every(5).minutes.do(update_product_data)

# Função para criar um evento no Google Calendar
def create_event(summary, description, start_time, end_time):
    event = {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': start_time,
            'timeZone': 'America/Sao_Paulo',
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'America/Sao_Paulo',
        },
    }
    event = calendar_service.events().insert(calendarId='primary', body=event).execute()
    print('Evento criado: %s' % (event.get('htmlLink')))
    return event['id']

# Função para criar uma pasta no Google Drive
def create_folder(folder_name):
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    folder = drive_service.files().create(body=file_metadata, fields='id').execute()
    print('ID da pasta: %s' % folder.get('id'))
    return folder.get('id')

# Função para fazer upload de arquivos para o Google Drive
def upload_file(file_name, folder_id):
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_name, mimetype='application/octet-stream')
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print('ID do arquivo: %s' % file.get('id'))
    return file.get('id')

# Função para gerar e atualizar o arquivo CSV dos produtos
def generate_csv(product_data):
    df = pd.DataFrame(product_data)
    df.to_csv('products.csv', index=False)

# Função para convidar um email para o evento
def invite_attendee(event_id, attendee_email):
    event = calendar_service.events().get(calendarId='primary', eventId=event_id).execute()
    if 'attendees' not in event:
        event['attendees'] = []
    event['attendees'].append({'email': attendee_email})
    updated_event = calendar_service.events().update(calendarId='primary', eventId=event['id'], body=event).execute()
    print('Convidado adicionado: %s' % updated_event.get('htmlLink'))

# Loop principal para manter o agendamento em execução
while True:
    schedule.run_pending()
    time.sleep(1)
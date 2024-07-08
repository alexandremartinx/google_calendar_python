# google_calendar_python

# Projeto 1: próximos 10 eventos

Google Calendar API
Este projeto implementa uma classe Python para interagir com a API do Google Calendar. Ele permite autenticar um usuário e recuperar os próximos eventos de um calendário específico.

Pré-requisitos
Python 3.6 ou superior
Bibliotecas Python: google-auth, google-auth-oauthlib, google-auth-httplib2, google-api-python-client, python-dotenv
Arquivos de credenciais do Google OAuth 2.0: credentials.json
Arquivo de variáveis de ambiente .env contendo o ID do calendário
Instalação

python -m venv venv
source venv/bin/activate  # No Windows use `venv\Scripts\activate`
Instale as dependências:

pip install -r requirements.txt
Coloque o arquivo credentials.json no diretório credentials/.

Uso
Carregue as variáveis de ambiente e execute o script google_calendar.py:

python main.py
O script exibirá os próximos eventos do calendário especificado.


# Projeto 2: Eventos em 24 horas

Google Calendar API
Este projeto implementa uma classe Python para interagir com a API do Google Calendar. Ele permite autenticar um usuário e recuperar os horários ocupados no calendário do usuário para as próximas 24 horas.

Pré-requisitos
Python 3.6 ou superior
Bibliotecas Python: google-auth, google-auth-oauthlib, google-auth-httplib2, google-api-python-client
Arquivos de credenciais do Google OAuth 2.0: credentials.json
Instalação:

Crie e ative um ambiente virtual (opcional, mas recomendado):`

Instale as dependências:
pip install -r requirements.txt
Coloque o arquivo credentials.json no diretório do projeto.

Uso
Execute o script get_others.py
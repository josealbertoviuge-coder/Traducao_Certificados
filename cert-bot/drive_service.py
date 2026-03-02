import os
import json
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive']

def conectar_drive():

    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:

        flow = Flow.from_client_config(
            json.loads(os.environ["GOOGLE_CREDENTIALS"]),
            scopes=SCOPES,
            redirect_uri="http://localhost"
        )

        auth_url, _ = flow.authorization_url(prompt='consent')

        print("\n👉 Abra este link:")
        print(auth_url)

        code = input("\n👉 Cole o código retornado: ")

        flow.fetch_token(code=code)
        creds = flow.credentials

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build('drive', 'v3', credentials=creds)

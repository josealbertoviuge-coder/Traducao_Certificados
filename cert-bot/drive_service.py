import os
import json
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive']

def conectar_drive():

    if "GOOGLE_AUTH_CODE" not in os.environ:
        raise Exception("Variável GOOGLE_AUTH_CODE não definida")

    flow = Flow.from_client_config(
        json.loads(os.environ["GOOGLE_CREDENTIALS"]),
        scopes=SCOPES,
        redirect_uri="http://localhost"
    )

    flow.fetch_token(code=os.environ["GOOGLE_AUTH_CODE"])

    creds = flow.credentials

    return build('drive', 'v3', credentials=creds)

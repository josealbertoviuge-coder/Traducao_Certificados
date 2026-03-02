import os
import json
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials

def conectar_drive():
    gauth = GoogleAuth()

    scope = ['https://www.googleapis.com/auth/drive']
    creds_json = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])

    gauth.credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        creds_json, scope
    )

    return GoogleDrive(gauth)

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials

def conectar_drive():
    gauth = GoogleAuth()

    scope = ['https://www.googleapis.com/auth/drive']
    gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(
        'service_account.json', scope
    )

    return GoogleDrive(gauth)

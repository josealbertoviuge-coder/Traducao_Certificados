from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

def conectar_drive():
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    return GoogleDrive(gauth)

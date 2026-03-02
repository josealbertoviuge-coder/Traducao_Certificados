from drive_service import conectar_drive
from processor import processar
import time

def executar():
    print("Verificando novos certificados...")
    drive = conectar_drive()
    processar(drive)
    print("Aguardando próxima verificação...\n")

while True:
    executar()
    time.sleep(30)  # 30 s

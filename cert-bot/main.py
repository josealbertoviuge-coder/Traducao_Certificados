from drive_service import conectar_drive
from processor import processar

def main():
    drive = conectar_drive()
    processar(drive)

if __name__ == "__main__":
    main()

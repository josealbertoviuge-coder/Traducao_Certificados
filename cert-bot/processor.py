from config import ID_ENTRADA, ID_TRADUZIDOS, ID_PROCESSADOS
from pdf_utils import extrair_texto, gerar_pdf
from translator import traduzir

from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
import io


# =========================
# LISTAR ARQUIVOS NA PASTA
# =========================
def listar_arquivos(drive):
    results = drive.files().list(
        q=f"'{ID_ENTRADA}' in parents and trashed=false",
        fields="files(id, name)"
    ).execute()

    return results.get("files", [])


# =========================
# BAIXAR ARQUIVO DO DRIVE
# =========================
def baixar_arquivo(drive, file_id, nome):
    request = drive.files().get_media(fileId=file_id)

    fh = io.FileIO(nome, 'wb')
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        _, done = downloader.next_chunk()

    return nome


# =========================
# ENVIAR ARQUIVO TRADUZIDO
# =========================
def enviar_traduzido(drive, pasta_id, caminho_arquivo):

    file_metadata = {
        'name': caminho_arquivo,
        'parents': [pasta_id]
    }

    media = MediaFileUpload(caminho_arquivo, resumable=True)

    drive.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()


# =========================
# MOVER ARQUIVO PARA PROCESSADOS
# =========================
def mover_para_processados(drive, file_id):

    drive.files().update(
        fileId=file_id,
        addParents=ID_PROCESSADOS,
        removeParents=ID_ENTRADA,
        fields='id, parents'
    ).execute()


# =========================
# PROCESSAMENTO PRINCIPAL
# =========================
def processar(drive):

    arquivos = listar_arquivos(drive)

    if not arquivos:
        print("Nenhum arquivo novo.")
        return

    for arquivo in arquivos:
        print("Processando:", arquivo['name'])

        # baixar
        caminho = baixar_arquivo(drive, arquivo['id'], arquivo['name'])

        # extrair texto
        texto = extrair_texto(caminho)

        # traduzir
        texto_traduzido = traduzir(texto)

        # gerar PDF traduzido
        nome_saida = "EN_" + arquivo['name']
        gerar_pdf(texto_traduzido, nome_saida)

        # enviar arquivo traduzido
        enviar_traduzido(drive, ID_TRADUZIDOS, nome_saida)

        # mover original para processados
        mover_para_processados(drive, arquivo['id'])

        print("✔ Concluído:", arquivo['name'])

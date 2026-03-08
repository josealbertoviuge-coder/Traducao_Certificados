import os
import io
from datetime import datetime

from config import ID_ENTRADA, ID_TRADUZIDOS, ID_PROCESSADOS

from pdf_utils import (
    extrair_texto,
    precisa_ocr,
    limpar_assinatura,
    ocr_pdf
)

from docx_utils import (
    pdf_para_docx,
    traduzir_docx,
    criar_docx_ocr
)

from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload


# =========================
# LISTAR ARQUIVOS NA PASTA
# =========================
def listar_arquivos(drive):

    results = drive.files().list(
        q=f"'{ID_ENTRADA}' in parents and trashed=false",
        fields="files(id, name)",
        supportsAllDrives=True,
        includeItemsFromAllDrives=True
    ).execute()

    print("RETORNO DRIVE:", results)

    return results.get("files", [])


# =========================
# BAIXAR ARQUIVO DO DRIVE
# =========================
def baixar_arquivo(drive, file_id, nome):

    request = drive.files().get_media(fileId=file_id)

    fh = io.FileIO(nome, "wb")

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
        "name": caminho_arquivo,
        "parents": [pasta_id]
    }

    media = MediaFileUpload(caminho_arquivo, resumable=True)

    drive.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()


# =========================
# MOVER ARQUIVO PARA PROCESSADOS
# =========================
def mover_para_processados(drive, file_id):

    drive.files().update(
        fileId=file_id,
        addParents=ID_PROCESSADOS,
        removeParents=ID_ENTRADA,
        fields="id, parents"
    ).execute()


# =========================
# REGISTRO DE LOG
# =========================
def registrar_log(nome):

    with open("log.txt", "a") as log:
        log.write(f"{nome} processado em {datetime.now()}\n")


# =========================
# PROCESSAMENTO PRINCIPAL
# =========================
def processar(drive):

    arquivos = listar_arquivos(drive)

    if not arquivos:
        print("Nenhum arquivo novo.")
        return

    for arquivo in arquivos:

        print("Processando:", arquivo["name"])

        try:

            # =========================
            # BAIXAR PDF
            # =========================
            caminho = baixar_arquivo(
                drive,
                arquivo["id"],
                arquivo["name"]
            )

            # =========================
            # LIMPAR ASSINATURAS
            # =========================
            limpar_assinatura(caminho, caminho)

            # =========================
            # DETECTAR TEXTO
            # =========================
            texto = extrair_texto(caminho)

            # =================================================
            # PIPELINE PARA PDF ESCANEADO
            # =================================================
            if precisa_ocr(texto):

                print("⚠ PDF escaneado detectado — usando OCR")

                texto_ocr = ocr_pdf(caminho)

                if not texto_ocr.strip():
                    raise Exception("OCR não conseguiu extrair texto")

                docx_traduzido = "EN_" + arquivo["name"].replace(".pdf", ".docx")

                print("✔ Criando DOCX a partir do OCR")

                criar_docx_ocr(
                    texto_ocr,
                    docx_traduzido
                )

                nome_saida = docx_traduzido

            # =================================================
            # PIPELINE PARA PDF DIGITAL
            # =================================================
            else:

                print("✔ PDF digital detectado")

                print("✔ Convertendo PDF para DOCX")

                docx_original = arquivo["name"].replace(".pdf", ".docx")

                pdf_para_docx(
                    caminho,
                    docx_original
                )

                print("✔ Traduzindo DOCX")

                docx_traduzido = "EN_" + docx_original

                traduzir_docx(
                    docx_original,
                    docx_traduzido
                )

                nome_saida = docx_traduzido

            # =========================
            # ENVIAR RESULTADO
            # =========================
            enviar_traduzido(
                drive,
                ID_TRADUZIDOS,
                nome_saida
            )

            # =========================
            # MOVER ORIGINAL
            # =========================
            mover_para_processados(
                drive,
                arquivo["id"]
            )

            # =========================
            # LOG
            # =========================
            registrar_log(arquivo["name"])

            print("✔ Concluído:", arquivo["name"])

        except Exception as e:

            print(f"Erro ao processar {arquivo['name']}: {e}")

import os
import io
from datetime import datetime

from config import ID_ENTRADA, ID_TRADUZIDOS, ID_PROCESSADOS

from pdf_utils import (
    extrair_texto,
    extrair_paginas,
    precisa_ocr,
    limpar_assinatura,
    ocr_pdf
)

from docx_utils import (
    criar_docx_paginas,
    criar_docx_ocr
)

from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload


def listar_arquivos(drive):

    results = drive.files().list(
        q=f"'{ID_ENTRADA}' in parents and trashed=false",
        fields="files(id, name)",
        supportsAllDrives=True,
        includeItemsFromAllDrives=True
    ).execute()

    print("RETORNO DRIVE:", results)

    return results.get("files", [])


def baixar_arquivo(drive, file_id, nome):

    request = drive.files().get_media(fileId=file_id)

    fh = io.FileIO(nome, "wb")

    downloader = MediaIoBaseDownload(fh, request)

    done = False

    while not done:
        _, done = downloader.next_chunk()

    return nome


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


def mover_para_processados(drive, file_id):

    drive.files().update(
        fileId=file_id,
        addParents=ID_PROCESSADOS,
        removeParents=ID_ENTRADA,
        fields="id, parents"
    ).execute()


def registrar_log(nome):

    with open("log.txt", "a") as log:
        log.write(f"{nome} processado em {datetime.now()}\n")


def processar(drive):

    arquivos = listar_arquivos(drive)

    if not arquivos:
        print("Nenhum arquivo novo.")
        return

    for arquivo in arquivos:

        print("Processando:", arquivo["name"])

        try:

            caminho = baixar_arquivo(
                drive,
                arquivo["id"],
                arquivo["name"]
            )

            limpar_assinatura(caminho, caminho)

            texto = extrair_texto(caminho)

            if precisa_ocr(texto):

                print("⚠ PDF escaneado detectado — usando OCR")

                texto_ocr = ocr_pdf(caminho)

                docx_traduzido = "EN_" + arquivo["name"].replace(".pdf", ".docx")

                criar_docx_ocr(
                    texto_ocr,
                    docx_traduzido
                )

                nome_saida = docx_traduzido

            else:

                print("✔ PDF digital detectado")

                paginas = extrair_paginas(caminho)

                docx_traduzido = "EN_" + arquivo["name"].replace(".pdf", ".docx")

                criar_docx_paginas(
                    paginas,
                    docx_traduzido
                )

                nome_saida = docx_traduzido

            enviar_traduzido(
                drive,
                ID_TRADUZIDOS,
                nome_saida
            )

            mover_para_processados(
                drive,
                arquivo["id"]
            )

            registrar_log(arquivo["name"])

            print("✔ Concluído:", arquivo["name"])

        except Exception as e:

            print(f"Erro ao processar {arquivo['name']}: {e}")

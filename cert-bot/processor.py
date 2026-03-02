from pdf_utils import gerar_pdf_bilingue
from pdf_utils import ocr_pdf
from config import ID_ENTRADA, ID_TRADUZIDOS, ID_PROCESSADOS

from pdf_utils import (
    extrair_texto,
    gerar_pdf,
    extrair_blocos,
    gerar_pdf_layout,
    precisa_ocr,
    limpar_assinatura
)

from translator import traduzir

from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
import io
from datetime import datetime
import os


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
        print("Processando:", arquivo['name'])

        try:
            # baixar arquivo
            caminho = baixar_arquivo(drive, arquivo['id'], arquivo['name'])

            # limpar assinaturas e carimbos
            limpar_assinatura(caminho, caminho)

            # extrair texto
            texto = extrair_texto(caminho)

            # detectar PDF escaneado
            if precisa_ocr(texto):
                print("⚠ PDF escaneado detectado — usando OCR")
                texto = ocr_pdf(caminho)

            # traduzir conteúdo
            texto_traduzido = traduzir(texto)

            nome_saida = "EN_" + arquivo['name']

            # ===== tentativa de preservar layout =====
            blocos = extrair_blocos(caminho)

            if blocos:
                print("✔ Layout preservado")
                gerar_pdf_layout(blocos, texto_traduzido, nome_saida)

                # fallback se layout gerar PDF vazio
                if os.path.getsize(nome_saida) < 2000:
                    print("Layout vazio — usando modo simples")
                    gerar_pdf(texto_traduzido, nome_saida)
            else:
                print("PDF escaneado → gerando versão bilíngue")
                from pdf_utils import gerar_pdf_tabelado

                print("Gerando PDF com tabelas estruturadas")
                gerar_pdf_tabelado(texto_traduzido, nome_saida)

            # enviar traduzido
            enviar_traduzido(drive, ID_TRADUZIDOS, nome_saida)

            # mover original
            mover_para_processados(drive, arquivo['id'])

            # registrar log
            registrar_log(arquivo['name'])

            print("✔ Concluído:", arquivo['name'])

        except Exception as e:
            print(f"Erro ao processar {arquivo['name']}: {e}")

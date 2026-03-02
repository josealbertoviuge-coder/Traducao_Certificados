from config import ID_ENTRADA, ID_TRADUZIDOS, ID_PROCESSADOS
from pdf_utils import extrair_texto
from translator import traduzir
from pdf_utils import gerar_pdf

def listar_arquivos(drive):
    return drive.ListFile(
        {'q': f"'{ID_ENTRADA}' in parents and trashed=false"}
    ).GetList()

def baixar_arquivo(file):
    file.GetContentFile(file['title'])
    return file['title']

def enviar_traduzido(drive, pasta_id, caminho_arquivo):
    file = drive.CreateFile({'parents': [{'id': pasta_id}]})
    file.SetContentFile(caminho_arquivo)
    file.Upload()

def mover_para_processados(file):
    file['parents'] = [{'id': ID_PROCESSADOS}]
    file.Upload()

def processar(drive):
    arquivos = listar_arquivos(drive)

    for arquivo in arquivos:
        print("Processando:", arquivo['title'])

        caminho = baixar_arquivo(arquivo)

        texto = extrair_texto(caminho)

        texto_traduzido = traduzir(texto)

        nome_saida = "EN_" + arquivo['title']
        gerar_pdf(texto_traduzido, nome_saida)

        enviar_traduzido(drive, ID_TRADUZIDOS, nome_saida)

        mover_para_processados(arquivo)

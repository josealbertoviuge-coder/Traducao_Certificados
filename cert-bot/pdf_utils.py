import fitz
from reportlab.pdfgen import canvas
import pdfplumber

def extrair_texto(pdf):
    doc = fitz.open(pdf)
    texto = ""
    for page in doc:
        texto += page.get_text()
    return texto

def gerar_pdf(texto, nome):
    c = canvas.Canvas(nome)
    y = 800
    for linha in texto.split("\n"):
        c.drawString(40, y, linha)
        y -= 15
    c.save()

def extrair_blocos(pdf):
    blocos = []

    with pdfplumber.open(pdf) as pdf_file:
        for page in pdf_file.pages:
            words = page.extract_words()
            blocos.extend(words)

    return blocos

import fitz
from reportlab.pdfgen import canvas

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

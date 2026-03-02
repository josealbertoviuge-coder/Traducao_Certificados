import fitz
import pdfplumber
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from openai import OpenAI
from pdf2image import convert_from_path
import base64
import io
import os

client = OpenAI()

# =========================================================
# EXTRAIR TEXTO
# =========================================================
def extrair_texto(pdf):
    doc = fitz.open(pdf)
    texto = ""
    for page in doc:
        texto += page.get_text()
    return texto.strip()


# =========================================================
# DETECTAR OCR NECESSÁRIO
# =========================================================
def precisa_ocr(texto):
    return len(texto.strip()) < 30


# =========================================================
# LIMPAR ASSINATURA
# =========================================================
def limpar_assinatura(pdf_entrada, pdf_saida=None):
    if pdf_saida is None:
        pdf_saida = pdf_entrada

    temp = pdf_entrada + "_clean.pdf"
    doc = fitz.open(pdf_entrada)

    for page in doc:
        h = page.rect.height
        area = fitz.Rect(0, h-120, page.rect.width, h)
        page.draw_rect(area, fill=(1,1,1))

    doc.save(temp)
    doc.close()
    os.replace(temp, pdf_saida)


# =========================================================
# EXTRAIR BLOCOS (PDF DIGITAL)
# =========================================================
def extrair_blocos(pdf):
    blocos = []
    with pdfplumber.open(pdf) as pdf_file:
        for page in pdf_file.pages:
            words = page.extract_words()
            for w in words:
                blocos.append({
                    "text": w["text"],
                    "x": w["x0"],
                    "y": w["top"]
                })
    return blocos


# =========================================================
# GERAR PDF COM LAYOUT PRESERVADO
# =========================================================
def gerar_pdf_layout(blocos, texto_traduzido, nome):
    largura, altura = A4
    c = canvas.Canvas(nome, pagesize=A4)

    linhas = texto_traduzido.split("\n")

    for bloco, linha in zip(blocos, linhas):
        x = bloco["x"]
        y = altura - bloco["y"]
        if 20 < y < altura-20:
            c.drawString(x, y, linha)

    c.save()


# =========================================================
# OCR VIA OPENAI (PDF ESCANEADO)
# =========================================================
def ocr_pdf(pdf_path):
    imagens = convert_from_path(pdf_path)
    texto = ""

    for img in imagens:
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        encoded = base64.b64encode(buf.getvalue()).decode()

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[{
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "Extract all text from this document."},
                    {"type": "input_image", "image_url": f"data:image/png;base64,{encoded}"}
                ]
            }]
        )

        texto += response.output_text + "\n"

    return texto


# =========================================================
# SOBREPOR TRADUÇÃO NO LAYOUT ORIGINAL
# =========================================================
def gerar_pdf_sobreposto(pdf_original, nome_saida, traduzir_func):

    paginas = convert_from_path(pdf_original)

    largura, altura = A4
    c = canvas.Canvas(nome_saida, pagesize=A4)

    for pagina in paginas:

        buffer = io.BytesIO()
        pagina.save(buffer, format="PNG")
        buffer.seek(0)

        img = ImageReader(buffer)
        c.drawImage(img, 0, 0, width=largura, height=altura)

        # OCR da página inteira
        buf = io.BytesIO()
        pagina.save(buf, format="PNG")
        encoded = base64.b64encode(buf.getvalue()).decode()

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[{
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "Translate the text in this page to English."},
                    {"type": "input_image", "image_url": f"data:image/png;base64,{encoded}"}
                ]
            }]
        )

        traducao = response.output_text

        textobject = c.beginText(40, altura-40)
        textobject.setFont("Helvetica", 8)

        for line in traducao.split("\n"):
            textobject.textLine(line)

        c.drawText(textobject)
        c.showPage()

    c.save()

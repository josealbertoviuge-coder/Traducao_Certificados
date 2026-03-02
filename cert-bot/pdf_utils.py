import fitz  # PyMuPDF
import pdfplumber
from reportlab.pdfgen import canvas


# =========================================================
# EXTRAIR TEXTO PADRÃO (PDF COM TEXTO)
# =========================================================
def extrair_texto(pdf):
    doc = fitz.open(pdf)
    texto = ""

    for page in doc:
        texto += page.get_text()

    return texto.strip()


# =========================================================
# VERIFICAR SE O PDF PRECISA OCR
# (texto muito pequeno ou inexistente)
# =========================================================
def precisa_ocr(texto):
    return len(texto.strip()) < 30


# =========================================================
# EXTRAIR BLOCOS COM POSIÇÃO (PARA PRESERVAR LAYOUT)
# =========================================================
def extrair_blocos(pdf):
    blocos = []

    with pdfplumber.open(pdf) as pdf_file:
        for page in pdf_file.pages:
            palavras = page.extract_words()

            for p in palavras:
                blocos.append({
                    "texto": p["text"],
                    "x": p["x0"],
                    "y": p["top"]
                })

    return blocos


# =========================================================
# REMOVER ASSINATURAS / CARIMBOS (ÁREA INFERIOR)
# =========================================================
def limpar_assinatura(pdf_entrada, pdf_saida=None):

    if pdf_saida is None:
        pdf_saida = pdf_entrada

    temp_saida = pdf_entrada + "_clean.pdf"

    doc = fitz.open(pdf_entrada)

    for page in doc:
        altura = page.rect.height

        area_assinatura = fitz.Rect(
            0,
            altura - 120,
            page.rect.width,
            altura
        )

        page.add_redact_annot(area_assinatura)
        page.apply_redactions()

    doc.save(temp_saida)
    doc.close()

    # substitui o original
    import os
    os.replace(temp_saida, pdf_saida)


# =========================================================
# GERAR PDF SIMPLES (TEXTO CORRIDO)
# =========================================================
def gerar_pdf(texto, nome):

    c = canvas.Canvas(nome)
    y = 800

    for linha in texto.split("\n"):
        c.drawString(40, y, linha)
        y -= 15

        if y < 40:  # nova página automática
            c.showPage()
            y = 800

    c.save()


# =========================================================
# GERAR PDF PRESERVANDO LAYOUT
# =========================================================
def gerar_pdf_layout(blocos, texto_traduzido, nome):

    c = canvas.Canvas(nome)

    linhas = texto_traduzido.split("\n")

    for bloco, linha in zip(blocos, linhas):
        x = bloco["x"]
        y = 800 - bloco["y"]

        c.drawString(x, y, linha)

    c.save()

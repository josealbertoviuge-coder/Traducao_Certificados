import fitz  # PyMuPDF
import pdfplumber
from reportlab.pdfgen import canvas
from openai import OpenAI
from pdf2image import convert_from_path
import base64
import io


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

    import fitz

    temp_saida = pdf_entrada + "_clean.pdf"

    doc = fitz.open(pdf_entrada)

    for page in doc:
        altura = page.rect.height

        # área inferior (assinaturas/carimbos)
        area = fitz.Rect(
            0,
            altura - 120,
            page.rect.width,
            altura
        )

        # desenha retângulo branco (sem apagar conteúdo interno)
        page.draw_rect(area, color=(1, 1, 1), fill=(1, 1, 1))

    doc.save(temp_saida)
    doc.close()

    import os
    os.replace(temp_saida, pdf_saida)

# =========================================================
# GERAR PDF SIMPLES (TEXTO CORRIDO)
# =========================================================
def gerar_pdf(texto, nome):

    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4

    largura, altura = A4
    c = canvas.Canvas(nome, pagesize=A4)

    y = altura - 40

    for linha in texto.split("\n"):
        c.drawString(40, y, linha)
        y -= 15

        if y < 40:
            c.showPage()
            y = altura - 40

    c.save()


# =========================================================
# GERAR PDF PRESERVANDO LAYOUT
# =========================================================
def gerar_pdf_layout(blocos, texto_traduzido, nome):

    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4

    largura, altura = A4
    c = canvas.Canvas(nome, pagesize=A4)

    linhas = texto_traduzido.split("\n")

    for bloco, linha in zip(blocos, linhas):

        x = bloco["x"]

        # converter coordenada (origem topo → origem base)
        y = altura - bloco["y"]

        # garantir que o texto fique dentro da página
        if 20 < y < altura - 20:
            c.drawString(x, y, linha)

    c.save()


client = OpenAI()

def ocr_pdf(pdf_path):

    imagens = convert_from_path(pdf_path)

    texto_final = ""

    for img in imagens:

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        encoded = base64.b64encode(buffer.getvalue()).decode()

        data_url = f"data:image/png;base64,{encoded}"

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[{
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "Extract all text from this document."},
                    {
                        "type": "input_image",
                        "image_url": data_url
                    }
                ]
            }]
        )

        texto_final += response.output_text + "\n"

    return texto_final

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from pdf2image import convert_from_path
import io

def gerar_pdf_bilingue(pdf_original, texto_traduzido, nome_saida):

    paginas = convert_from_path(pdf_original)

    largura, altura = A4
    c = canvas.Canvas(nome_saida, pagesize=A4)

    linhas = texto_traduzido.split("\n")
    linha_index = 0

    for pagina in paginas:

        buffer = io.BytesIO()
        pagina.save(buffer, format="PNG")
        buffer.seek(0)

        img = ImageReader(buffer)

        # lado esquerdo → original
        c.drawImage(img, 0, 0, width=largura/2, height=altura)

        # lado direito → tradução
        y = altura - 40

        while y > 40 and linha_index < len(linhas):
            c.drawString(largura/2 + 20, y, linhas[linha_index])
            y -= 14
            linha_index += 1

        c.showPage()

    c.save()

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors


def gerar_pdf_tabelado(texto, nome_saida):

    doc = SimpleDocTemplate(nome_saida)
    styles = getSampleStyleSheet()
    elementos = []

    for bloco in texto.split("\n\n"):

        linhas = [l.strip() for l in bloco.split("\n") if l.strip()]

        # detectar tabela (linhas com |)
        if all("|" in l for l in linhas) and len(linhas) > 1:
            dados = [linha.split("|") for linha in linhas]

            tabela = Table(dados)
            tabela.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('GRID', (0,0), (-1,-1), 0.5, colors.black),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ]))

            elementos.append(tabela)
        else:
            elementos.append(Paragraph(bloco, styles['Normal']))

    doc.build(elementos)

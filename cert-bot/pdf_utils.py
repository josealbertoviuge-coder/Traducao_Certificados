import fitz
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from pdf2image import convert_from_path
from openai import OpenAI
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
# LIMPAR ASSINATURAS / CARIMBOS
# =========================================================
def limpar_assinatura(pdf_entrada, pdf_saida=None):
    if pdf_saida is None:
        pdf_saida = pdf_entrada

    temp = pdf_entrada + "_clean.pdf"
    doc = fitz.open(pdf_entrada)

    for page in doc:
        h = page.rect.height
        area = fitz.Rect(0, h-120, page.rect.width, h)
        page.draw_rect(area, fill=(1, 1, 1))

    doc.save(temp)
    doc.close()
    os.replace(temp, pdf_saida)


# =========================================================
# OCR VIA OPENAI (para PDFs escaneados)
# =========================================================
def ocr_pdf(pdf_path):
    imagens = convert_from_path(pdf_path)
    texto = ""

    for img in imagens:
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        encoded = base64.b64encode(buffer.getvalue()).decode()

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[{
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "Extract all text from this document."},
                    {"type": "input_image",
                     "image_url": f"data:image/png;base64,{encoded}"}
                ]
            }]
        )

        texto += response.output_text + "\n"

    return texto


# =========================================================
# GERAR PDF CORPORATIVO
# ORIGINAL + TRADUÇÃO ORGANIZADA POR PÁGINA
# =========================================================
def gerar_pdf_traducao_por_pagina(pdf_original, nome_saida):

    paginas = convert_from_path(pdf_original)

    styles = getSampleStyleSheet()

    estilo_titulo = ParagraphStyle(
        'titulo',
        parent=styles['Heading2'],
        spaceAfter=10
    )

    estilo_texto = ParagraphStyle(
        'texto',
        parent=styles['Normal'],
        fontSize=9,
        leading=12
    )

    story = []

    for i, pagina in enumerate(paginas, start=1):

        # =========================
        # Página original
        # =========================
        buffer = io.BytesIO()
        pagina.save(buffer, format="PNG")
        buffer.seek(0)

        story.append(Image(buffer, width=16*cm, height=24*cm))
        story.append(PageBreak())

        # =========================
        # OCR + Tradução estruturada
        # =========================
        encoded = base64.b64encode(buffer.getvalue()).decode()

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[{
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": "Translate and organize this page into structured data. Do NOT use markdown tables. Do NOT use | characters. Return structured plain text only."
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/png;base64,{encoded}"
                    }
                ]
            }]
        )

        traducao = response.output_text

        story.append(Paragraph(f"ENGLISH TRANSLATION — PAGE {i}", styles['Heading1']))
        story.append(Spacer(1, 12))

        linhas = traducao.split("\n")
        tabela_temp = []

        for linha in linhas:
            linha = linha.strip()
            if not linha:
                continue

            # detectar títulos técnicos
            if linha.isupper() or linha.endswith(":"):
                if tabela_temp:
                    story.append(_criar_tabela(tabela_temp))
                    tabela_temp = []
                    story.append(Spacer(1, 12))

                story.append(Paragraph(linha, estilo_titulo))
                continue

            # detectar colunas chave: valor
            if ":" in linha and len(linha) < 60:
                chave, valor = linha.split(":", 1)
                tabela_temp.append([chave.strip(), valor.strip()])
            else:
                if tabela_temp:
                    story.append(_criar_tabela(tabela_temp))
                    tabela_temp = []
                    story.append(Spacer(1, 12))

                story.append(Paragraph(linha, estilo_texto))

        if tabela_temp:
            story.append(_criar_tabela(tabela_temp))

        story.append(PageBreak())

    doc = SimpleDocTemplate(nome_saida)
    doc.build(story)


# =========================================================
# FUNÇÃO AUXILIAR PARA TABELAS ALINHADAS
# =========================================================
def _criar_tabela(dados):

    # Detectar se é formato horizontal (Element | C | Mn | ...)
    if len(dados) == 2 and len(dados[0]) > 2:
        cabecalho = dados[0]
        valores = dados[1]

        nova_tabela = [["Element", "Value"]]

        for i in range(1, len(cabecalho)):
            nova_tabela.append([
                cabecalho[i].strip(),
                valores[i].strip()
            ])

        dados = nova_tabela

    tabela = Table(dados, colWidths=[6*cm, 6*cm])

    tabela.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,0), 1, colors.black),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
    ]))

    return tabela

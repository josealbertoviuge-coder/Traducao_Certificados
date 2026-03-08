import fitz
from pdf2image import convert_from_path
from translator import traduzir_pagina
from pdf_utils import ocr_pdf


def traduzir_pdf_overlay(pdf_entrada, pdf_saida):

    doc = fitz.open(pdf_entrada)

    for page_num, page in enumerate(doc):

        blocks = page.get_text("blocks")

        # -------------------------
        # PDF DIGITAL
        # -------------------------
        if blocks:

            print("PDF digital detectado")

            for block in blocks:

                x0, y0, x1, y1, texto, *_ = block

                texto = texto.strip()

                if not texto:
                    continue

                try:
                    traducao = traduzir_pagina(texto)
                except:
                    traducao = texto

                rect = fitz.Rect(x0, y0, x1, y1)

                page.draw_rect(rect, fill=(1, 1, 1))

                page.insert_textbox(
                    rect,
                    traducao,
                    fontsize=8
                )

        # -------------------------
        # PDF ESCANEADO
        # -------------------------
        else:

            print("PDF escaneado detectado — usando OCR")

            texto = ocr_pdf(pdf_entrada)

            traducao = traduzir_pagina(texto)

            rect = fitz.Rect(
                50,
                50,
                page.rect.width - 50,
                page.rect.height - 50
            )

            page.insert_textbox(
                rect,
                traducao,
                fontsize=10
            )

    doc.save(pdf_saida)

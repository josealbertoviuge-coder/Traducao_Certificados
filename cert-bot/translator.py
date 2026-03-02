from openai import OpenAI

client = OpenAI()

# =====================================================
# GLOSSÁRIO TÉCNICO (OPCIONAL — melhora consistência)
# =====================================================
GLOSSARIO = {
    "LIMITE DE ESCOAMENTO": "Yield Strength",
    "RESISTÊNCIA À TRAÇÃO": "Tensile Strength",
    "ALONGAMENTO": "Elongation",
    "DUREZA": "Hardness",
    "TRATAMENTO TÉRMICO": "Heat Treatment",
    "COMPOSIÇÃO QUÍMICA": "Chemical Composition",
    "PROPRIEDADES MECÂNICAS": "Mechanical Properties"
}


# =====================================================
# APLICAR GLOSSÁRIO APÓS TRADUÇÃO
# =====================================================
def aplicar_glossario(texto):
    for pt, en in GLOSSARIO.items():
        texto = texto.replace(pt, en)
    return texto


# =====================================================
# DIVIDIR TEXTOS MUITO GRANDES
# (evita limite de tokens)
# =====================================================
def dividir_texto(texto, tamanho=3500):
    partes = []
    atual = ""

    for linha in texto.split("\n"):
        if len(atual) + len(linha) < tamanho:
            atual += linha + "\n"
        else:
            partes.append(atual)
            atual = linha + "\n"

    if atual:
        partes.append(atual)

    return partes


# =====================================================
# TRADUÇÃO TÉCNICA PRINCIPAL
# =====================================================
def traduzir(texto):

    if not texto.strip():
        return ""

    partes = dividir_texto(texto)

    traducao_final = ""

    for parte in partes:

prompt = f"""
Translate the following material certificate to English.

IMPORTANT:

If the document contains tables such as:
- chemical composition
- mechanical properties
- test results

Return them in structured table format like:

Element | %
C | 0.20
Mn | 1.50

Yield Strength | 355 MPa
Tensile Strength | 510 MPa

RULES:
- preserve technical terminology
- keep standards (ASTM, DIN, ISO)
- keep units exactly
- keep chemical symbols unchanged
- do not translate steel grades
- maintain numeric precision

TEXT:
{parte}
"""

        resposta = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )

        traducao = resposta.output[0].content[0].text

        traducao_final += traducao + "\n"

    traducao_final = aplicar_glossario(traducao_final)

    return traducao_final.strip()

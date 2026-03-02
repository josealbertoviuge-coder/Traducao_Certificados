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
Extract structured data from this material certificate.

Return JSON only.

If present, extract:

- chemical composition
- mechanical properties
- heat treatment
- material specification
- standards

FORMAT:

{{
  "chemical_composition": [
    {{"element": "", "value": ""}}
  ],
  "mechanical_properties": [
    {{"property": "", "value": ""}}
  ],
  "notes": ""
}}

TEXT:
{parte}
"""

        resposta = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )

        traducao = resposta.output_text

        traducao_final += traducao + "\n"

    traducao_final = aplicar_glossario(traducao_final)

    return traducao_final.strip()

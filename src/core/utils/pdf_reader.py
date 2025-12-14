# src/core/utils/pdf_reader.py

from PyPDF2 import PdfReader
import re

def leer_texto_pdf(path_pdf):
    """
    Lee todo el texto de un PDF y lo devuelve como un solo string.
    """
    texto_completo = ""

    reader = PdfReader(path_pdf)

    for pagina in reader.pages:
        texto_pagina = pagina.extract_text()
        if texto_pagina:
            texto_completo += texto_pagina + "\n"

    return texto_completo


def extraer_nombre_paciente(path_pdf):
    """
    Extrae el nombre del paciente desde el PDF.

    Busca el texto que esté entre:
    'Nombre completo' y 'Tipo Documento'

    Retorna:
        - string con el nombre del paciente
        - None si no se encuentra
    """
    texto = leer_texto_pdf(path_pdf)

    if not texto:
        return None

    # Normalizamos espacios para evitar problemas
    texto = re.sub(r'\s+', ' ', texto)

    inicio = "Nombre completo"
    fin = "Tipo Documento"

    if inicio not in texto or fin not in texto:
        return None

    try:
        # Cortamos el texto entre los dos delimitadores
        fragmento = texto.split(inicio, 1)[1]
        fragmento = fragmento.split(fin, 1)[0]

        nombre = fragmento.strip()

        return nombre if nombre else None

    except Exception:
        return None

def extraer_numero_identificacion(path_pdf):
    """
    Extrae el número de identificación desde el PDF de
    'Validación de derechos de afiliados'.

    Busca el número que aparece después de:
    'Número de Identificación'
    """

    texto = leer_texto_pdf(path_pdf)

    if not texto:
        return None

    # Normalizamos espacios y saltos de línea
    texto = re.sub(r'\s+', ' ', texto)

    clave = "Número de Identificación"

    if clave not in texto:
        return None

    try:
        # Tomamos lo que viene después del texto clave
        fragmento = texto.split(clave, 1)[1]

        # Buscamos el primer número largo (cédula)
        match = re.search(r'\b\d{6,12}\b', fragmento)

        if match:
            return match.group(0)

        return None

    except Exception:
        return None

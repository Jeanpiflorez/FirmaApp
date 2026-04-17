import fitz
import os
import tempfile
import shutil
from core.utils.logging_utils import configurar_logger

logger = configurar_logger()


def insertar_firma_y_parentesco(path_pdf, firma_path, parentesco=None, output_path=None):
    try:
        logger.info(f"Iniciando inserción de firma en: {path_pdf}")
        
        # Verificar que el archivo existe y es accesible
        if not os.path.exists(path_pdf):
            raise FileNotFoundError(f"El archivo PDF no existe: {path_pdf}")
        
        if not os.path.exists(firma_path):
            raise FileNotFoundError(f"La imagen de firma no existe: {firma_path}")

        doc = fitz.open(path_pdf)
        page = doc[0]

        # Posiciones fijas para la firma
        x_firma = 90
        y_firma = 307
        ancho_firma = 300
        alto_firma = 48
        firma_rect = fitz.Rect(x_firma, y_firma, x_firma + ancho_firma, y_firma + alto_firma)

        with open(firma_path, "rb") as f:
            firma_bytes = f.read()
            page.insert_image(firma_rect, stream=firma_bytes)
            logger.info(f"Firma insertada en posición ({x_firma}, {y_firma})")

        if parentesco:
            x_texto = 200
            y_texto = 395
            page.insert_text((x_texto, y_texto), f"{parentesco}", fontsize=10, fontname="helv")
            logger.info(f"Parentesco '{parentesco}' insertado en posición ({x_texto}, {y_texto})")

        # Crear archivo temporal para reemplazar el original
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            temp_pdf_path = tmp.name

        doc.save(temp_pdf_path, garbage=4, deflate=True)
        doc.close()

        # Reemplazar el original con el firmado
        shutil.move(temp_pdf_path, path_pdf)
        logger.info(f"Archivo firmado guardado y reemplazado: {path_pdf}")

        return path_pdf

    except Exception as e:
        logger.exception(f"Error al insertar firma y parentesco en {path_pdf}: {e}")
        raise

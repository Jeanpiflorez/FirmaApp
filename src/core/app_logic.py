import os
import shutil
import time
from core.utils.pdf_utils import insertar_firma_y_parentesco
from core.utils.logging_utils import configurar_logger
from core.controllers.rutas_controller import RutasController
from ui.modules.firma.index import FirmaView
from core.utils.pdf_reader import (
    extraer_nombre_paciente,
    extraer_numero_identificacion
)

logger = configurar_logger()
rutas_controller = RutasController()

def procesar_pdf(path_pdf):
    try:
        nombre = os.path.basename(path_pdf)
        logger.info(f"Procesando archivo PDF: {nombre}")
        
        if nombre.endswith("_CURL.pdf"):
            logger.info("El archivo requiere firma digital.")

            nombre_paciente = extraer_nombre_paciente(path_pdf)

            if nombre_paciente:
                logger.info(f"Nombre del paciente detectado: {nombre_paciente}")
            else:
                logger.warning("No se pudo extraer el nombre del paciente.")
                nombre_paciente = "No identificado"

            FirmaView(
                path_pdf=path_pdf,
                nombre_paciente=nombre_paciente,
                on_firmar_callback=mover_pdf_firmado
            )
            
        elif nombre.startswith("Boxalud") and nombre.endswith(".pdf"):
            logger.info("Documento sin firma detectado. Se validará identificación y se renombrará.")
            mover_pdf_directo(path_pdf)

        else:
            logger.warning(f"Archivo no reconocido y no procesado: {nombre}")

    except Exception:
        logger.exception("Error al procesar el PDF")


def mover_pdf_firmado(path_pdf, firma_path, parentesco):
    try:
        if esperar_archivo_estable(path_pdf):
            insertar_firma_y_parentesco(path_pdf, firma_path, parentesco)
            _mover_archivo(path_pdf, eliminar=firma_path)
        else:
            logger.error(f"No se pudo firmar el archivo porque no se estabilizó: {path_pdf}")
    except Exception:
        logger.exception("Error al mover el PDF firmado")


def mover_pdf_directo(path_pdf):
    """
    Mueve el PDF sin firma.
    Si es posible, lo renombra usando el número de identificación
    extraído desde el contenido del PDF.
    """
    try:
        if not esperar_archivo_estable(path_pdf):
            logger.error(f"No se pudo mover el archivo porque no se estabilizó: {path_pdf}")
            return
        numero_id = extraer_numero_identificacion(path_pdf)

        if numero_id:
            nuevo_nombre = f"{numero_id}_DID.pdf"
            logger.info(f"Renombrando archivo con identificación: {nuevo_nombre}")
            _mover_archivo(path_pdf, nuevo_nombre=nuevo_nombre)
        else:
            logger.warning("No se pudo extraer el número de identificación. Se moverá sin renombrar.")
            _mover_archivo(path_pdf)

    except Exception:
        logger.exception("Error al mover el PDF sin firmar")


def _mover_archivo(path_origen, eliminar=None, nuevo_nombre=None, reintentos=5, espera=0.5):
    ruta_destino = rutas_controller.get_ruta_destino()

    if not ruta_destino:
        logger.warning("Ruta de destino no configurada.")
        return

    os.makedirs(ruta_destino, exist_ok=True)

    nombre_final = nuevo_nombre if nuevo_nombre else os.path.basename(path_origen)
    nueva_ruta = os.path.join(ruta_destino, nombre_final)

    for intento in range(reintentos):
        try:
            if os.path.exists(nueva_ruta):
                os.remove(nueva_ruta)

            shutil.move(path_origen, nueva_ruta)
            logger.info(f"Archivo movido a: {nueva_ruta}")
            break

        except PermissionError:
            logger.warning(
                f"Intento {intento + 1}: el archivo está en uso ({path_origen}). "
                f"Reintentando en {espera} segundos..."
            )
            time.sleep(espera)

        except Exception:
            logger.exception("Error inesperado al mover archivo")
            return

    else:
        logger.error(f"No se pudo mover el archivo después de {reintentos} intentos: {path_origen}")
        return

    if eliminar and os.path.exists(eliminar):
        try:
            os.remove(eliminar)
            logger.info(f"Archivo temporal eliminado: {eliminar}")
        except Exception as e:
            logger.warning(f"No se pudo eliminar el archivo temporal: {eliminar} -> {e}")


def esperar_archivo_estable(path, tiempo_espera=0.5, reintentos=10):
    """ Espera hasta que el archivo deje de crecer en tamaño. """
    ultimo_tamano = -1

    for intento in range(reintentos):
        if not os.path.exists(path):
            logger.warning(f"Archivo no encontrado aún: {path}")
            time.sleep(tiempo_espera)
            continue

        tamano_actual = os.path.getsize(path)

        if tamano_actual == ultimo_tamano:
            return True

        logger.debug(
            f"Tamaño del archivo aún cambiando (intento {intento + 1}): {tamano_actual} bytes"
        )
        ultimo_tamano = tamano_actual
        time.sleep(tiempo_espera)

    logger.error(f"El archivo no se estabilizó a tiempo: {path}")
    return False

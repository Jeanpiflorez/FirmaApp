from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import time
import os

from core.utils.logging_utils import configurar_logger

logger = configurar_logger()

class MonitorCarpeta:
    def __init__(self, ruta_directorio, callback_pdf_detectado):
        self.ruta = ruta_directorio
        self.callback = callback_pdf_detectado
        self.observer = Observer()

    def iniciar(self):
        try:
            event_handler = self._crear_event_handler()
            self.observer.schedule(event_handler, self.ruta, recursive=False)
            self.observer.start()

            logger.info(f"Monitor de carpeta activado en: {self.ruta}")

            hilo = threading.Thread(target=self._ejecutar)
            hilo.daemon = True
            hilo.start()

        except Exception as e:
            logger.exception(f"Error al iniciar el monitor de carpeta en {self.ruta}: {e}")

    def _esperar_archivo_disponible(self, path_archivo, timeout=10, intervalo=0.5):
        """
        Espera a que un archivo esté completamente escrito y disponible para lectura.
        
        Args:
            path_archivo: Ruta del archivo a verificar
            timeout: Tiempo máximo de espera en segundos
            intervalo: Intervalo entre verificaciones en segundos
        """
        tiempo_inicio = time.time()
        tamanio_anterior = -1
        
        while time.time() - tiempo_inicio < timeout:
            try:
                # Verificar que el archivo existe
                if not os.path.exists(path_archivo):
                    time.sleep(intervalo)
                    continue
                
                # Verificar que el tamaño del archivo no está cambiando
                tamanio_actual = os.path.getsize(path_archivo)
                
                if tamanio_actual == tamanio_anterior and tamanio_actual > 0:
                    # Intentar abrir el archivo para verificar que no está bloqueado
                    try:
                        with open(path_archivo, 'rb') as f:
                            f.read(1)  # Leer 1 byte para verificar acceso
                        logger.info(f"Archivo disponible para procesamiento: {path_archivo}")
                        return True
                    except PermissionError:
                        logger.debug(f"Archivo aún bloqueado, esperando... {path_archivo}")
                        time.sleep(intervalo)
                        continue
                
                tamanio_anterior = tamanio_actual
                time.sleep(intervalo)
                
            except Exception as e:
                logger.warning(f"Error al verificar disponibilidad del archivo: {e}")
                time.sleep(intervalo)
        
        logger.warning(f"Timeout esperando que el archivo esté disponible: {path_archivo}")
        return False

    def _crear_event_handler(self):
        monitor = self

        class Handler(FileSystemEventHandler):
            def on_created(self, event):
                try:
                    if not event.is_directory and event.src_path.endswith(".pdf"):
                        logger.info(f"Archivo PDF detectado: {event.src_path}")
                        # Esperar a que el archivo esté completamente escrito y disponible
                        monitor._esperar_archivo_disponible(event.src_path)
                        monitor.callback(event.src_path)
                except Exception as e:
                    logger.exception(f"Error al procesar archivo creado: {event.src_path}")

        return Handler()

    def _ejecutar(self):
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Deteniendo el monitor de carpeta (KeyboardInterrupt)...")
            self.observer.stop()
        except Exception as e:
            logger.exception("Error inesperado durante la ejecución del monitor")
            self.observer.stop()

        self.observer.join()
        logger.info("Monitor de carpeta detenido correctamente.")

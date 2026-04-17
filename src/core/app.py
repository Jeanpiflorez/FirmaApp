import customtkinter as ctk
from ui.modules.rutasconfig.index import RutasSetupView
from core.utils.monitor import MonitorCarpeta
from core.controllers.rutas_controller import RutasController
from core.utils.logging_utils import configurar_logger

from core.app_logic import procesar_pdf  # delegamos lógica de procesamiento

logger = configurar_logger()
rutas_controller = RutasController()

def obtener_ruta_origen():
    ruta = rutas_controller.get_ruta_origen()
    if not ruta:
        logger.warning("No se encontró ruta de origen configurada.")
        return None
    return ruta

def iniciar_monitor(ruta):
    monitor = MonitorCarpeta(ruta, procesar_pdf)
    monitor.iniciar()

def mostrar_ventana_configuracion(app):
    def continuar_app():
        ruta = obtener_ruta_origen()
        if ruta:
            app.after(500, lambda: iniciar_monitor(ruta))
    setup_view = RutasSetupView(on_guardar_callback=continuar_app)
    setup_view.grab_set()
    app.mainloop()

def lanzar_aplicacion():
    from core.bootstrap import crear_y_configurar_db, verificar_db
    from core.utils.config import DB_PATH

    crear_y_configurar_db()
    verificar_db()

    app = ctk.CTk()
    app.withdraw()
    # Maximizar la ventana principal
    app.state('zoomed')

    from core.bootstrap import hay_rutas_configuradas
    if not hay_rutas_configuradas():
        mostrar_ventana_configuracion(app)
    else:
        ruta = obtener_ruta_origen()
        if ruta:
            iniciar_monitor(ruta)
            app.mainloop()

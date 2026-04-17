import customtkinter as ctk
import tkinter.filedialog as filedialog
from core.controllers.rutas_controller import RutasController

class RutasSetupView(ctk.CTkToplevel):
    def __init__(self, on_guardar_callback=None):
        super().__init__()
        self.title("Configurar rutas")
        self.geometry("500x400")
        # Maximizar la ventana
        self.state('zoomed')
        self.resizable(True, True)

        self.controller = RutasController()
        self.on_guardar_callback = on_guardar_callback

        ctk.CTkLabel(self, text="Ruta de escucha (origen):").pack(pady=(20, 5))
        self.entry_origen = ctk.CTkEntry(self, width=400)
        self.entry_origen.pack()

        ctk.CTkButton(self, text="Seleccionar carpeta", command=self.seleccionar_origen).pack(pady=(10, 15))

        ctk.CTkLabel(self, text="Ruta de destino:").pack(pady=(10, 5))
        self.entry_destino = ctk.CTkEntry(self, width=400)
        self.entry_destino.pack()

        ctk.CTkButton(self, text="Seleccionar carpeta", command=self.seleccionar_destino).pack(pady=(10, 20))

        self.btn_guardar = ctk.CTkButton(self, text="Guardar rutas", command=self.guardar_rutas)
        self.btn_guardar.pack(pady=10)

    def seleccionar_origen(self):
        carpeta = filedialog.askdirectory(title="Seleccionar carpeta de escucha")
        if carpeta:
            self.entry_origen.delete(0, 'end')
            self.entry_origen.insert(0, carpeta)

    def seleccionar_destino(self):
        carpeta = filedialog.askdirectory(title="Seleccionar carpeta destino")
        if carpeta:
            self.entry_destino.delete(0, 'end')
            self.entry_destino.insert(0, carpeta)

    def guardar_rutas(self):
        origen = self.entry_origen.get().strip()
        destino = self.entry_destino.get().strip()

        if not origen or not destino:
            ctk.CTkLabel(self, text="Debes ingresar ambas rutas.", text_color="red").pack()
            return

        # Insertar rutas en la base de datos
        self.controller.insertar_ruta(origen, "Carpeta de escucha", "origen")
        self.controller.insertar_ruta(destino, "Carpeta destino", "destino")

        print("Rutas insertadas correctamente.")

        if self.on_guardar_callback:
            self.on_guardar_callback()  # Notificar al main que ya puede continuar

        self.destroy()

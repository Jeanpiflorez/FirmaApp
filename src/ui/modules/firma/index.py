# ui/modules/firma/index.py

import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageDraw
import os


class FirmaView(ctk.CTkToplevel):
    def __init__(self, path_pdf, nombre_paciente=None, on_firmar_callback=None):
        super().__init__()
        
        self.attributes("-fullscreen", True)
        
        self.title("Firmar Documento PDF")
        self.geometry("600x600")
        self.path_pdf = path_pdf
        self.on_firmar_callback = on_firmar_callback
        self.nombre_paciente = nombre_paciente

        self.canvas_width = 500
        self.canvas_height = 200

        # Imagen PIL para capturar la firma
        self.image = Image.new("RGBA", (self.canvas_width, self.canvas_height), (255, 255, 255, 0))
        self.draw = ImageDraw.Draw(self.image)

        self.old_x = None
        self.old_y = None

        # PDF info
        texto_info = f"PDF listo para firma:\n{os.path.basename(path_pdf)}"
        if self.nombre_paciente:
            texto_info += f"\n\nPaciente:\n{self.nombre_paciente}"
        self.label_info = ctk.CTkLabel(
            self,
            text=texto_info,
            font=("Arial", 20),
            justify="center"
        )
        self.label_info.pack(pady=15)

        # Canvas de firma
        self.canvas = tk.Canvas(self, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas.pack(pady=10)
        self.canvas.bind("<B1-Motion>", self.draw_signature)
        self.canvas.bind("<ButtonPress-1>", self.start_draw)

        # Limpiar canvas
        self.btn_limpiar = ctk.CTkButton(self, text="Limpiar firma", command=self.limpiar_canvas)
        self.btn_limpiar.pack(pady=5)

        # Checkbox: ¿El firmante es el paciente?
        self.es_paciente = tk.BooleanVar(value=True)
        self.chk_es_paciente = ctk.CTkCheckBox(self, text="¿Es el paciente quien firma?", variable=self.es_paciente, command=self.toggle_combo)
        self.chk_es_paciente.pack(pady=10)

        # ComboBox de parentesco (solo si no es el paciente)
        self.combo_parentesco = ctk.CTkComboBox(self, values=["Padre", "Madre", "Hermano/a", "Hijo/a", "Cónyuge", "Otro"])
        self.combo_parentesco.set("Padre")
        self.combo_parentesco.pack(pady=5)
        self.combo_parentesco.pack_forget()  # Oculto por defecto

        # Botones
        self.btn_firmar = ctk.CTkButton(self, text="Firmar documento", command=self.firmar_pdf)
        self.btn_firmar.pack(pady=15)

        self.btn_cancelar = ctk.CTkButton(self, text="Cancelar", command=self.destroy)
        self.btn_cancelar.pack(pady=5)

    def toggle_combo(self):
        if self.es_paciente.get():
            self.combo_parentesco.pack_forget()
        else:
            self.combo_parentesco.pack(pady=5)

    def start_draw(self, event):
        self.old_x = event.x
        self.old_y = event.y

    def draw_signature(self, event):
        if self.old_x and self.old_y:
            self.canvas.create_line(self.old_x, self.old_y, event.x, event.y, width=2, fill='black', capstyle=tk.ROUND, smooth=True)
            self.draw.line([self.old_x, self.old_y, event.x, event.y], fill='black', width=2)
        self.old_x = event.x
        self.old_y = event.y

    def limpiar_canvas(self):
        self.canvas.delete("all")
        self.draw.rectangle([0, 0, self.canvas_width, self.canvas_height], fill="white")

    def firmar_pdf(self):
        firma_path = "firma.png"
        self.image.save(firma_path)

        parentesco = None
        if not self.es_paciente.get():
            parentesco = self.combo_parentesco.get()

        if self.on_firmar_callback:
            self.on_firmar_callback(self.path_pdf, firma_path, parentesco)

        self.destroy()
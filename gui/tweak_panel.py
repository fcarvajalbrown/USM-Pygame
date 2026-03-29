# Panel de ajuste — construido dinámicamente desde slides.json de la lección activa
import json
from pathlib import Path
import customtkinter as ctk
from engine.injector import LiveInjector


class TweakPanel(ctk.CTkFrame):
    def __init__(self, parent, injector: LiveInjector, lesson_path: Path, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.injector = injector
        self.variables = self._load_variables(lesson_path)
        self._build()

    def _load_variables(self, lesson_path: Path) -> list:
        # Lee la definición de variables desde slides.json de la lección
        slides = json.loads((lesson_path / "slides.json").read_text(encoding="utf-8"))
        return slides.get("variables", [])

    def _build(self):
        ctk.CTkLabel(self, text="Panel de Ajuste",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="#FFC832").pack(anchor="w")
        ctk.CTkLabel(self, text="Declara las variables correctas.",
                     font=ctk.CTkFont(size=11),
                     text_color="#666666").pack(anchor="w", pady=(0, 12))

        for var in self.variables:
            self._add_code_input(var)

    def _add_code_input(self, var: dict):
        ctk.CTkLabel(self, text=var["hint"],
                     font=ctk.CTkFont(family="Courier New", size=11),
                     text_color="#555555").pack(anchor="w", pady=(10, 0))

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", pady=(2, 0))

        ctk.CTkLabel(row, text=f"{var['nombre']} = ",
                     font=ctk.CTkFont(family="Courier New", size=13, weight="bold"),
                     text_color="#64C8FF").pack(side="left")

        entry = ctk.CTkEntry(row, width=80,
                             font=ctk.CTkFont(family="Courier New", size=13),
                             placeholder_text=var["default"],
                             justify="center")
        entry.pack(side="left", padx=(0, 8))
        entry.insert(0, var["default"])

        feedback = ctk.CTkLabel(row, text="",
                                font=ctk.CTkFont(size=11),
                                text_color="#888888")
        feedback.pack(side="left")

        def apply(event=None, e=entry, v=var, fb=feedback):
            raw = e.get().strip()
            try:
                value = float(raw)
                self._apply_variable(v, value)
                fb.configure(text="✓", text_color="#50C850")
            except ValueError:
                fb.configure(text="valor inválido", text_color="#FF5050")
            # Devuelve el foco a la ventana principal para que W/S controlen la paleta
            self.winfo_toplevel().focus_set()

        entry.bind("<Return>", apply)
        ctk.CTkButton(self, text="Aplicar", command=apply,
                      height=26, font=ctk.CTkFont(size=11),
                      fg_color="#1a3a5c", hover_color="#1f4f80").pack(anchor="w", pady=(4, 0))

    def _apply_variable(self, var: dict, value: float):
        # Aplica el valor al objeto registrado según el transform definido en slides.json
        transform = var.get("transform", "float")
        target = var["target"]

        if transform == "int":
            self.injector.set_attr(target, var["atributos"][0], int(value))

        elif transform == "float":
            self.injector.set_attr(target, var["atributos"][0], value)

        elif transform == "speed_xy":
            # Preserva dirección actual de la pelota al cambiar magnitud
            obj = self.injector._registry.get(target)
            if obj is None:
                return
            sign_x = 1 if obj.vx >= 0 else -1
            sign_y = 1 if obj.vy >= 0 else -1
            self.injector.set_attr(target, "vx", sign_x * value)
            self.injector.set_attr(target, "vy", sign_y * value * 0.6)
# Panel de ajuste en vivo — entradas de código conectadas al injector
import customtkinter as ctk
from engine.injector import LiveInjector


class TweakPanel(ctk.CTkFrame):
    def __init__(self, parent, injector: LiveInjector, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.injector = injector
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="Panel de Ajuste",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="#FFC832").pack(anchor="w")
        ctk.CTkLabel(self, text="Declara las variables correctas.",
                     font=ctk.CTkFont(size=11),
                     text_color="#666666").pack(anchor="w", pady=(0, 12))

        self._add_code_input(
            variable="BALL_SPEED",
            hint="# Velocidad de la pelota (150 – 300)",
            default="800",
            on_apply=self._on_speed,
        )
        self._add_code_input(
            variable="PADDLE_H",
            hint="# Altura de la paleta (80 – 120)",
            default="8",
            on_apply=self._on_paddle_h,
        )

    def _add_code_input(self, variable: str, hint: str, default: str, on_apply):
        # Comentario estilo código
        ctk.CTkLabel(self, text=hint,
                     font=ctk.CTkFont(family="Courier New", size=11),
                     text_color="#555555").pack(anchor="w", pady=(10, 0))

        # Línea de declaración: VARIABLE = [entrada]
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", pady=(2, 0))

        ctk.CTkLabel(row, text=f"{variable} = ",
                     font=ctk.CTkFont(family="Courier New", size=13, weight="bold"),
                     text_color="#64C8FF").pack(side="left")

        entry = ctk.CTkEntry(row,
                             width=80,
                             font=ctk.CTkFont(family="Courier New", size=13),
                             placeholder_text=default,
                             justify="center")
        entry.pack(side="left", padx=(0, 8))
        entry.insert(0, default)

        feedback = ctk.CTkLabel(row, text="",
                                font=ctk.CTkFont(size=11),
                                text_color="#888888")
        feedback.pack(side="left")

        def apply(event=None, e=entry, cb=on_apply, fb=feedback):
            raw = e.get().strip()
            try:
                value = float(raw)
                cb(value)
                fb.configure(text="✓", text_color="#50C850")
            except ValueError:
                fb.configure(text="valor inválido", text_color="#FF5050")

        entry.bind("<Return>", apply)

        ctk.CTkButton(self, text="Aplicar",
                      command=apply,
                      height=26,
                      font=ctk.CTkFont(size=11),
                      fg_color="#1a3a5c", hover_color="#1f4f80").pack(anchor="w", pady=(4, 0))

    # --- Callbacks ---

    def _on_speed(self, value: float):
        # Preserva dirección de la pelota al cambiar magnitud
        ball = self.injector._registry.get("pelota")
        if ball is None:
            return
        sign_x = 1 if ball.vx >= 0 else -1
        sign_y = 1 if ball.vy >= 0 else -1
        self.injector.set_attr("pelota", "vx", sign_x * value)
        self.injector.set_attr("pelota", "vy", sign_y * value * 0.6)

    def _on_paddle_h(self, value: float):
        self.injector.set_attr("paleta_jugador", "h", int(value))
        self.injector.set_attr("paleta_enemigo", "h", int(value))
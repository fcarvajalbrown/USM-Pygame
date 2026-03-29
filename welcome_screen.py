# Pantalla de bienvenida — el estudiante maximiza antes de entrar al juego
# En el futuro: lista de lecciones disponibles para seleccionar
import customtkinter as ctk
from pathlib import Path


class WelcomeScreen(ctk.CTk):
    def __init__(self, available_lessons: list[dict]):
        super().__init__()
        self.title("AtariLab — USM")
        self.geometry("700x500")
        self.resizable(True, True)

        # Lección seleccionada — None hasta que el estudiante confirme
        self.selected_lesson: Path | None = None

        self._lessons = available_lessons
        self._selected_index: int | None = None

        self._build()

    def _build(self):
        # Título
        ctk.CTkLabel(self, text="AtariLab",
                     font=ctk.CTkFont(size=48, weight="bold"),
                     text_color="#FFC832").pack(pady=(48, 4))

        ctk.CTkLabel(self, text="Universidad Santa María — Aprendizaje de POO mediante juegos",
                     font=ctk.CTkFont(size=14),
                     text_color="#666666").pack(pady=(0, 32))

        # Lista de lecciones
        ctk.CTkLabel(self, text="Selecciona una lección:",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color="#CCCCCC").pack(anchor="center", pady=(0, 12))

        lesson_frame = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=12)
        lesson_frame.pack(padx=80, fill="x")

        self._btn_refs = []
        for i, lesson in enumerate(self._lessons):
            btn = ctk.CTkButton(
                lesson_frame,
                text=f"  {lesson['titulo']}",
                font=ctk.CTkFont(size=14),
                anchor="w",
                fg_color="transparent",
                hover_color="#2a2a2a",
                text_color="#AAAAAA",
                command=lambda idx=i: self._select(idx),
            )
            btn.pack(fill="x", padx=8, pady=4)
            self._btn_refs.append(btn)

        # Botón de inicio
        self.btn_enter = ctk.CTkButton(
            self,
            text="Entrar a la Lección  →",
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#2D7D2D", hover_color="#3A9A3A",
            height=44, width=260,
            state="disabled",
            command=self._confirm,
        )
        self.btn_enter.pack(pady=32)

        ctk.CTkLabel(self, text="💡 Maximiza la ventana antes de entrar para mejor experiencia.",
                     font=ctk.CTkFont(size=11),
                     text_color="#444444").pack(pady=(0, 16))

    def _select(self, index: int):
        # Resalta la lección seleccionada
        for i, btn in enumerate(self._btn_refs):
            btn.configure(
                fg_color="#1f4f80" if i == index else "transparent",
                text_color="#FFFFFF" if i == index else "#AAAAAA",
            )
        self._selected_index = index
        self.btn_enter.configure(state="normal")

    def _confirm(self):
        if self._selected_index is None:
            return
        self.selected_lesson = self._lessons[self._selected_index]["path"]
        self.destroy()
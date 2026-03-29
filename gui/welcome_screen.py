# Pantalla de bienvenida — logo animado por partes, luego selección de lección
import customtkinter as ctk
from pathlib import Path


# Colores del logo
_NAVY  = "#002B5C"
_RED   = "#E63946"
_GREEN = "#2DC653"
_BLUE  = "#1982C4"

# Escala del logo en canvas (viewBox original 680×280 → mostrar a 340×140)
_SCALE = 0.5
_CW, _CH = int(680 * _SCALE), int(280 * _SCALE)


def _s(v): return int(v * _SCALE)  # helper de escala


class WelcomeScreen(ctk.CTk):
    def __init__(self, available_lessons: list[dict]):
        super().__init__()
        self.title("USM-Pygame")
        self.geometry("720x560")
        self.resizable(True, True)

        self.selected_lesson: Path | None = None
        self._lessons = available_lessons
        self._selected_index: int | None = None

        self._build()
        # Arranca animación del logo 100ms después de que la ventana esté lista
        self.after(100, self._animate_logo)

    def _build(self):
        # Canvas del logo
        _bg = "#212121" if ctk.get_appearance_mode() == "Dark" else "#ebebeb"
        self.logo_canvas = ctk.CTkCanvas(
            self, width=_CW, height=_CH,
            bg=_bg, highlightthickness=0,
        )
        self.logo_canvas.pack(pady=(36, 0))

        # Subtítulo — aparece tras el logo
        self.lbl_sub = ctk.CTkLabel(
            self,
            text="Universidad Técnica Federico Santa María — Aprendizaje de POO mediante juegos",
            font=ctk.CTkFont(size=12),
            text_color="#444444",
        )

        # Sección de lecciones — aparece tras el subtítulo
        self.lesson_section = ctk.CTkFrame(self, fg_color="transparent")

        ctk.CTkLabel(self.lesson_section, text="Selecciona una lección:",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color="#CCCCCC").pack(anchor="center", pady=(0, 8))

        lesson_frame = ctk.CTkFrame(self.lesson_section, fg_color="#1a1a1a", corner_radius=12)
        lesson_frame.pack(padx=80, fill="x")

        self._btn_refs = []
        for i, lesson in enumerate(self._lessons):
            btn = ctk.CTkButton(
                lesson_frame,
                text=f"  {lesson['titulo']}",
                font=ctk.CTkFont(size=13),
                anchor="w",
                fg_color="transparent",
                hover_color="#2a2a2a",
                text_color="#AAAAAA",
                command=lambda idx=i: self._select(idx),
            )
            btn.pack(fill="x", padx=8, pady=4)
            self._btn_refs.append(btn)

        # Botón de entrada — aparece al final
        self.btn_enter = ctk.CTkButton(
            self,
            text="Entrar a la Lección  →",
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#2D7D2D", hover_color="#3A9A3A",
            height=44, width=260,
            state="disabled",
            command=self._confirm,
        )

        self.lbl_hint = ctk.CTkLabel(
            self,
            text="Maximiza la ventana antes de entrar para mejor experiencia.",
            font=ctk.CTkFont(size=11),
            text_color="#444444",
        )

    # --- Animación del logo parte por parte ---

    def _animate_logo(self):
        c = self.logo_canvas
        delay = 0

        def after(ms, fn):
            # helper para encadenar pasos
            self.after(delay + ms, fn)

        # Paso 1: barra vertical navy
        def step1():
            c.create_rectangle(_s(200), _s(40), _s(208), _s(240), fill=_NAVY, outline="")
        self.after(0, step1); delay += 120

        # Paso 2: bloques columna izquierda
        def step2():
            c.create_rectangle(_s(216), _s(40),  _s(242), _s(106), fill=_RED,   outline="")
        self.after(delay, step2); delay += 100

        def step3():
            c.create_rectangle(_s(216), _s(114), _s(242), _s(180), fill=_GREEN, outline="")
        self.after(delay, step3); delay += 100

        def step4():
            c.create_rectangle(_s(216), _s(188), _s(242), _s(240), fill=_BLUE,  outline="")
        self.after(delay, step4); delay += 100

        # Paso 3: bloques columna derecha
        def step5():
            c.create_rectangle(_s(250), _s(40),  _s(276), _s(92),  fill=_BLUE,  outline="")
        self.after(delay, step5); delay += 100

        def step6():
            c.create_rectangle(_s(250), _s(100), _s(276), _s(166), fill=_RED,   outline="")
        self.after(delay, step6); delay += 100

        def step7():
            c.create_rectangle(_s(250), _s(174), _s(276), _s(240), fill=_GREEN, outline="")
        self.after(delay, step7); delay += 120

        # Paso 4: texto USM
        def step8():
            c.create_text(_s(296), _s(132), text="USM",
                          font=("Georgia", int(72 * _SCALE), "bold"),
                          fill=_NAVY, anchor="w")
        self.after(delay, step8); delay += 120

        # Paso 5: línea roja — ancho aproximado del texto USM a 72px Georgia (~190px)
        def step9():
            c.create_rectangle(_s(296), _s(151), _s(486), _s(155), fill=_RED, outline="")
        self.after(delay, step9); delay += 120

        # Paso 6: texto Pygame
        def step10():
            c.create_text(_s(296), _s(196), text="Pygame",
                          font=("Georgia", int(44 * _SCALE)),
                          fill=_NAVY, anchor="w")
        self.after(delay, step10); delay += 200

        # Revelar resto de la UI
        def reveal():
            self.lbl_sub.pack(pady=(8, 20))
            self.lesson_section.pack(padx=40, fill="x", pady=(0, 16))
            self.btn_enter.pack(pady=(8, 4))
            self.lbl_hint.pack(pady=(0, 16))

        self.after(delay, reveal)

    def _select(self, index: int):
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
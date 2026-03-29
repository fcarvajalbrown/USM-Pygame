# Ventana principal — genérica, sin hardcoding de lección alguna
import json
import threading
import importlib
from pathlib import Path

import customtkinter as ctk
from PIL import Image, ImageTk
import pygame

from engine.injector import LiveInjector
from engine.validation_watcher import ValidationWatcher
from gui.tweak_panel import TweakPanel

GAME_W, GAME_H = 800, 600
FPS = 60

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Teclas rastreadas desde CTk — Pygame offscreen no recibe eventos de teclado
_keys_held: set[str] = set()


class AtariLabApp(ctk.CTk):
    def __init__(self, lesson_path: Path):
        super().__init__()
        self.lesson_path = lesson_path
        self.slides = json.loads((lesson_path / "slides.json").read_text(encoding="utf-8"))

        # Importa template y win_condition dinámicamente desde la carpeta de la lección
        module_base = ".".join(lesson_path.parts[-2:])  # e.g. "lessons.pong_01"
        self.lesson = importlib.import_module(f"{module_base}.template")
        win_mod = importlib.import_module(f"{module_base}.win_condition")

        self.injector = LiveInjector()
        self.watcher = ValidationWatcher(win_mod.win_condition)

        self.game_objects: tuple | None = None  # lo que retorna lesson.build()

        self._running = False
        self._paused = False
        self._game_thread = None
        self._pending_frame = None
        self._photo = None
        self._intro_confirmed = False  # juego bloqueado hasta que el estudiante confirme

        self.title(f"USM-Pygame — {self.slides['intro']['titulo']}")
        self.resizable(True, True)

        self._build_layout()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.bind("<KeyPress>", lambda e: _keys_held.add(e.keysym.lower()))
        self.bind("<KeyRelease>", lambda e: _keys_held.discard(e.keysym.lower()))

        # Popup se muestra 200ms después de que mainloop arranca — única forma confiable en Windows
        self.after(200, self._show_lesson_intro)

    # --- Layout ---

    def _build_layout(self):
        left = ctk.CTkFrame(self, fg_color="transparent")
        left.pack(side="left", padx=12, pady=12, fill="both", expand=True)

        self.canvas = ctk.CTkCanvas(left, bg="#141414", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        score_row = ctk.CTkFrame(left, fg_color="transparent")
        score_row.pack(fill="x", pady=(6, 0))

        self.lbl_player = ctk.CTkLabel(score_row, text="Jugador: 0",
                                        font=ctk.CTkFont(size=16, weight="bold"),
                                        text_color="#64C8FF")
        self.lbl_player.pack(side="left", padx=20)

        self.lbl_status = ctk.CTkLabel(score_row, text="⏸ Presiona Iniciar",
                                        font=ctk.CTkFont(size=14),
                                        text_color="#AAAAAA")
        self.lbl_status.pack(side="left", expand=True)

        self.lbl_enemy = ctk.CTkLabel(score_row, text="IA: 0",
                                       font=ctk.CTkFont(size=16, weight="bold"),
                                       text_color="#FF7850")
        self.lbl_enemy.pack(side="right", padx=20)

        right = ctk.CTkFrame(self, width=300, fg_color="#1a1a1a", corner_radius=12)
        right.pack(side="right", fill="y", padx=(0, 12), pady=12)
        right.pack_propagate(False)

        ctk.CTkLabel(right, text="USM-Pygame",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color="#FFC832").pack(pady=(20, 2))
        ctk.CTkLabel(right, text=self.slides["intro"]["titulo"],
                     font=ctk.CTkFont(size=12),
                     text_color="#888888").pack(pady=(0, 16))

        btn_frame = ctk.CTkFrame(right, fg_color="transparent")
        btn_frame.pack(fill="x", padx=16, pady=(0, 12))

        self.btn_start = ctk.CTkButton(btn_frame, text="▶  Iniciar",
                                        command=self._on_iniciar,
                                        fg_color="#2D7D2D", hover_color="#3A9A3A")
        self.btn_start.pack(fill="x", pady=3)

        self.btn_pause = ctk.CTkButton(btn_frame, text="⏸  Pausar",
                                        command=self._toggle_pause,
                                        fg_color="#7D5A00", hover_color="#A07500",
                                        state="disabled")
        self.btn_pause.pack(fill="x", pady=3)

        self.btn_restart = ctk.CTkButton(btn_frame, text="↺  Reiniciar",
                                          command=self._restart_lesson,
                                          fg_color="#5A2D7D", hover_color="#7A3DAA",
                                          state="disabled")
        self.btn_restart.pack(fill="x", pady=3)

        ctk.CTkLabel(right, text="CONTROLES: W / S",
                     font=ctk.CTkFont(size=11),
                     text_color="#555555").pack(pady=(0, 8))

        ctk.CTkFrame(right, height=1, fg_color="#333333").pack(fill="x", padx=16, pady=8)

        # TweakPanel recibe la ruta de la lección — lee variables[] desde slides.json
        self.tweak_panel = TweakPanel(right, self.injector, self.lesson_path)
        self.tweak_panel.pack(fill="x", padx=16, pady=4)

        ctk.CTkFrame(right, height=1, fg_color="#333333").pack(fill="x", padx=16, pady=8)

        ctk.CTkLabel(right, text="Estado de la Lección",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color="#CCCCCC").pack(pady=(0, 4))

        self.lbl_lesson = ctk.CTkLabel(right,
                                        text="Inicia el juego para comenzar.",
                                        font=ctk.CTkFont(size=12),
                                        text_color="#AAAAAA",
                                        wraplength=260,
                                        justify="center")
        self.lbl_lesson.pack(padx=16, pady=(0, 16))

    # --- Popup de introducción ---

    def _on_iniciar(self):
        # Si el estudiante aún no vio el popup, mostrarlo primero
        if not self._intro_confirmed:
            self._show_lesson_intro()
        else:
            self._start_game()

    def _show_lesson_intro(self):
        intro = self.slides["intro"]

        popup = ctk.CTkToplevel(self)
        popup.title(intro["titulo"])
        popup.geometry("500x380")
        popup.resizable(False, False)
        popup.lift()
        popup.focus_force()
        popup.grab_set()

        ctk.CTkLabel(popup, text=f"🎮 {intro['titulo']}",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="#FFC832").pack(pady=(24, 8))

        ctk.CTkLabel(popup, text=intro["cuerpo"],
                     font=ctk.CTkFont(size=13),
                     text_color="#CCCCCC",
                     justify="left",
                     wraplength=440).pack(padx=32, pady=(0, 20))

        def on_confirm():
            popup.grab_release()
            popup.destroy()
            self._intro_confirmed = True
            self._start_game()

        ctk.CTkButton(popup, text=intro["boton"],
                      command=on_confirm,
                      fg_color="#2D7D2D", hover_color="#3A9A3A",
                      width=200).pack(pady=(0, 24))

    # --- Control del juego ---

    def _start_game(self):
        if self._running or not self._intro_confirmed:
            return
        self.watcher.reset()
        self.game_objects = self.lesson.build(self.injector)
        self._running = True
        self._paused = False
        self._game_thread = threading.Thread(target=self._game_loop, daemon=True)
        self._game_thread.start()
        self.btn_start.configure(state="disabled")
        self.btn_pause.configure(state="normal")
        self.btn_restart.configure(state="normal")
        self._tick_gui()

    def _toggle_pause(self):
        self._paused = not self._paused
        self.btn_pause.configure(text="▶  Reanudar" if self._paused else "⏸  Pausar")

    def _restart_lesson(self):
        self.watcher.reset()
        self.game_objects = self.lesson.build(self.injector)

    def _on_close(self):
        self._running = False
        self.destroy()

    # --- Loop del juego (hilo separado) ---

    def _game_loop(self):
        pygame.init()
        surface = pygame.Surface((GAME_W, GAME_H))
        clock = pygame.time.Clock()

        while self._running:
            clock.tick(FPS)

            if self._paused:
                continue

            dt = clock.tick(FPS) / 1000.0
            pygame.event.pump()

            if self.game_objects is None:
                continue

            # run_frame recibe los objetos desempaquetados + estado compartido
            self.lesson.run_frame(*self.game_objects, _keys_held, dt, surface, self.watcher)

            raw = pygame.image.tobytes(surface, "RGB")
            self._pending_frame = Image.frombytes("RGB", (GAME_W, GAME_H), raw)

        pygame.quit()

    # --- Tick de la GUI (hilo principal) ---

    def _tick_gui(self):
        if not self._running:
            return

        frame = self._pending_frame
        if frame is not None:
            cw = self.canvas.winfo_width()
            ch = self.canvas.winfo_height()
            if cw > 1 and ch > 1:
                scale = min(cw / GAME_W, ch / GAME_H)
                nw, nh = int(GAME_W * scale), int(GAME_H * scale)
                ox, oy = (cw - nw) // 2, (ch - nh) // 2
                scaled = frame.resize((nw, nh), Image.Resampling.NEAREST)
                self._photo = ImageTk.PhotoImage(scaled)
                self.canvas.delete("all")
                self.canvas.create_image(ox, oy, anchor="nw", image=self._photo)
            self._pending_frame = None

        # Marcadores — el contrato asume player en índice 0, enemy en índice 1
        if self.game_objects:
            player, enemy = self.game_objects[0], self.game_objects[1]
            self.lbl_player.configure(text=f"Jugador: {player.score}")
            self.lbl_enemy.configure(text=f"IA: {enemy.score}")
            falta = max(0, 3 - player.score)

            if self.watcher.passed:
                self.lbl_lesson.configure(text="✅ ¡Lección superada!\nConcepto desbloqueado.",
                                           text_color="#50C850")
                self.lbl_status.configure(text="✅ ¡Superada!", text_color="#50C850")
            elif self._paused:
                self.lbl_status.configure(text="⏸ Pausado", text_color="#FFAA00")
            else:
                self.lbl_lesson.configure(text=f"Calibra el juego y anota {falta} punto(s) más.",
                                           text_color="#AAAAAA")
                self.lbl_status.configure(text="▶ En juego", text_color="#64C8FF")

        self.after(16, self._tick_gui)
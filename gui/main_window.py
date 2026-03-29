# Ventana principal con CustomTkinter — Pygame renderiza en un canvas embebido vía PIL
import threading
import customtkinter as ctk
from PIL import Image, ImageTk
import pygame

from engine.injector import LiveInjector
from engine.validation_watcher import ValidationWatcher
from gui.tweak_panel import TweakPanel
from lessons.pong_01 import template as pong
from lessons.pong_01.win_condition import win_condition

GAME_W, GAME_H = 800, 600
FPS = 60

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Teclas rastreadas manualmente desde CTk
_keys_held: set[str] = set()


class AtariLabApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AtariLab — USM")
        self.resizable(True, True)

        self.injector = LiveInjector()
        self.watcher = ValidationWatcher(win_condition)

        self.player = None
        self.enemy = None
        self.ball = None

        self._running = False
        self._paused = False
        self._game_thread = None
        self._photo = None

        self._build_layout()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Capturar teclado en la ventana CTk — Pygame offscreen no recibe eventos
        self.bind("<KeyPress>", lambda e: _keys_held.add(e.keysym.lower()))
        self.bind("<KeyRelease>", lambda e: _keys_held.discard(e.keysym.lower()))

        # Mostrar popup de la lección al arrancar — after() espera a que la ventana esté lista
        self.after(300, self._show_lesson_intro)

    # --- Layout ---

    def _build_layout(self):
        # Panel izquierdo: canvas del juego + marcador
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

        # Panel derecho: controles + sliders
        right = ctk.CTkFrame(self, width=300, fg_color="#1a1a1a", corner_radius=12)
        right.pack(side="right", fill="y", padx=(0, 12), pady=12)
        right.pack_propagate(False)

        ctk.CTkLabel(right, text="AtariLab",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color="#FFC832").pack(pady=(20, 2))
        ctk.CTkLabel(right, text="Lección 01 · Variables & Tipos",
                     font=ctk.CTkFont(size=12),
                     text_color="#888888").pack(pady=(0, 16))

        # Botones de control
        btn_frame = ctk.CTkFrame(right, fg_color="transparent")
        btn_frame.pack(fill="x", padx=16, pady=(0, 12))

        self.btn_start = ctk.CTkButton(btn_frame, text="▶  Iniciar",
                                        command=self._show_lesson_intro,
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

        # Separador
        ctk.CTkFrame(right, height=1, fg_color="#333333").pack(fill="x", padx=16, pady=8)

        # Panel de ajuste (sliders)
        self.tweak_panel = TweakPanel(right, self.injector)
        self.tweak_panel.pack(fill="x", padx=16, pady=4)

        # Separador
        ctk.CTkFrame(right, height=1, fg_color="#333333").pack(fill="x", padx=16, pady=8)

        # Estado de la lección
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

    # --- Control del juego ---

    def _show_lesson_intro(self):
        # Carga el contenido del popup desde la lección activa
        import json
        from pathlib import Path
        root = Path(__file__).parent.parent
        slides_path = root / "lessons" / "pong_01" / "slides.json"

        try:
            data = json.loads(slides_path.read_text(encoding="utf-8"))
            intro = data["intro"]
        except Exception as e:
            print(f"Error cargando slides.json: {e}")
            self._start_game()
            return

        popup = ctk.CTkToplevel(self)
        popup.title(intro["titulo"])
        popup.geometry("500x380")
        popup.resizable(False, False)

        # Forzar al frente en Windows
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
            self._start_game()

        ctk.CTkButton(popup, text=intro["boton"],
                      command=on_confirm,
                      fg_color="#2D7D2D", hover_color="#3A9A3A",
                      width=200).pack(pady=(0, 24))

        # Bloquea el mainloop hasta que el popup se cierre
        self.wait_window(popup)

    def _start_game(self):
        if self._running:
            return
        self.watcher.reset()
        self.player, self.enemy, self.ball = pong.build(self.injector)
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
        label = "▶  Reanudar" if self._paused else "⏸  Pausar"
        self.btn_pause.configure(text=label)

    def _restart_lesson(self):
        self.watcher.reset()
        self.player, self.enemy, self.ball = pong.build(self.injector)

    def _on_close(self):
        self._running = False
        self.destroy()

    # --- Loop del juego (hilo separado) ---

    def _game_loop(self):
        pygame.init()
        # Superficie offscreen — sin ventana nativa de Pygame
        surface = pygame.Surface((GAME_W, GAME_H))
        clock = pygame.time.Clock()

        while self._running:
            clock.tick(FPS)

            if self._paused:
                continue

            dt = clock.tick(FPS) / 1000.0

            pygame.event.pump()

            if self.player is None or self.enemy is None or self.ball is None:
                continue

            pong.run_frame(self.player, self.enemy, self.ball,
                           _keys_held, dt, surface, self.watcher)

            # Convertir surface a ImageTk y programar actualización en el hilo principal
            raw = pygame.image.tobytes(surface, "RGB")
            img = Image.frombytes("RGB", (GAME_W, GAME_H), raw)
            self._pending_frame = img

        pygame.quit()

    # --- Tick de la GUI (hilo principal) ---

    def _tick_gui(self):
        if not self._running:
            return

        # Volcar el frame pendiente al canvas
        frame = getattr(self, "_pending_frame", None)
        if frame is not None:
            cw = self.canvas.winfo_width()
            ch = self.canvas.winfo_height()
            if cw > 1 and ch > 1:
                scaled = frame.resize((cw, ch), Image.Resampling.NEAREST)
                self._photo = ImageTk.PhotoImage(scaled)
                self.canvas.create_image(0, 0, anchor="nw", image=self._photo)
            self._pending_frame = None

        # Actualizar marcadores
        if self.player and self.enemy:
            self.lbl_player.configure(text=f"Jugador: {self.player.score}")
            self.lbl_enemy.configure(text=f"IA: {self.enemy.score}")

        # Actualizar estado de la lección
        if self.watcher.passed:
            self.lbl_lesson.configure(
                text="✅ ¡Lección superada!\nConcepto desbloqueado.",
                text_color="#50C850"
            )
            self.lbl_status.configure(text="✅ ¡Superada!", text_color="#50C850")
        elif self._paused:
            self.lbl_status.configure(text="⏸ Pausado", text_color="#FFAA00")
        else:
            falta = max(0, 3 - (self.player.score if self.player else 0))
            self.lbl_lesson.configure(
                text=f"Calibra el juego y anota {falta} punto(s) más.",
                text_color="#AAAAAA"
            )
            self.lbl_status.configure(text="▶ En juego", text_color="#64C8FF")

        # Reprogramar en 16ms (~60fps)
        self.after(16, self._tick_gui)
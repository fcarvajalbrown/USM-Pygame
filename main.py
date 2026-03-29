# Punto de entrada — bienvenida persiste en memoria, juego se abre encima
import json
from pathlib import Path
import customtkinter as ctk
from gui.welcome_screen import WelcomeScreen
from gui.main_window import AtariLabApp

ROOT = Path(__file__).parent


def discover_lessons() -> list[dict]:
    lessons = []
    for folder in sorted((ROOT / "lessons").iterdir()):
        slides = folder / "slides.json"
        if folder.is_dir() and slides.exists():
            data = json.loads(slides.read_text(encoding="utf-8"))
            lessons.append({"titulo": data["intro"]["titulo"], "path": folder})
    return lessons


if __name__ == "__main__":
    lessons = discover_lessons()

    welcome = WelcomeScreen(available_lessons=lessons)
    welcome.state("zoomed")

    # Espera hasta que el estudiante seleccione una lección
    welcome.wait_variable(welcome.lesson_selected_var)

    if welcome.selected_lesson is None:
        raise SystemExit

    app = AtariLabApp(lesson_path=welcome.selected_lesson, root=welcome)
    app.state("zoomed")
    app.mainloop()
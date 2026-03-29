# Punto de entrada — selecciona la lección y muestra el popup antes de arrancar
from pathlib import Path
from gui.main_window import AtariLabApp

LESSON = Path(__file__).parent / "lessons" / "pong_01"

if __name__ == "__main__":
    app = AtariLabApp(lesson_path=LESSON)
    app.update()                   # renderiza la ventana completa antes del popup
    app.update_idletasks()         # asegura que todos los widgets estén dibujados
    app._show_lesson_intro()       # bloquea hasta que el estudiante confirme
    app.mainloop()
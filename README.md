# USM Pygame

Plataforma de aprendizaje de Python y POO mediante juegos Atari rotos.
Desarrollado para primer año de Ingeniería en Diseño de Videojuegos, Universidad Técnica Federico Santa María.

## Estructura del proyecto

```
USM-Pygame/
├── main.py                          # Punto de entrada — descubre lecciones y abre bienvenida
├── requirements.txt                 # pygame-ce, customtkinter, pillow, pygments
│
├── assets/
│   └── logo.svg                     # Logo USM Pygame (SVG vectorial)
│
├── engine/                          # Motor compartido por todas las lecciones
│   ├── base_entities.py             # AtariObject → MovingObject → Destructible
│   ├── injector.py                  # Bridge setattr para mutación en vivo
│   └── validation_watcher.py        # Evalúa condición de victoria por frame
│
├── gui/                             # Interfaz CustomTkinter
│   ├── welcome_screen.py            # Bienvenida con logo animado + selección de lección
│   ├── main_window.py               # Ventana principal + loop Pygame embebido
│   ├── tweak_panel.py               # Panel de variables (construido desde slides.json)
│   ├── xray_overlay.py              # (pendiente) Overlay de estado de objetos en vivo
│   └── code_editor.py               # (pendiente) Editor de código embebido
│
└── lessons/                         # Una carpeta por lección — descubiertas automáticamente
    └── pong_01/                     # Lección 01: Variables & Tipos
        ├── template.py              # Juego roto + build(injector) + run_frame(...)
        ├── win_condition.py         # win_condition(state) -> bool
        └── slides.json              # intro{}, variables[], diapositivas[]
```

## Contrato de cada lección

Cada carpeta en `lessons/` debe implementar:

| Archivo | Contrato |
|---|---|
| `template.py` | `build(injector) -> tuple` — retorna (player, enemy, *resto); `run_frame(*objects, keys, dt, surface, watcher)` |
| `win_condition.py` | `win_condition(state: dict) -> bool` — importa constantes vía importación relativa |
| `slides.json` | `intro{}`, `variables[]`, `diapositivas[]` — ver pong_01 como referencia |

**Nota:** `main_window.py` asume `game_objects[0].score` = jugador, `game_objects[1].score` = IA.
Toda lección nueva debe respetar este orden en el retorno de `build()`.

El panel de ajuste y el popup se construyen automáticamente desde `slides.json`.
Agregar una lección nueva no requiere modificar ningún archivo fuera de su carpeta.

## Instalación

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```
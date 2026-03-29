# USM Pygame

Plataforma de aprendizaje de Python y POO mediante juegos Atari rotos.
Desarrollado para primer año de Ingeniería en Diseño de Videojuegos, Universidad Santa María.

## Estructura del proyecto

```
USM-Pygame/
├── main.py                          # Punto de entrada
├── requirements.txt                 # pygame-ce, customtkinter, pillow, pygments
│
├── engine/                          # Motor compartido por todas las lecciones
│   ├── base_entities.py             # AtariObject → MovingObject → Destructible
│   ├── injector.py                  # Bridge setattr para mutación en vivo
│   └── validation_watcher.py        # Evalúa condición de victoria por frame
│
├── gui/                             # Interfaz CustomTkinter
│   ├── main_window.py               # Ventana principal + loop Pygame embebido
│   ├── tweak_panel.py               # Panel de variables (construido desde slides.json)
│   ├── xray_overlay.py              # (pendiente) Overlay de estado de objetos
│   └── code_editor.py               # (pendiente) Editor de código embebido
│
└── lessons/                         # Una carpeta por lección
    └── pong_01/                     # Lección 01: Variables & Tipos
        ├── template.py              # Juego roto + build() + run_frame()
        ├── win_condition.py         # Lambda de condición de victoria
        └── slides.json              # intro, variables[], diapositivas[]
```

## Contrato de cada lección

Cada carpeta en `lessons/` debe implementar:

- `template.py` — expone `build(injector) -> tuple` y `run_frame(...)`
- `win_condition.py` — expone `win_condition(state: dict) -> bool`
- `slides.json` — define `intro`, `variables[]` y `diapositivas[]`

El panel de ajuste y el popup se construyen automáticamente desde `slides.json`.
`main_window.py` nunca hardcodea el nombre de una lección.

## Instalación

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

# Changelog

## v0.1.0 — 2026-03-29

### Added
- Welcome screen with animated USM-Pygame logo (part-by-part reveal)
- Lesson selection screen — new lessons auto-discovered from `lessons/` folder
- Lección 01: Variables & Tipos — Pong en Modo Caos
  - Ball speed broken to 800 px/s, player paddle broken to 8px
  - Live variable injection via `BALL_SPEED` and `PADDLE_H` code-style inputs
  - Validation watcher — passes when speed ∈ [150,300], paddle ≥ 80px, score ≥ 3
  - Intro popup loaded from `slides.json` — explains the lesson goal before starting
  - AI opponent at 85% paddle speed — competent but beatable
  - Bottom and top wall collision, letterboxed scaling on resize
- Engine: `AtariObject → MovingObject → Destructible` inheritance chain
- Engine: `LiveInjector` — `setattr` bridge for real-time object mutation
- Engine: `ValidationWatcher` — per-frame win condition evaluation
- GUI: `TweakPanel` — dynamically built from `slides.json` variables block
- All windows open maximized by default
- MIT license

### Architecture
- Lesson contract: `build(injector)`, `run_frame(...)`, `win_condition(state)`, `slides.json`
- Adding a new lesson requires zero changes outside its own folder
- `WelcomeScreen` is the persistent Tk root — never destroyed
- `AtariLabApp` is a `CTkToplevel` child of the welcome screen

### Known issues
- `xray_overlay.py` and `code_editor.py` not yet implemented
- Windows only (Inno Setup installer pending)
- Only one lesson available
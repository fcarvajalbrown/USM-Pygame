# Validador de condiciones de victoria por lección
from typing import Callable


class ValidationWatcher:
    # Evalúa el estado del juego contra la condición de victoria definida en la lección
    def __init__(self, win_condition: Callable[[dict], bool]):
        self.win_condition = win_condition
        self.passed = False
        self.ticks = 0

    def update(self, state: dict):
        # Llama la condición en cada frame; marca passed cuando se cumple
        self.ticks += 1
        if not self.passed and self.win_condition(state):
            self.passed = True

    def reset(self):
        self.passed = False
        self.ticks = 0

# Entidades base del motor — todas las lecciones heredan desde aquí
import pygame

SCREEN_W = 800
SCREEN_H = 600


class AtariObject:
    # Objeto raíz: posición, tamaño y dibujo básico
    def __init__(self, x: float, y: float, w: int, h: int, color=(255, 255, 255)):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, self.color, (int(self.x), int(self.y), self.w, self.h))

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)


class Destructible(AtariObject):
    # Agrega HP al objeto; subclases pueden definir on_death()
    def __init__(self, *args, hp: int = 1, **kwargs):
        super().__init__(*args, **kwargs)
        self.hp = hp
        self.max_hp = hp
        self.alive = True

    def take_damage(self, amount: int = 1):
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False
            self.on_death()

    def on_death(self):
        # Gancho para que subclases definan efectos al morir
        pass


class MovingObject(AtariObject):
    # Agrega velocidad vectorial y rebote en bordes de pantalla
    def __init__(self, *args, vx: float = 0, vy: float = 0, **kwargs):
        super().__init__(*args, **kwargs)
        self.vx = vx
        self.vy = vy

    def update(self, dt: float):
        self.x += self.vx * dt
        self.y += self.vy * dt

    def bounce_walls(self):
        # Rebota en bordes izquierdo/derecho
        if self.x <= 0 or self.x + self.w >= SCREEN_W:
            self.vx *= -1
        # Rebota en bordes superior e inferior
        if self.y <= 0 or self.y + self.h >= SCREEN_H:
            self.vy *= -1
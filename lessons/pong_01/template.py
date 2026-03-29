# Lección 01 — Pong en modo caos: velocidad y tamaño deliberadamente rotos
# El estudiante corrige BALL_SPEED y PADDLE_H escribiendo el valor correcto
import pygame
from engine.base_entities import AtariObject, MovingObject, SCREEN_W, SCREEN_H
from engine.injector import LiveInjector
from engine.validation_watcher import ValidationWatcher

# Ambos valores están rotos a propósito — el estudiante los corrige
BALL_SPEED_DEFAULT = 800   # demasiado rápido; valor correcto: 150–300
PADDLE_H_DEFAULT = 8       # paleta del JUGADOR — rota a propósito; valor correcto: 80–120
PADDLE_H_ENEMY = 90        # paleta de la IA — tamaño normal, no está rota
PADDLE_W = 14
PADDLE_SPEED = 400
WIN_SCORE = 3


class Paddle(AtariObject):
    # Paleta controlada por teclado; hereda dibujo de AtariObject
    def __init__(self, x, is_player=True):
        h = PADDLE_H_DEFAULT if is_player else PADDLE_H_ENEMY
        super().__init__(x, SCREEN_H // 2 - h // 2, PADDLE_W, h)
        self.is_player = is_player
        self.score = 0

    def handle_input(self, keys: set, dt: float):
        if not self.is_player:
            return
        if "w" in keys and self.y > 0:
            self.y -= PADDLE_SPEED * dt
        if "s" in keys and self.y + self.h < SCREEN_H:
            self.y += PADDLE_SPEED * dt

    def ai_follow(self, ball_y: float, dt: float):
        # IA sigue el centro de la pelota con 85% de velocidad — competente pero vencible
        center = self.y + self.h / 2
        if center < ball_y - 4:
            self.y += PADDLE_SPEED * 0.85 * dt
        elif center > ball_y + 4:
            self.y -= PADDLE_SPEED * 0.85 * dt
        self.y = max(0, min(self.y, SCREEN_H - self.h))


class Ball(MovingObject):
    # Pelota con rebote; hereda movimiento de MovingObject
    def __init__(self):
        super().__init__(SCREEN_W // 2, SCREEN_H // 2, 10, 10, vx=BALL_SPEED_DEFAULT, vy=BALL_SPEED_DEFAULT * 0.6)
        self.reset_pending = False

    def update(self, dt):
        super().update(dt)
        self.bounce_walls()

    def check_paddle_collision(self, paddle: Paddle):
        if self.get_rect().colliderect(paddle.get_rect()):
            self.vx *= -1
            # Pequeño empuje vertical según dónde golpea la paleta
            offset = (self.y + 5) - (paddle.y + paddle.h / 2)
            self.vy = offset * 4

    def check_score(self, player: Paddle, enemy: Paddle):
        # Pelota sale por la derecha: punto para el jugador
        if self.x > SCREEN_W:
            player.score += 1
            self._reset()
        # Pelota sale por la izquierda: punto para la IA
        elif self.x + self.w < 0:
            enemy.score += 1
            self._reset()

    def _reset(self):
        self.x = SCREEN_W // 2
        self.y = SCREEN_H // 2
        # Invierte dirección horizontal y reinicia vertical
        self.vx *= -1
        self.vy = abs(self.vx) * 0.6


def build(injector: LiveInjector) -> tuple:
    # Construye e inyecta los objetos de la lección al injector
    player = Paddle(20, is_player=True)
    enemy = Paddle(SCREEN_W - 20 - PADDLE_W, is_player=False)
    ball = Ball()

    injector.register("pelota", ball)
    injector.register("paleta_jugador", player)
    injector.register("paleta_enemigo", enemy)

    return player, enemy, ball


def run_frame(player: Paddle, enemy: Paddle, ball: Ball,
              keys, dt: float, surface: pygame.Surface,
              watcher: ValidationWatcher):
    surface.fill((20, 20, 20))

    player.handle_input(keys, dt)
    enemy.ai_follow(ball.y, dt)
    ball.update(dt)
    ball.check_paddle_collision(player)
    ball.check_paddle_collision(enemy)
    ball.check_score(player, enemy)

    player.draw(surface)
    enemy.draw(surface)
    ball.draw(surface)

    # Línea divisoria central
    pygame.draw.line(surface, (60, 60, 60), (SCREEN_W // 2, 0), (SCREEN_W // 2, SCREEN_H), 2)

    # Marcador
    font = pygame.font.SysFont("monospace", 28)
    surface.blit(font.render(str(player.score), True, (200, 200, 200)), (SCREEN_W // 2 - 40, 20))
    surface.blit(font.render(str(enemy.score), True, (200, 200, 200)), (SCREEN_W // 2 + 20, 20))

    # Actualizar validador con estado actual
    state = {"score": player.score, "ball_speed": abs(ball.vx), "paddle_h": player.h}
    watcher.update(state)
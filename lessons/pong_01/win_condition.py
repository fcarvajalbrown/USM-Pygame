# Condición de victoria: pelota dentro de rango jugable Y el jugador anotó al menos WIN_SCORE puntos
from lessons.pong_01.template import WIN_SCORE


def win_condition(state: dict) -> bool:
    speed_ok = 100 <= state.get("ball_speed", 0) <= 400
    size_ok = state.get("paddle_h", 0) >= 60
    score_ok = state.get("score", 0) >= WIN_SCORE
    return speed_ok and size_ok and score_ok

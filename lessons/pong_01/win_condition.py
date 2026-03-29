# Condición de victoria: velocidad y paleta calibradas Y jugador anotó WIN_SCORE puntos
from .template import WIN_SCORE


def win_condition(state: dict) -> bool:
    speed_ok = 150 <= state.get("ball_speed", 0) <= 300
    size_ok = state.get("paddle_h", 0) >= 80
    score_ok = state.get("score", 0) >= WIN_SCORE
    return speed_ok and size_ok and score_ok
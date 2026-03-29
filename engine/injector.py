# Inyector en vivo — conecta sliders de Dear PyGui con instancias Pygame en ejecución
from typing import Any


class LiveInjector:
    # Registra objetos y expone sus atributos al panel de ajuste
    def __init__(self):
        self._registry: dict[str, Any] = {}

    def register(self, name: str, obj: Any):
        # Registra un objeto bajo un nombre legible para la GUI
        self._registry[name] = obj

    def set_attr(self, name: str, attr: str, value: Any):
        # Llama setattr en el objeto registrado; usado por los sliders
        obj = self._registry.get(name)
        if obj is not None:
            setattr(obj, attr, value)

    def get_attr(self, name: str, attr: str) -> Any:
        obj = self._registry.get(name)
        if obj is not None:
            return getattr(obj, attr, None)
        return None

    def snapshot(self) -> dict:
        # Retorna estado completo de todos los objetos registrados (para X-Ray)
        result = {}
        for name, obj in self._registry.items():
            result[name] = {
                k: v for k, v in vars(obj).items()
                if not k.startswith("_") and not callable(v)
            }
        return result

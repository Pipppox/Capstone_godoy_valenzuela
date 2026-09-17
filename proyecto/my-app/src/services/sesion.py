_usuario_actual: dict | None = None


def iniciar(usuario: dict) -> None:
    global _usuario_actual
    _usuario_actual = usuario


def cerrar() -> None:
    global _usuario_actual
    _usuario_actual = None


def usuario() -> dict | None:
    return _usuario_actual


def activa() -> bool:
    return _usuario_actual is not None
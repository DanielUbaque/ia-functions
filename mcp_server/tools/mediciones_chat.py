"""Escritura de mediciones rápidas dictadas por chat, con trazabilidad de
que el dato vino del chat (no del ETL formal) — ver arquitectura.md,
funcionalidad 9. El backend todavía no expone un endpoint de escritura para
esto ni un campo de origen en su modelo de mediciones, así que estas tools
quedan declaradas (para que el contrato ya exista) pero inactivas."""

NO_DISPONIBLE = {
    "error": "No disponible: el backend no expone todavía un endpoint de "
             "escritura para mediciones registradas por chat.",
}


def proponer_guardar_medicion(sitio: str, fecha: str, variable: str,
                               valor: float, unidad: str | None = None) -> dict:
    """Prepara el registro de una medición dictada por chat, para que la
    persona la confirme antes de guardarla. No disponible todavía."""
    return NO_DISPONIBLE


def confirmar_medicion(sitio_id: int, fecha: str, variable: str,
                        valor: float, unidad: str | None = None) -> dict:
    """Guarda una medición previamente propuesta y confirmada. No disponible
    todavía."""
    return NO_DISPONIBLE

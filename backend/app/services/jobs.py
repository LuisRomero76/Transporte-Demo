"""Tareas periódicas dentro del proceso de la API."""

import asyncio
import logging

from app.core.db import SessionLocal
from app.services import comprobantes, reservas

log = logging.getLogger("transdemo.jobs")


async def expirar_reservas_periodicamente(intervalo_segundos: int) -> None:
    while True:
        try:
            async with SessionLocal() as session:
                liberadas = await reservas.expirar_vencidas(session)
            if liberadas:
                log.info("Reservas expiradas: %s", liberadas)
        except asyncio.CancelledError:
            raise
        except Exception:  # noqa: BLE001 - la tarea no debe morir por un error puntual
            log.exception("Error al expirar reservas")
        await asyncio.sleep(intervalo_segundos)


async def descargar_comprobantes_periodicamente(intervalo_segundos: int) -> None:
    """Respaldo del webhook post-llamada: guarda las imágenes de comprobantes que aún no se descargaron."""
    while True:
        await asyncio.sleep(intervalo_segundos)
        await comprobantes.descargar_imagenes_en_segundo_plano()

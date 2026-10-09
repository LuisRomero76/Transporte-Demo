"""Comprobantes de pago por QR de la compra por WhatsApp: imagen, revisión en el panel y aviso al cliente.

Flujo: el agente lee la foto del comprobante y llama a `registrar_comprobante` (servicio `compra_chat`);
la reserva queda sin plazo mientras se revisa. La imagen no viaja en la tool: se descarga de la conversación
de ElevenLabs cuando termina (webhook post-llamada, con una tarea periódica de respaldo). En el panel una
persona aprueba (se emiten los boletos) o rechaza (vuelve a correr un plazo corto); en ambos casos se avisa
al cliente por WhatsApp con una plantilla de Meta.
"""

import hashlib
import hmac
import logging
import re
import time
import uuid
from datetime import timedelta
from typing import Any

import httpx
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, undefer

from app.core.config import get_settings
from app.core.db import SessionLocal
from app.core.errors import Conflicto, NoEncontrado, ReglaNegocio
from app.models import Boleto, ComprobantePago, Ruta, Salida, Usuario, VentaPasaje
from app.models.enums import EstadoComprobante, EstadoVenta, MetodoPago
from app.schemas.ventas import PagoIn
from app.services import auditoria, parametros, reservas, whatsapp
from app.utils.fechas import a_local, ahora

log = logging.getLogger("transdemo.comprobantes")

URL_CONVERSACION = "https://api.elevenlabs.io/v1/convai/conversations/{}"
IMAGEN_MAX_BYTES = 5 * 1024 * 1024
MIMES_PERMITIDOS = ("image/jpeg", "image/png", "image/webp", "application/pdf")
MAX_INTENTOS_IMAGEN = 30
TOLERANCIA_FIRMA_SEG = 30 * 60
_UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")


def normalizar_transaccion(valor: str | None) -> str | None:
    """'18092026/295 140-726' → '18092026295140726'; así dos lecturas del mismo comprobante coinciden."""
    limpio = "".join(c for c in (valor or "").upper() if c.isalnum())
    return limpio[:80] or None


def plazo_tras_rechazo(salida: Salida, minutos: int, cierre_chat_min: int):
    """Nuevo vencimiento: `minutos` desde ahora, sin pasar el cierre de la venta por WhatsApp."""
    return min(ahora() + timedelta(minutes=minutos), salida.fecha_hora_salida - timedelta(minutes=cierre_chat_min))


# --- Imagen del comprobante (ElevenLabs) --------------------------------------------------------


def verificar_firma(cuerpo: bytes, cabecera: str | None) -> bool:
    """Valida la cabecera `ElevenLabs-Signature: t=<unix>,v0=<hmac-sha256 de "t.cuerpo">`."""
    secreto = get_settings().elevenlabs_webhook_secret
    if not secreto or not cabecera:
        return False
    partes = dict(p.split("=", 1) for p in cabecera.split(",") if "=" in p)
    try:
        momento = int(partes.get("t", ""))
    except ValueError:
        return False
    if abs(time.time() - momento) > TOLERANCIA_FIRMA_SEG:
        return False
    esperado = hmac.new(secreto.encode(), f"{momento}.".encode() + cuerpo, hashlib.sha256).hexdigest()
    return hmac.compare_digest(esperado, partes.get("v0", ""))


async def _conversacion(cliente: httpx.AsyncClient, conversation_id: str) -> dict[str, Any] | None:
    r = await cliente.get(
        URL_CONVERSACION.format(conversation_id), headers={"xi-api-key": get_settings().elevenlabs_api_key or ""}
    )
    if r.status_code != 200:
        log.warning("No se pudo leer la conversación %s (%s)", conversation_id, r.status_code)
        return None
    return r.json()


def imagenes_de(transcript: list[dict[str, Any]]) -> tuple[dict[str, dict[str, Any]], dict[str, Any] | None]:
    """Asocia a cada comprobante registrado la última imagen que envió el cliente antes de registrarlo.

    El id del comprobante viaja en la respuesta de `registrar_comprobante`, que queda en el transcript.
    Devuelve ({comprobante_id: archivo}, último archivo de la conversación).
    """
    por_id: dict[str, dict[str, Any]] = {}
    ultima: dict[str, Any] | None = None
    for turno in transcript or []:
        for archivo in turno.get("file_inputs") or ([turno["file_input"]] if turno.get("file_input") else []):
            if archivo and archivo.get("file_url"):
                ultima = archivo
        for resultado in turno.get("tool_results") or []:
            if resultado.get("tool_name") == "registrar_comprobante" and ultima:
                for comprobante_id in _UUID.findall(str(resultado.get("result_value") or "")):
                    por_id.setdefault(comprobante_id, ultima)
    return por_id, ultima


async def _descargar(cliente: httpx.AsyncClient, archivo: dict[str, Any]) -> tuple[bytes, str] | None:
    mime = (archivo.get("mime_type") or "").lower()
    if mime not in MIMES_PERMITIDOS:
        return None
    r = await cliente.get(archivo["file_url"])
    if r.status_code != 200 or not r.content or len(r.content) > IMAGEN_MAX_BYTES:
        return None
    return r.content, mime


async def descargar_imagenes(session: AsyncSession, conversation_id: str | None = None) -> int:
    """Descarga las imágenes de los comprobantes en revisión que aún no la tienen. Devuelve cuántas guardó.

    Con `conversation_id` (webhook) solo revisa esa conversación; sin él (tarea periódica) revisa todas.
    Las conversaciones que siguen abiertas se reintentan después.
    """
    if not get_settings().elevenlabs_api_key:
        return 0
    q = select(ComprobantePago).where(
        ComprobantePago.estado == EstadoComprobante.en_revision,
        ComprobantePago.imagen_obtenida_at.is_(None),
        ComprobantePago.conversation_id.is_not(None),
        ComprobantePago.intentos_imagen < MAX_INTENTOS_IMAGEN,
    )
    if conversation_id:
        q = q.where(ComprobantePago.conversation_id == conversation_id)
    pendientes = (await session.scalars(q.with_for_update(skip_locked=True))).all()
    if not pendientes:
        return 0

    por_conversacion: dict[str, list[ComprobantePago]] = {}
    for c in pendientes:
        por_conversacion.setdefault(c.conversation_id or "", []).append(c)

    guardadas = 0
    async with httpx.AsyncClient(timeout=30) as cliente:
        for conv_id, comprobantes in por_conversacion.items():
            for c in comprobantes:
                c.intentos_imagen += 1
            datos = await _conversacion(cliente, conv_id)
            if not datos or datos.get("status") != "done":
                continue  # sigue abierta: la imagen aún no está en el transcript
            por_id, ultima = imagenes_de(datos.get("transcript") or [])
            for c in comprobantes:
                archivo = por_id.get(str(c.id)) or ultima
                descarga = await _descargar(cliente, archivo) if archivo else None
                if descarga:
                    c.imagen, c.imagen_mime = descarga
                    c.imagen_obtenida_at = ahora()
                    guardadas += 1
    await session.commit()
    return guardadas


async def descargar_imagenes_en_segundo_plano(conversation_id: str | None = None) -> None:
    try:
        async with SessionLocal() as session:
            n = await descargar_imagenes(session, conversation_id)
        if n:
            log.info("Imágenes de comprobantes guardadas: %s", n)
    except Exception:  # noqa: BLE001 - se reintenta en la siguiente pasada
        log.exception("Error al descargar imágenes de comprobantes")


# --- Panel ------------------------------------------------------------------------------------------


def _opciones():
    salida = selectinload(ComprobantePago.venta).selectinload(VentaPasaje.boletos).selectinload(Boleto.salida)
    return (
        selectinload(ComprobantePago.venta).selectinload(VentaPasaje.comprador),
        salida.selectinload(Salida.ruta).selectinload(Ruta.origen),
        salida.selectinload(Salida.ruta).selectinload(Ruta.destino),
    )


async def listar(
    session: AsyncSession, *, estado: EstadoComprobante | None, limit: int, offset: int
) -> tuple[int, list[dict[str, Any]]]:
    q = select(ComprobantePago)
    if estado:
        q = q.where(ComprobantePago.estado == estado)
    total = await session.scalar(select(func.count()).select_from(q.subquery()))
    orden = (
        ComprobantePago.created_at.asc()
        if estado == EstadoComprobante.en_revision
        else ComprobantePago.created_at.desc()
    )
    filas = (await session.scalars(q.options(*_opciones()).order_by(orden).limit(limit).offset(offset))).all()

    numeros = {c.numero_transaccion for c in filas if c.numero_transaccion}
    repetidos: set[str] = set()
    if numeros:
        # Repetido: el número aparece en otra reserva (reenviar el propio tras un rechazo no cuenta).
        repetidos = set(
            (
                await session.scalars(
                    select(ComprobantePago.numero_transaccion)
                    .where(ComprobantePago.numero_transaccion.in_(numeros))
                    .group_by(ComprobantePago.numero_transaccion)
                    .having(func.count(func.distinct(ComprobantePago.venta_id)) > 1)
                )
            ).all()
        )
    return total or 0, [a_respuesta(c, c.numero_transaccion in repetidos) for c in filas]


def a_respuesta(c: ComprobantePago, transaccion_repetida: bool = False) -> dict[str, Any]:
    venta = c.venta
    salida = venta.boletos[0].salida if venta.boletos else None
    horas = (salida.fecha_hora_salida - ahora()).total_seconds() / 3600 if salida else None
    return {
        "id": c.id,
        "estado": c.estado,
        "codigo_reserva": venta.codigo_reserva,
        "estado_reserva": venta.estado,
        "comprador": venta.comprador.nombre_completo,
        "telefono": c.caller_id,
        "total_bs": venta.total_bs,
        "monto_leido_bs": c.monto_leido_bs,
        "monto_coincide": c.monto_leido_bs is not None and c.monto_leido_bs == venta.total_bs,
        "fecha_leida": c.fecha_leida,
        "numero_transaccion": c.numero_transaccion,
        "transaccion_repetida": transaccion_repetida,
        "banco": c.banco,
        "cuenta_destino": c.cuenta_destino,
        "tiene_imagen": c.imagen_obtenida_at is not None,
        "viaje": f"{salida.ruta.origen.nombre} → {salida.ruta.destino.nombre}" if salida else None,
        "fecha_hora_salida": salida.fecha_hora_salida if salida else None,
        "boletos": len(venta.boletos),
        "salida_proxima": horas is not None and horas < 6,
        "motivo_rechazo": c.motivo_rechazo,
        "revisado_at": c.revisado_at,
        "notificado_at": c.notificado_at,
        "notificacion_error": c.notificacion_error,
        "created_at": c.created_at,
    }


async def obtener(session: AsyncSession, comprobante_id: uuid.UUID, *, bloquear: bool = False) -> ComprobantePago:
    q = select(ComprobantePago).where(ComprobantePago.id == comprobante_id).options(*_opciones())
    if bloquear:
        q = q.with_for_update(of=ComprobantePago)
    c = await session.scalar(q.execution_options(populate_existing=True))
    if not c:
        raise NoEncontrado("No existe ese comprobante.", codigo="comprobante_no_encontrado")
    return c


async def imagen(session: AsyncSession, comprobante_id: uuid.UUID) -> tuple[bytes, str]:
    c = await session.scalar(
        select(ComprobantePago).where(ComprobantePago.id == comprobante_id).options(undefer(ComprobantePago.imagen))
    )
    if not c:
        raise NoEncontrado("No existe ese comprobante.", codigo="comprobante_no_encontrado")
    if not c.imagen:
        raise NoEncontrado(
            "La imagen todavía no está disponible. Llega unos segundos después de que termina el chat.",
            codigo="imagen_pendiente",
        )
    return c.imagen, c.imagen_mime or "image/jpeg"


def _en_revision(c: ComprobantePago) -> None:
    if c.estado != EstadoComprobante.en_revision:
        raise Conflicto(f"Este comprobante ya fue {c.estado}.", codigo="comprobante_ya_revisado")


async def aprobar(session: AsyncSession, comprobante_id: uuid.UUID, usuario: Usuario) -> ComprobantePago:
    c = await obtener(session, comprobante_id, bloquear=True)
    _en_revision(c)
    if c.venta.estado != EstadoVenta.pendiente_pago:
        raise ReglaNegocio(reservas.mensaje_reserva(c.venta), codigo="reserva_no_pagable")
    c.estado = EstadoComprobante.aprobado
    c.revisado_por_usuario_id = usuario.id
    c.revisado_at = ahora()
    auditoria.registrar(session, usuario, "comprobante.aprobar", "comprobantes_pago", c.id)
    # `pagar` confirma la transacción junto con el cambio del comprobante.
    await reservas.pagar(
        session,
        c.venta.codigo_reserva,
        PagoIn(metodo=MetodoPago.qr),
        usuario=usuario,
        proveedor="qr_whatsapp",
        transaccion_externa_id=c.numero_transaccion,
    )
    return await obtener(session, c.id)


async def rechazar(session: AsyncSession, comprobante_id: uuid.UUID, motivo: str, usuario: Usuario) -> ComprobantePago:
    c = await obtener(session, comprobante_id, bloquear=True)
    _en_revision(c)
    c.estado = EstadoComprobante.rechazado
    c.motivo_rechazo = motivo.strip()
    c.revisado_por_usuario_id = usuario.id
    c.revisado_at = ahora()
    venta = c.venta
    if venta.estado == EstadoVenta.pendiente_pago and venta.boletos:
        venta.expira_at = plazo_tras_rechazo(
            venta.boletos[0].salida,
            await parametros.obtener_int(session, "comprobante_rechazo_plazo_minutos"),
            await parametros.obtener_int(session, "venta_chat_cierre_minutos_antes"),
        )
    auditoria.registrar(
        session, usuario, "comprobante.rechazar", "comprobantes_pago", c.id, {"motivo": c.motivo_rechazo}
    )
    await session.commit()
    return await obtener(session, c.id)


# --- Aviso al cliente por WhatsApp ------------------------------------------------------------------


def _parametros_aviso(c: ComprobantePago) -> tuple[str, list[str]]:
    s = get_settings()
    venta = c.venta
    nombre = venta.comprador.nombres.split()[0]
    if c.estado == EstadoComprobante.aprobado:
        salida = venta.boletos[0].salida
        return s.whatsapp_plantilla_compra_confirmada, [
            nombre,
            venta.codigo_reserva,
            f"{salida.ruta.origen.nombre} a {salida.ruta.destino.nombre}",
            f"{a_local(salida.fecha_hora_salida):%d/%m %H:%M}",
        ]
    motivo = c.motivo_rechazo or "el comprobante no es válido"
    if venta.estado == EstadoVenta.pendiente_pago and venta.expira_at and venta.expira_at > ahora():
        motivo += f". Tienes hasta las {a_local(venta.expira_at):%H:%M}"
    return s.whatsapp_plantilla_pago_rechazado, [nombre, venta.codigo_reserva, motivo]


async def avisar_cliente(comprobante_id: uuid.UUID) -> None:
    """Envía la plantilla de WhatsApp según el resultado de la revisión y deja constancia del envío."""
    async with SessionLocal() as session:
        c = await obtener(session, comprobante_id)
        if not c.caller_id:
            return
        plantilla, params = _parametros_aviso(c)
        try:
            await whatsapp.enviar_plantilla(c.caller_id, plantilla, params)
            c.notificado_at = ahora()
            c.notificacion_error = None
        except Exception as exc:  # noqa: BLE001 - el resultado de la revisión no depende del aviso
            log.warning("No se pudo avisar por WhatsApp del comprobante %s: %s", c.id, exc)
            c.notificacion_error = str(exc)[:300]
        await session.commit()

"""Compra de pasajes por WhatsApp (tools del agente): asientos libres, reserva y comprobante de pago por QR.

Seguridad contra compras duplicadas (por ejemplo, el mismo cliente escribiendo desde dos chats):
- La salida se bloquea (`SELECT … FOR UPDATE`) antes de validar: las compras sobre un mismo viaje se
  procesan de a una, y el índice único de asientos activos impide vender dos veces un asiento.
- Un número de WhatsApp tiene como máximo una reserva pendiente por salida; si el agente repite la
  llamada, se devuelve la misma reserva (idempotente) en vez de crear otra.
- Un carnet no puede tener dos pasajes activos en la misma salida.
- Cada número puede tener pocas reservas pendientes a la vez (`reservas_chat_pendientes_max`).
- La reserva solo se crea con la confirmación explícita del cliente (`confirmado`).
- El teléfono lo inyecta ElevenLabs (`system__caller_id`); el modelo no puede elegirlo.
- Un número de transacción no se acepta en dos comprobantes (índice único).
"""

import re
from datetime import timedelta
from decimal import Decimal, InvalidOperation
from typing import Any

from pydantic import BaseModel, Field, ValidationError
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.core.errors import Conflicto, NoEncontrado, ReglaNegocio
from app.models import Boleto, Cliente, ComprobantePago, Salida, VentaPasaje
from app.models.enums import BOLETO_ACTIVO, CanalVenta, EstadoComprobante, EstadoVenta
from app.schemas.ventas import CompradorIn, PasajeroIn, ReservaIn
from app.services import catalogos, parametros, reservas, salidas
from app.services.bot import caller, cuando, dinero, hora, interpretar_bool, lista
from app.services.comprobantes import normalizar_transaccion
from app.utils.fechas import ahora
from app.utils.texto import normalizar

MAX_ASIENTOS_MOSTRADOS = 12


def enlace_pago(codigo: str) -> str:
    return f"{get_settings().web_publica_url.rstrip('/')}/pagar/{codigo}"


async def _salida(session: AsyncSession, codigo_salida: str | None, *, bloquear: bool = False) -> Salida:
    if not codigo_salida or not codigo_salida.strip():
        raise ReglaNegocio("Primero busca la salida con consultar_salidas y usa su código.", codigo="salida_requerida")
    salida_id = await session.scalar(select(Salida.id).where(Salida.codigo == codigo_salida.strip().upper()))
    if not salida_id:
        raise NoEncontrado("No encontré esa salida. Vuelve a consultar los horarios.", codigo="salida_no_encontrada")
    return await salidas.obtener(session, salida_id, bloquear=bloquear)


async def _verificar_venta_chat(session: AsyncSession, salida: Salida) -> None:
    cierre_chat = await parametros.obtener_int(session, "venta_chat_cierre_minutos_antes")
    _, max_dias = await salidas.ventana_de_venta(session)
    if not salidas.es_vendible(salida.estado, salida.fecha_hora_salida, cierre_chat, max_dias):
        horas = cierre_chat // 60
        raise ReglaNegocio(
            f"Por este chat vendemos hasta {horas} horas antes de la salida. Para este viaje puedes comprar "
            "en transdemo.com o en nuestras boleterías.",
            codigo="venta_chat_cerrada",
        )


def _clase(texto: str | None, tipos: list) -> Any | None:
    """'suite', 'arriba', 'leito', 'abajo' → tipo de asiento."""
    t = normalizar(texto or "")
    if not t:
        return None
    for tipo in tipos:
        nombre = normalizar(tipo.nombre)
        if t in nombre or nombre.split()[0] in t or normalizar(tipo.codigo) == t.replace(" ", "_"):
            return tipo
        if (t in ("arriba", "planta alta", "piso de arriba", "segundo piso") and tipo.planta == "alta") or (
            t in ("abajo", "planta baja", "piso de abajo", "primer piso") and tipo.planta == "baja"
        ):
            return tipo
    return None


# --- ver_asientos ----------------------------------------------------------------------------------


async def ver_asientos(session: AsyncSession, codigo_salida: str | None, clase: str | None) -> dict[str, Any]:
    salida = await _salida(session, codigo_salida)
    await _verificar_venta_chat(session, salida)
    mapa = await salidas.mapa_asientos(session, salida.id)
    tipos = await catalogos.listar_tipos_asiento(session)
    elegido = _clase(clase, tipos)
    clases = []
    for tipo in tipos:
        if elegido and tipo.id != elegido.id:
            continue
        libres = sorted(
            a["numero"] for a in mapa["asientos"] if a["estado"] == "libre" and a["tipo_asiento"] == tipo.codigo
        )
        clases.append(
            {
                "clase": tipo.nombre,
                "piso": "arriba" if tipo.planta == "alta" else "abajo",
                "libres": len(libres),
                "asientos": libres[:MAX_ASIENTOS_MOSTRADOS],
            }
        )
    partes = [
        f"en {c['clase']} (piso de {c['piso']}) "
        + (
            f"están libres los asientos {lista([str(n) for n in c['asientos']])}"
            if c["libres"]
            else "no quedan asientos"
        )
        + (f" y {c['libres'] - len(c['asientos'])} más" if c["libres"] > len(c["asientos"]) else "")
        for c in clases
    ]
    return {
        "encontrado": True,
        "codigo_salida": salida.codigo,
        "clases": clases,
        "mensaje": f"Para la salida {cuando(salida.fecha_hora_salida)}, " + "; ".join(partes) + ".",
    }


# --- crear_reserva_chat ----------------------------------------------------------------------------


class BotPasajeroIn(BaseModel):
    numero_documento: str | None = None
    nombres: str | None = None
    apellidos: str | None = None
    numero_asiento: int | str | None = None


class BotReservaIn(BaseModel):
    caller_id: str | None = None
    codigo_salida: str | None = None
    clase: str | None = Field(None, description="Suite Cama o Leito Cama; obligatoria si no se eligen asientos")
    pasajeros: list[BotPasajeroIn] = Field(default_factory=list)
    confirmado: bool | str | None = None


async def _pendientes_del_numero(session: AsyncSession, telefono: str) -> list[VentaPasaje]:
    return list(
        (
            await session.scalars(
                select(VentaPasaje)
                .join(Cliente, Cliente.id == VentaPasaje.comprador_cliente_id)
                .where(
                    VentaPasaje.canal == CanalVenta.whatsapp_chat,
                    VentaPasaje.estado == EstadoVenta.pendiente_pago,
                    Cliente.telefono_e164 == telefono,
                    (VentaPasaje.expira_at.is_(None)) | (VentaPasaje.expira_at > ahora()),
                )
                .options(selectinload(VentaPasaje.boletos))
                .order_by(VentaPasaje.created_at)
            )
        ).all()
    )


def _asiento(valor: int | str | None) -> int | None:
    if valor is None:
        return None
    m = re.search(r"\d+", str(valor))
    return int(m[0]) if m else None


def _respuesta_reserva(venta: VentaPasaje, *, nueva: bool) -> dict[str, Any]:
    salida = venta.boletos[0].salida
    asientos = lista([str(b.numero_asiento) for b in venta.boletos])
    enlace = enlace_pago(venta.codigo_reserva)
    inicio = "Listo, reservé" if nueva else "Ya tienes reservados"
    plural = len(venta.boletos) != 1
    mensaje = (
        f"{inicio} {'los asientos' if plural else 'el asiento'} {asientos} de {salida.ruta.origen.nombre} a "
        f"{salida.ruta.destino.nombre} {cuando(salida.fecha_hora_salida)}. Código de reserva {venta.codigo_reserva}, "
        f"total {dinero(venta.total_bs)}. "
    )
    if venta.expira_at is None:
        mensaje += "Tu comprobante de pago está en revisión; te avisaremos por este chat."
    else:
        mensaje += (
            f"Paga con el QR de este enlace antes de las {hora(venta.expira_at)}: {enlace} . "
            "Cuando pagues, envíame la foto del comprobante por este chat."
        )
    return {
        "encontrado": True,
        "codigo_reserva": venta.codigo_reserva,
        "total_bs": float(venta.total_bs),
        "asientos": [b.numero_asiento for b in venta.boletos],
        "paga_hasta": hora(venta.expira_at) if venta.expira_at else None,
        "enlace_pago": enlace,
        "mensaje": mensaje,
        "_coincide": True,
    }


async def crear_reserva(session: AsyncSession, datos: BotReservaIn) -> dict[str, Any]:
    telefono = caller(datos.caller_id)
    if not telefono:
        raise ReglaNegocio(
            "No pude identificar tu número de WhatsApp. Escríbenos desde tu celular para reservar.",
            codigo="sin_caller",
        )
    if not interpretar_bool(datos.confirmado):
        raise ReglaNegocio(
            "Antes de reservar, muestra al cliente el resumen (salida, pasajeros, asientos y total) y pide que "
            "confirme con un sí.",
            codigo="falta_confirmacion",
        )
    if not datos.pasajeros:
        raise ReglaNegocio("¿Para cuántas personas es el pasaje y cuáles son sus datos?", codigo="datos_incompletos")
    maximo = await parametros.obtener_int(session, "boletos_max_por_venta")
    if len(datos.pasajeros) > maximo:
        raise ReglaNegocio(
            f"Por reserva se pueden comprar como máximo {maximo} pasajes.", codigo="demasiados_pasajeros"
        )
    for i, p in enumerate(datos.pasajeros, start=1):
        faltan = [
            etiqueta
            for campo, etiqueta in (
                ("numero_documento", "el carnet"),
                ("nombres", "el nombre"),
                ("apellidos", "el apellido"),
            )
            if not (getattr(p, campo) or "").strip()
        ]
        if faltan:
            quien = "del pasajero" if len(datos.pasajeros) == 1 else f"del pasajero {i}"
            raise ReglaNegocio(f"Me falta {lista(faltan)} {quien}.", codigo="datos_incompletos")
    documentos = [p.numero_documento.strip().upper() for p in datos.pasajeros]  # type: ignore[union-attr]
    if len(set(documentos)) != len(documentos):
        raise ReglaNegocio("Hay dos pasajeros con el mismo carnet. Revisa los datos.", codigo="documento_repetido")

    # Bloquea la salida: a partir de aquí las compras sobre este viaje se procesan de a una.
    salida = await _salida(session, datos.codigo_salida, bloquear=True)
    await _verificar_venta_chat(session, salida)

    pendientes = await _pendientes_del_numero(session, telefono)
    misma_salida = [v for v in pendientes if v.boletos and v.boletos[0].salida_id == salida.id]
    if misma_salida:
        # Reintento o segundo chat del mismo número: se devuelve la reserva existente.
        return _respuesta_reserva(await reservas.obtener(session, misma_salida[0].codigo_reserva), nueva=False)
    max_pendientes = await parametros.obtener_int(session, "reservas_chat_pendientes_max")
    if len(pendientes) >= max_pendientes:
        codigos = lista([v.codigo_reserva for v in pendientes])
        raise ReglaNegocio(
            f"Ya tienes {len(pendientes)} reservas pendientes de pago ({codigos}). Págalas o espera a que venzan "
            "antes de hacer otra.",
            codigo="demasiadas_pendientes",
        )

    con_pasaje = (
        await session.scalars(
            select(Cliente.numero_documento)
            .join(Boleto, Boleto.pasajero_cliente_id == Cliente.id)
            .where(
                Boleto.salida_id == salida.id,
                Boleto.estado.in_(BOLETO_ACTIVO),
                Cliente.numero_documento.in_(documentos),
            )
        )
    ).all()
    if con_pasaje:
        raise Conflicto(
            f"El carnet {lista(sorted(set(con_pasaje)))} ya tiene pasaje en esta salida.", codigo="pasajero_con_pasaje"
        )

    # Asientos: los elegidos o los primeros libres de la clase pedida.
    mapa = await salidas.mapa_asientos(session, salida.id)
    tipos = await catalogos.listar_tipos_asiento(session)
    elegidos = [_asiento(p.numero_asiento) for p in datos.pasajeros]
    if any(n is None for n in elegidos):
        tipo = _clase(datos.clase, tipos)
        if not tipo:
            raise ReglaNegocio(
                "¿Prefieres Suite Cama (piso de arriba) o Leito Cama (piso de abajo)?", codigo="clase_requerida"
            )
        tomados = {n for n in elegidos if n is not None}
        libres = [
            a["numero"]
            for a in sorted(mapa["asientos"], key=lambda a: a["numero"])
            if a["estado"] == "libre" and a["tipo_asiento"] == tipo.codigo and a["numero"] not in tomados
        ]
        if len(libres) < elegidos.count(None):
            raise Conflicto(f"No quedan suficientes asientos en {tipo.nombre}.", codigo="sin_asientos")
        libres_iter = iter(libres)
        elegidos = [n if n is not None else next(libres_iter) for n in elegidos]
    if len(set(elegidos)) != len(elegidos):
        raise ReglaNegocio(
            "Hay asientos repetidos. Elige un asiento distinto para cada pasajero.", codigo="asiento_repetido"
        )

    try:
        reserva_in = ReservaIn(
            salida_id=salida.id,
            comprador=CompradorIn(
                numero_documento=datos.pasajeros[0].numero_documento or "",
                nombres=datos.pasajeros[0].nombres or "",
                apellidos=datos.pasajeros[0].apellidos or "",
                telefono=telefono,
            ),
            pasajeros=[
                PasajeroIn(
                    numero_documento=p.numero_documento or "",
                    nombres=p.nombres or "",
                    apellidos=p.apellidos or "",
                    numero_asiento=n,
                )
                for p, n in zip(datos.pasajeros, elegidos, strict=True)
            ],
        )
    except ValidationError as exc:
        campo = str(exc.errors()[0]["loc"][-1])
        etiquetas = {"numero_documento": "el carnet", "nombres": "el nombre", "apellidos": "el apellido"}
        raise ReglaNegocio(f"Revisa {etiquetas.get(campo, campo)}: no parece válido.", codigo="dato_invalido") from exc

    plazo = await parametros.obtener_int(session, "reserva_chat_expira_minutos")
    cierre_chat = await parametros.obtener_int(session, "venta_chat_cierre_minutos_antes")
    expira_at = min(ahora() + timedelta(minutes=plazo), salida.fecha_hora_salida - timedelta(minutes=cierre_chat))
    venta = await reservas.crear_reserva(session, reserva_in, canal=CanalVenta.whatsapp_chat, expira_at=expira_at)
    return _respuesta_reserva(venta, nueva=True)


# --- registrar_comprobante -------------------------------------------------------------------------


class BotComprobanteIn(BaseModel):
    caller_id: str | None = None
    conversation_id: str | None = None
    codigo_reserva: str | None = None
    es_comprobante: bool | str | None = Field(None, description="false si la imagen no es un comprobante de pago")
    monto: str | float | None = None
    fecha: str | None = None
    numero_transaccion: str | None = None
    banco: str | None = None
    cuenta_destino: str | None = None


def _monto(valor: str | float | None) -> Decimal | None:
    """'Bs. 27,000.00' → 27000.00; '360,50' → 360.50."""
    if valor is None:
        return None
    # Solo dígitos y separadores, sin los puntos sueltos de "Bs." ni de un punto final.
    texto = re.sub(r"[^\d.,]", "", str(valor)).strip(".,")
    if not texto:
        return None
    if "," in texto and "." in texto:
        texto = (
            texto.replace(",", "") if texto.rfind(".") > texto.rfind(",") else texto.replace(".", "").replace(",", ".")
        )
    elif "," in texto:
        entero, _, dec = texto.rpartition(",")
        texto = f"{entero.replace(',', '')}.{dec}" if len(dec) <= 2 else texto.replace(",", "")
    elif texto.count(".") > 1 or (texto.count(".") == 1 and len(texto.rpartition(".")[2]) == 3):
        texto = texto.replace(".", "")  # '1.500' o '27.000.000': separador de miles
    try:
        return Decimal(texto).quantize(Decimal("0.01"))
    except InvalidOperation:
        return None


async def registrar_comprobante(session: AsyncSession, datos: BotComprobanteIn) -> dict[str, Any]:
    telefono = caller(datos.caller_id)
    if not telefono:
        raise ReglaNegocio("No pude identificar tu número de WhatsApp.", codigo="sin_caller")

    if datos.codigo_reserva and datos.codigo_reserva.strip():
        venta = await reservas.obtener(session, datos.codigo_reserva)
        if venta.comprador.telefono_e164 != telefono:
            raise NoEncontrado(
                f"No encontré la reserva {venta.codigo_reserva} hecha desde tu número.", codigo="reserva_no_encontrada"
            )
    else:
        pendientes = await _pendientes_del_numero(session, telefono)
        if not pendientes:
            raise NoEncontrado("No tienes reservas pendientes de pago desde este número.", codigo="sin_pendientes")
        if len(pendientes) > 1:
            raise ReglaNegocio(
                f"Tienes {len(pendientes)} reservas pendientes ({lista([v.codigo_reserva for v in pendientes])}). "
                "¿De cuál es este comprobante?",
                codigo="reserva_requerida",
            )
        venta = await reservas.obtener(session, pendientes[0].codigo_reserva)

    if venta.estado != EstadoVenta.pendiente_pago:
        raise ReglaNegocio(reservas.mensaje_reserva(venta), codigo="reserva_no_pagable")
    if venta.expira_at is None:
        raise Conflicto(
            f"Ya recibimos el comprobante de la reserva {venta.codigo_reserva} y está en revisión. Te avisaremos por "
            "este chat.",
            codigo="comprobante_en_revision",
        )
    if datos.es_comprobante is not None and not interpretar_bool(datos.es_comprobante):
        raise ReglaNegocio(
            "La imagen enviada no corresponde a un comprobante de pago. Envíame la captura del pago realizado con "
            "el QR, donde se vea el monto y el número de transacción.",
            codigo="no_es_comprobante",
        )
    monto = _monto(datos.monto)
    if monto is None:
        raise ReglaNegocio(
            "No pude leer el monto en la imagen. Envíame una captura más clara del comprobante.",
            codigo="monto_ilegible",
        )
    if monto != venta.total_bs:
        raise ReglaNegocio(
            f"El comprobante es por {dinero(monto)}, pero el total de la reserva {venta.codigo_reserva} es "
            f"{dinero(venta.total_bs)}. Envíame el comprobante correcto.",
            codigo="monto_no_coincide",
        )
    numero = normalizar_transaccion(datos.numero_transaccion)
    if numero:
        usado = await session.scalar(
            select(func.count()).where(
                ComprobantePago.numero_transaccion == numero, ComprobantePago.estado != EstadoComprobante.rechazado
            )
        )
        if usado:
            raise Conflicto(
                "Ese comprobante ya fue usado para otra reserva. Envíame el comprobante de este pago.",
                codigo="comprobante_repetido",
            )

    comprobante = ComprobantePago(
        venta_id=venta.id,
        caller_id=telefono,
        conversation_id=(datos.conversation_id or "").strip()[:64] or None,
        monto_leido_bs=monto,
        fecha_leida=(datos.fecha or "").strip()[:40] or None,
        numero_transaccion=numero,
        banco=(datos.banco or "").strip()[:60] or None,
        cuenta_destino=(datos.cuenta_destino or "").strip()[:80] or None,
    )
    session.add(comprobante)
    venta.expira_at = None  # en revisión la reserva no vence
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        if "numero_transaccion" in str(exc.orig):
            raise Conflicto("Ese comprobante ya fue usado para otra reserva.", codigo="comprobante_repetido") from exc
        raise Conflicto(
            "Ya recibimos un comprobante para esta reserva y está en revisión.", codigo="comprobante_en_revision"
        ) from exc
    return {
        "encontrado": True,
        "comprobante_id": str(comprobante.id),
        "codigo_reserva": venta.codigo_reserva,
        "terminar_conversacion": True,
        "mensaje": (
            f"Recibí tu comprobante de {dinero(monto)} para la reserva {venta.codigo_reserva}. Lo estamos revisando "
            "y te avisaremos por este chat cuando se confirme tu compra."
        ),
        "_coincide": True,
    }

from fastapi import APIRouter, Depends, Query, status

from app.core.deps import SessionDep
from app.core.ratelimit import limitar
from app.models.enums import CanalVenta, EstadoVenta
from app.schemas.admin import ReembolsoIn, ReembolsoOut
from app.schemas.ventas import PagoIn, PagoQrOut, ReservaIn, ReservaOut
from app.services import reembolsos, reservas

# 40 solicitudes por minuto e IP: evita adivinar códigos de reserva o documentos.
router = APIRouter(tags=["Reservas y pasajes"], dependencies=[Depends(limitar("reservas", 40, 60))])

_DOCUMENTO = Query(description="Documento del comprador o de un pasajero (protege los datos de la reserva)")


@router.post(
    "/reservas",
    response_model=ReservaOut,
    status_code=status.HTTP_201_CREATED,
    summary="Reservar asientos (queda pendiente de pago)",
    description=(
        "Bloquea los asientos por `reserva_expira_minutos` (15 por defecto). En línea solo se venden tarifas "
        "de adulto y embarazada; menores, adultos mayores y personas con discapacidad compran en boletería."
    ),
)
async def crear(session: SessionDep, datos: ReservaIn):
    venta = await reservas.crear_reserva(session, datos, canal=CanalVenta.web)
    return await reservas.a_respuesta(session, venta)


@router.get("/reservas/{codigo}", response_model=ReservaOut, summary="Consultar una reserva")
async def consultar(session: SessionDep, codigo: str, documento: str = _DOCUMENTO):
    venta = await reservas.obtener(session, codigo, documento=documento)
    return await reservas.a_respuesta(session, venta)


@router.get(
    "/reservas/{codigo}/pago-qr",
    response_model=PagoQrOut,
    summary="QR de pago de una reserva hecha por WhatsApp (sin datos personales)",
)
async def pago_qr(session: SessionDep, codigo: str):
    venta = await reservas.obtener(session, codigo)
    salida = venta.boletos[0].salida
    pendiente = venta.estado == EstadoVenta.pendiente_pago
    return {
        "codigo_reserva": venta.codigo_reserva,
        "estado": venta.estado,
        "en_revision": pendiente and venta.expira_at is None,
        "total_bs": venta.total_bs,
        "expira_at": venta.expira_at if pendiente else None,
        "origen": salida.ruta.origen.nombre,
        "destino": salida.ruta.destino.nombre,
        "fecha_hora_salida": salida.fecha_hora_salida,
        "boletos": len(venta.boletos),
        "qr_payload": reservas.qr_payload(venta) if pendiente and venta.expira_at else None,
    }


@router.post(
    "/reservas/{codigo}/pagar",
    response_model=ReservaOut,
    summary="Pagar una reserva (pago simulado)",
    description="QR, tarjeta de débito o crédito y Tigo Money. Una tarjeta terminada en 0002 simula un rechazo.",
)
async def pagar(session: SessionDep, codigo: str, datos: PagoIn):
    venta = await reservas.pagar(session, codigo, datos)
    return await reservas.a_respuesta(session, venta)


@router.post("/reservas/{codigo}/cancelar", response_model=ReservaOut, summary="Cancelar una reserva sin pagar")
async def cancelar(session: SessionDep, codigo: str, documento: str = _DOCUMENTO):
    venta = await reservas.cancelar(session, codigo, documento=documento)
    return await reservas.a_respuesta(session, venta)


@router.post(
    "/boletos/{numero_boleto}/reembolso",
    response_model=ReembolsoOut,
    status_code=status.HTTP_201_CREATED,
    summary="Solicitar el reembolso de un boleto (85 %, hasta 2 h antes)",
)
async def reembolso(session: SessionDep, numero_boleto: str, datos: ReembolsoIn):
    r = await reembolsos.solicitar(session, numero_boleto, datos.motivo, documento=datos.documento)
    return (await reembolsos.con_detalle(session, [r]))[0]

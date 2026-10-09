"""Comprobantes de pago por QR de la compra por WhatsApp: revisión, aprobación y rechazo."""

import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, Response

from app.core.deps import PaginacionDep, SessionDep, requiere_roles
from app.models import Usuario
from app.models.enums import EstadoComprobante, RolUsuario
from app.schemas.admin import ComprobanteOut, RechazarComprobanteIn
from app.schemas.common import Pagina
from app.services import comprobantes

R = RolUsuario
router = APIRouter(prefix="/comprobantes", tags=["Admin · Pagos por WhatsApp"])
_revisar = Depends(requiere_roles(R.boletero, R.supervisor))


@router.get(
    "", response_model=Pagina[ComprobanteOut], summary="Listar comprobantes (por revisar: más antiguos primero)"
)
async def listar(
    session: SessionDep, pag: PaginacionDep, estado: EstadoComprobante | None = None, _: Usuario = _revisar
):
    total, items = await comprobantes.listar(session, estado=estado, limit=pag.limit, offset=pag.offset)
    return {"total": total, "limit": pag.limit, "offset": pag.offset, "items": items}


@router.get(
    "/{comprobante_id}/imagen",
    response_class=Response,
    responses={200: {"content": {"image/jpeg": {}, "image/png": {}, "application/pdf": {}}}},
    summary="Imagen del comprobante enviada por el cliente",
)
async def imagen(session: SessionDep, comprobante_id: uuid.UUID, _: Usuario = _revisar):
    contenido, mime = await comprobantes.imagen(session, comprobante_id)
    return Response(content=contenido, media_type=mime, headers={"Cache-Control": "private, max-age=3600"})


@router.post(
    "/{comprobante_id}/aprobar",
    response_model=ComprobanteOut,
    summary="Aprobar: emite los boletos y avisa al cliente por WhatsApp",
)
async def aprobar(session: SessionDep, comprobante_id: uuid.UUID, tareas: BackgroundTasks, usuario: Usuario = _revisar):
    c = await comprobantes.aprobar(session, comprobante_id, usuario)
    tareas.add_task(comprobantes.avisar_cliente, c.id)
    return comprobantes.a_respuesta(c)


@router.post(
    "/{comprobante_id}/rechazar",
    response_model=ComprobanteOut,
    summary="Rechazar: el cliente recibe el motivo y un plazo corto para enviar otro comprobante",
)
async def rechazar(
    session: SessionDep,
    comprobante_id: uuid.UUID,
    datos: RechazarComprobanteIn,
    tareas: BackgroundTasks,
    usuario: Usuario = _revisar,
):
    c = await comprobantes.rechazar(session, comprobante_id, datos.motivo, usuario)
    tareas.add_task(comprobantes.avisar_cliente, c.id)
    return comprobantes.a_respuesta(c)

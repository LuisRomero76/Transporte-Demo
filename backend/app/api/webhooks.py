"""Webhooks entrantes. ElevenLabs avisa al terminar cada conversación (post-call): es el momento en que
la imagen del comprobante de pago ya está disponible para descargarla."""

import json
import logging

from fastapi import APIRouter, BackgroundTasks, Request
from fastapi.responses import JSONResponse

from app.services import comprobantes

log = logging.getLogger("transdemo.webhooks")
router = APIRouter(prefix="/api/webhooks", tags=["Webhooks"], include_in_schema=False)


@router.post("/elevenlabs")
async def elevenlabs(request: Request, tareas: BackgroundTasks):
    cuerpo = await request.body()
    if not comprobantes.verificar_firma(cuerpo, request.headers.get("elevenlabs-signature")):
        return JSONResponse(status_code=401, content={"error": "firma_invalida"})
    try:
        evento = json.loads(cuerpo)
    except ValueError:
        return JSONResponse(status_code=400, content={"error": "json_invalido"})
    conversation_id = (evento.get("data") or {}).get("conversation_id")
    if evento.get("type") == "post_call_transcription" and conversation_id:
        tareas.add_task(comprobantes.descargar_imagenes_en_segundo_plano, conversation_id)
    # Respuesta inmediata: ElevenLabs reintenta si tarda o falla.
    return {"recibido": True}

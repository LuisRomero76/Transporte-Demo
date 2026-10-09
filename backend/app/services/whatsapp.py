"""Mensajes salientes de WhatsApp con plantillas aprobadas por Meta, enviados a través de ElevenLabs.

Se usan para avisar al cliente cuando el panel aprueba o rechaza su comprobante de pago. Meta solo entrega
plantillas si la cuenta de WhatsApp Business tiene un método de pago; si no, las descarta sin error.
"""

import logging

import httpx

from app.core.config import get_settings

log = logging.getLogger("transdemo.whatsapp")

URL_SALIENTE = "https://api.elevenlabs.io/v1/convai/whatsapp/outbound-message"


class WhatsAppNoDisponible(Exception):
    pass


def configurado() -> bool:
    s = get_settings()
    return bool(s.elevenlabs_api_key and s.elevenlabs_agent_id and s.elevenlabs_whatsapp_phone_number_id)


async def enviar_plantilla(telefono_e164: str, plantilla: str, parametros: list[str]) -> str:
    """Envía la plantilla al número (E.164 solo dígitos) y devuelve el id de la conversación de ElevenLabs."""
    s = get_settings()
    if not configurado():
        raise WhatsAppNoDisponible(
            "Faltan ELEVENLABS_API_KEY, ELEVENLABS_AGENT_ID o ELEVENLABS_WHATSAPP_PHONE_NUMBER_ID."
        )
    cuerpo = {
        "whatsapp_phone_number_id": s.elevenlabs_whatsapp_phone_number_id,
        "whatsapp_user_id": telefono_e164,
        "template_name": plantilla,
        "template_language_code": s.whatsapp_plantilla_idioma,
        "agent_id": s.elevenlabs_agent_id,
        # Meta rechaza parámetros vacíos o con saltos de línea.
        "template_params": [
            {"type": "body", "parameters": [{"type": "text", "text": " ".join(p.split()) or "-"} for p in parametros]}
        ],
    }
    async with httpx.AsyncClient(timeout=20) as cliente:
        r = await cliente.post(URL_SALIENTE, json=cuerpo, headers={"xi-api-key": s.elevenlabs_api_key or ""})
    if r.status_code >= 400:
        raise WhatsAppNoDisponible(f"ElevenLabs respondió {r.status_code}: {r.text[:200]}")
    return r.json().get("conversation_id", "")

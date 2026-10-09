"""Compra de pasajes por WhatsApp: reserva por chat sin duplicados, comprobante QR, revisión en el panel y webhook."""

import asyncio
import hashlib
import hmac
import json
import time
from datetime import timedelta
from decimal import Decimal

import pytest
from sqlalchemy import select

from app.core.config import get_settings
from app.core.db import SessionLocal
from app.models import ComprobantePago, VentaPasaje
from app.services import api_keys, comprobantes
from app.services.compra_chat import _monto
from app.utils.fechas import ahora, hoy

CLIENTE = "59171111111"
OTRO = "59172222222"


@pytest.fixture(scope="module")
async def bot():
    async with SessionLocal() as session:
        clave = await api_keys.crear_o_rotar(session, "tests-chat", [api_keys.SCOPE_LECTURA, api_keys.SCOPE_ESCRITURA])
    return {"X-Bot-Key": clave}


async def _codigo_salida(client, bot, dias: int, indice: int = 0) -> str:
    fecha = (hoy() + timedelta(days=dias)).isoformat()
    r = await client.get(
        "/api/bot/salidas", headers=bot, params={"origen": "Sucre", "destino": "Santa Cruz", "fecha": fecha}
    )
    assert r.status_code == 200, r.text
    salidas = [s for s in r.json()["salidas"] if s["vendible"]]
    return salidas[indice]["codigo"]


def _reserva(caller: str, codigo_salida: str, documentos: list[str], **extra) -> dict:
    return {
        "caller_id": caller,
        "codigo_salida": codigo_salida,
        "clase": "suite",
        "pasajeros": [{"numero_documento": d, "nombres": "ana maría", "apellidos": "quispe rojas"} for d in documentos],
        "confirmado": True,
        **extra,
    }


async def _crear(client, bot, cuerpo: dict) -> dict:
    r = await client.post("/api/bot/reservas", headers=bot, json=cuerpo)
    assert r.status_code == 200, r.text
    return r.json()


# --- Unidades ----------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("texto", "esperado"),
    [
        ("Bs. 27,000.00", "27000.00"),
        ("360,50", "360.50"),
        ("27.000,00", "27000.00"),
        ("1.500", "1500.00"),
        (360, "360.00"),
        ("sin monto", None),
    ],
)
def test_lectura_de_montos(texto, esperado):
    assert _monto(texto) == (Decimal(esperado) if esperado else None)


def test_cada_comprobante_toma_la_imagen_previa_a_su_registro():
    a = "11111111-1111-1111-1111-111111111111"
    b = "22222222-2222-2222-2222-222222222222"
    transcript = [
        {"role": "user", "file_input": {"file_url": "https://x/1.jpg", "mime_type": "image/jpeg"}},
        {
            "role": "agent",
            "tool_results": [{"tool_name": "registrar_comprobante", "result_value": f'{{"comprobante_id": "{a}"}}'}],
        },
        {"role": "user", "file_inputs": [{"file_url": "https://x/2.jpg", "mime_type": "image/jpeg"}]},
        {"role": "agent", "tool_results": [{"tool_name": "registrar_comprobante", "result_value": f"ok {b}"}]},
    ]
    por_id, ultima = comprobantes.imagenes_de(transcript)
    assert por_id[a]["file_url"].endswith("1.jpg") and por_id[b]["file_url"].endswith("2.jpg")
    assert ultima["file_url"].endswith("2.jpg")


# --- Reserva por chat --------------------------------------------------------------------------


async def test_salidas_traen_codigo_y_asientos_libres(client, bot):
    codigo = await _codigo_salida(client, bot, 20)
    r = await client.get(f"/api/bot/salidas/{codigo}/asientos", headers=bot, params={"clase": "leito"})
    c = r.json()
    assert r.status_code == 200 and c["encontrado"] and len(c["clases"]) == 1
    assert c["clases"][0]["clase"] == "Leito Cama" and c["clases"][0]["asientos"]


async def test_reserva_exige_confirmacion_numero_y_datos(client, bot):
    codigo = await _codigo_salida(client, bot, 20)
    c = await _crear(client, bot, _reserva(CLIENTE, codigo, ["8100001"], confirmado=False))
    assert not c["encontrado"] and "confirme" in c["mensaje"]
    c = await _crear(client, bot, _reserva("", codigo, ["8100001"]))
    assert not c["encontrado"] and "número" in c["mensaje"]
    cuerpo = _reserva(CLIENTE, codigo, ["8100001"])
    cuerpo["pasajeros"][0]["apellidos"] = ""
    c = await _crear(client, bot, cuerpo)
    assert not c["encontrado"] and "apellido" in c["mensaje"]
    c = await _crear(client, bot, _reserva(CLIENTE, codigo, ["8100001"], clase=None))
    assert not c["encontrado"] and "Suite Cama" in c["mensaje"]


async def test_reserva_por_chat_y_reintentos_sin_duplicar(client, bot):
    codigo = await _codigo_salida(client, bot, 21)
    cuerpo = _reserva(CLIENTE, codigo, ["8200001", "8200002"])
    # Dos chats del mismo número al mismo tiempo: una sola reserva.
    r1, r2 = await asyncio.gather(_crear(client, bot, cuerpo), _crear(client, bot, cuerpo))
    assert r1["encontrado"] and r2["encontrado"]
    assert r1["codigo_reserva"] == r2["codigo_reserva"] and len(r1["asientos"]) == 2
    assert "/pagar/" in r1["enlace_pago"] and r1["paga_hasta"]

    async with SessionLocal() as session:
        venta = await session.scalar(select(VentaPasaje).where(VentaPasaje.codigo_reserva == r1["codigo_reserva"]))
    assert venta.canal == "whatsapp_chat"
    assert timedelta(minutes=110) < venta.expira_at - ahora() <= timedelta(minutes=120)

    # El mismo carnet desde otro número, en la misma salida: rechazado.
    c = await _crear(client, bot, _reserva(OTRO, codigo, ["8200002"]))
    assert not c["encontrado"] and "ya tiene pasaje" in c["mensaje"]


async def test_limite_de_reservas_pendientes_por_numero(client, bot):
    numero = "59173333333"
    for i, dias in enumerate((22, 23)):
        c = await _crear(client, bot, _reserva(numero, await _codigo_salida(client, bot, dias), [f"830000{i}"]))
        assert c["encontrado"], c
    c = await _crear(client, bot, _reserva(numero, await _codigo_salida(client, bot, 24), ["8300009"]))
    assert not c["encontrado"] and "2 reservas pendientes" in c["mensaje"]


async def test_venta_por_chat_cierra_horas_antes(client, bot):
    r = await client.get(
        "/api/bot/salidas", headers=bot, params={"origen": "Sucre", "destino": "Santa Cruz", "fecha": "hoy"}
    )
    proximas = [s for s in r.json().get("salidas", []) if s["vendible"]]
    salida = next((s for s in proximas), None)
    if salida is None:
        pytest.skip("No hay salidas vendibles hoy a esta hora")
    c = (await client.get(f"/api/bot/salidas/{salida['codigo']}/asientos", headers=bot)).json()
    # Las salidas de hoy (18:30 y 20:00) cierran 3 h antes por chat; según la hora de la prueba puede seguir abierta.
    assert c["encontrado"] or "horas antes" in c["mensaje"]


# --- Comprobante, panel y aviso ------------------------------------------------------------------


async def test_comprobante_revision_aprobacion_y_rechazo(client, bot, boletero):
    codigo = await _codigo_salida(client, bot, 25)
    reserva = await _crear(client, bot, _reserva("59174444444", codigo, ["8400001"]))
    total = reserva["total_bs"]

    def comprobante(**extra) -> dict:
        return {"caller_id": "59174444444", "conversation_id": "conv_test_1", "monto": f"Bs. {total:,.2f}", **extra}

    async def registrar(cuerpo: dict) -> dict:
        r = await client.post("/api/bot/comprobantes", headers=bot, json=cuerpo)
        assert r.status_code == 200, r.text
        return r.json()

    c = await registrar(comprobante(es_comprobante=False))
    assert not c["encontrado"] and "no corresponde a un comprobante" in c["mensaje"]
    c = await registrar(comprobante(monto="10"))
    assert not c["encontrado"] and "total de la reserva" in c["mensaje"]
    c = await registrar(comprobante(caller_id=OTRO, codigo_reserva=reserva["codigo_reserva"]))
    assert not c["encontrado"] and "desde tu número" in c["mensaje"]

    c = await registrar(comprobante(numero_transaccion="18092026/295 140-726", banco="Banco Sol"))
    assert c["encontrado"] and c["terminar_conversacion"] and "revisando" in c["mensaje"]
    c2 = await registrar(comprobante(numero_transaccion="999"))
    assert not c2["encontrado"] and "en revisión" in c2["mensaje"]

    qr = (await client.get(f"/api/v1/reservas/{reserva['codigo_reserva']}/pago-qr")).json()
    assert qr["en_revision"] and qr["qr_payload"] is None and "comprador" not in qr

    # El mismo número de transacción no sirve para otra reserva.
    otra = await _crear(client, bot, _reserva("59175555555", await _codigo_salida(client, bot, 26), ["8500001"]))
    c = await registrar(
        {
            "caller_id": "59175555555",
            "monto": str(otra["total_bs"]),
            "numero_transaccion": "18092026295140726",
        }
    )
    assert not c["encontrado"] and "ya fue usado" in c["mensaje"]

    lista = (await client.get("/api/v1/admin/comprobantes", headers=boletero, params={"estado": "en_revision"})).json()
    fila = next(f for f in lista["items"] if f["codigo_reserva"] == reserva["codigo_reserva"])
    assert fila["monto_coincide"] and fila["numero_transaccion"] == "18092026295140726" and not fila["tiene_imagen"]
    r = await client.get(f"/api/v1/admin/comprobantes/{fila['id']}/imagen", headers=boletero)
    assert r.status_code == 404

    r = await client.post(f"/api/v1/admin/comprobantes/{fila['id']}/aprobar", headers=boletero)
    assert r.status_code == 200, r.text
    assert r.json()["estado"] == "aprobado" and r.json()["estado_reserva"] == "pagada"
    r = await client.post(f"/api/v1/admin/comprobantes/{fila['id']}/aprobar", headers=boletero)
    assert r.status_code == 409
    async with SessionLocal() as session:
        aprobado = await session.get(ComprobantePago, fila["id"])
        # Sin credenciales de ElevenLabs en los tests: el aviso queda registrado como fallido.
        assert aprobado.notificado_at is None and "ELEVENLABS" in (aprobado.notificacion_error or "")
    pagada = (
        await client.get(
            f"/api/bot/reservas/{reserva['codigo_reserva']}", headers=bot, params={"caller_id": "59174444444"}
        )
    ).json()
    assert pagada["estado"] == "pagada"

    # Rechazo: la otra reserva recibe un comprobante válido, se rechaza y vuelve a correr un plazo corto.
    c = await registrar({"caller_id": "59175555555", "monto": str(otra["total_bs"]), "numero_transaccion": "777"})
    assert c["encontrado"]
    r = await client.post(
        f"/api/v1/admin/comprobantes/{c['comprobante_id']}/rechazar",
        headers=boletero,
        json={"motivo": "el pago no llegó a la cuenta"},
    )
    assert r.status_code == 200 and r.json()["estado"] == "rechazado"
    qr = (await client.get(f"/api/v1/reservas/{otra['codigo_reserva']}/pago-qr")).json()
    assert not qr["en_revision"] and qr["qr_payload"] and qr["expira_at"]
    # Tras el rechazo puede enviar otro comprobante, incluso con el mismo número de transacción.
    c = await registrar({"caller_id": "59175555555", "monto": str(otra["total_bs"]), "numero_transaccion": "777"})
    assert c["encontrado"]
    lista = (await client.get("/api/v1/admin/comprobantes", headers=boletero, params={"estado": "en_revision"})).json()
    fila = next(f for f in lista["items"] if f["codigo_reserva"] == otra["codigo_reserva"])
    assert not fila["transaccion_repetida"]  # reenviar el propio comprobante no cuenta como repetido


async def test_panel_de_comprobantes_requiere_permiso(client, bodega):
    r = await client.get("/api/v1/admin/comprobantes", headers=bodega)
    assert r.status_code == 403


# --- Webhook post-llamada ------------------------------------------------------------------------


async def test_webhook_valida_la_firma(client, monkeypatch):
    monkeypatch.setattr(get_settings(), "elevenlabs_webhook_secret", "secreto-de-prueba")
    cuerpo = json.dumps({"type": "post_call_transcription", "data": {"conversation_id": "conv_x"}}).encode()
    r = await client.post("/api/webhooks/elevenlabs", content=cuerpo, headers={"ElevenLabs-Signature": "t=1,v0=malo"})
    assert r.status_code == 401
    t = int(time.time())
    firma = hmac.new(b"secreto-de-prueba", f"{t}.".encode() + cuerpo, hashlib.sha256).hexdigest()
    r = await client.post(
        "/api/webhooks/elevenlabs", content=cuerpo, headers={"ElevenLabs-Signature": f"t={t},v0={firma}"}
    )
    assert r.status_code == 200 and r.json()["recibido"]

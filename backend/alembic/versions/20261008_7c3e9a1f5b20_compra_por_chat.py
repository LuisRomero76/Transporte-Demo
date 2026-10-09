"""compra de pasajes por chat: comprobantes de pago QR y parámetros de la venta por WhatsApp

Revision ID: 7c3e9a1f5b20
Revises: 4b9d2e7c1a53
Create Date: 2026-10-08 15:00:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "7c3e9a1f5b20"
down_revision: str | Sequence[str] | None = "4b9d2e7c1a53"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ESTADO_COMPROBANTE = postgresql.ENUM("en_revision", "aprobado", "rechazado", name="estado_comprobante")

# Mismos valores que seeds/data/demo.py; ON CONFLICT DO NOTHING respeta lo que ya se haya editado.
PARAMETROS = {
    "reserva_chat_expira_minutos": (120, "Minutos para pagar por QR una reserva hecha por WhatsApp"),
    "venta_chat_cierre_minutos_antes": (
        180,
        "La venta por WhatsApp cierra estos minutos antes de la salida (y el plazo de pago nunca los supera)",
    ),
    "reservas_chat_pendientes_max": (2, "Reservas pendientes de pago que puede tener a la vez un número de WhatsApp"),
    "comprobante_rechazo_plazo_minutos": (60, "Minutos para enviar otro comprobante cuando se rechaza el anterior"),
}


def upgrade() -> None:
    ESTADO_COMPROBANTE.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "comprobantes_pago",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("venta_id", sa.Uuid(), nullable=False),
        sa.Column("caller_id", sa.String(length=15), nullable=True),
        sa.Column("conversation_id", sa.String(length=64), nullable=True),
        sa.Column(
            "estado",
            postgresql.ENUM(name="estado_comprobante", create_type=False),
            server_default="en_revision",
            nullable=False,
        ),
        sa.Column("monto_leido_bs", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("fecha_leida", sa.String(length=40), nullable=True),
        sa.Column("numero_transaccion", sa.String(length=80), nullable=True),
        sa.Column("banco", sa.String(length=60), nullable=True),
        sa.Column("cuenta_destino", sa.String(length=80), nullable=True),
        sa.Column("imagen", sa.LargeBinary(), nullable=True),
        sa.Column("imagen_mime", sa.String(length=40), nullable=True),
        sa.Column("imagen_obtenida_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("intentos_imagen", sa.SmallInteger(), server_default="0", nullable=False),
        sa.Column("motivo_rechazo", sa.String(length=250), nullable=True),
        sa.Column("revisado_por_usuario_id", sa.Uuid(), nullable=True),
        sa.Column("revisado_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notificado_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notificacion_error", sa.String(length=300), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["venta_id"], ["ventas_pasaje.id"], name=op.f("fk_comprobantes_pago_venta_id_ventas_pasaje")
        ),
        sa.ForeignKeyConstraint(
            ["revisado_por_usuario_id"],
            ["usuarios.id"],
            name=op.f("fk_comprobantes_pago_revisado_por_usuario_id_usuarios"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_comprobantes_pago")),
    )
    op.create_index("ix_comprobantes_pago_venta_id", "comprobantes_pago", ["venta_id"])
    op.create_index("ix_comprobantes_pago_conversation_id", "comprobantes_pago", ["conversation_id"])
    op.create_index("ix_comprobantes_pago_estado_created_at", "comprobantes_pago", ["estado", "created_at"])
    op.create_index(
        "uq_comprobantes_pago_venta_en_revision",
        "comprobantes_pago",
        ["venta_id"],
        unique=True,
        postgresql_where=sa.text("estado = 'en_revision'"),
    )
    op.create_index(
        "uq_comprobantes_pago_numero_transaccion",
        "comprobantes_pago",
        ["numero_transaccion"],
        unique=True,
        postgresql_where=sa.text("estado <> 'rechazado' AND numero_transaccion IS NOT NULL"),
    )
    op.execute(
        "CREATE TRIGGER trg_comprobantes_pago_updated_at BEFORE UPDATE ON comprobantes_pago "
        "FOR EACH ROW EXECUTE FUNCTION set_updated_at()"
    )

    parametros = sa.table(
        "parametros_negocio",
        sa.column("clave", sa.String),
        sa.column("valor", postgresql.JSONB),
        sa.column("descripcion", sa.String),
        sa.column("es_dato_demo", sa.Boolean),
    )
    op.execute(
        postgresql.insert(parametros)
        .values(
            [
                {"clave": clave, "valor": valor, "descripcion": desc, "es_dato_demo": True}
                for clave, (valor, desc) in PARAMETROS.items()
            ]
        )
        .on_conflict_do_nothing(index_elements=["clave"])
    )


def downgrade() -> None:
    op.execute(
        sa.text("DELETE FROM parametros_negocio WHERE clave IN :claves").bindparams(
            sa.bindparam("claves", list(PARAMETROS), expanding=True)
        )
    )
    op.drop_table("comprobantes_pago")
    ESTADO_COMPROBANTE.drop(op.get_bind(), checkfirst=True)

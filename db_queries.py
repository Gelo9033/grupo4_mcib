from db_connection import RealDictCursor, get_connection


def init_db() -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS public.usuarios (
                    id BIGSERIAL PRIMARY KEY,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    saldo NUMERIC(12,2) NOT NULL DEFAULT 0 CHECK (saldo >= 0),
                    creado_en TIMESTAMP NOT NULL DEFAULT NOW()
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS public.movimientos (
                    id BIGSERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    tipo VARCHAR(30) NOT NULL,
                    monto NUMERIC(12,2) NOT NULL CHECK (monto > 0),
                    destino VARCHAR(100),
                    fraude BOOLEAN NOT NULL DEFAULT FALSE,
                    creado_en TIMESTAMP NOT NULL DEFAULT NOW(),
                    CONSTRAINT fk_mov_user
                        FOREIGN KEY (user_id)
                        REFERENCES public.usuarios(id)
                        ON DELETE CASCADE
                );
                """
            )


def get_user_by_username(username: str):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, username, password, saldo
                FROM public.usuarios
                WHERE username = %s
                """,
                (username,),
            )
            user = cur.fetchone()

            if not user:
                return None

    return {
        "id": user["id"],
        "username": user["username"],
        "password": user["password"],
        "saldo": float(user["saldo"]),
    }


def transferir_y_registrar(username: str, monto: float, destino: str, fraude: bool):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, saldo
                FROM public.usuarios
                WHERE username = %s
                FOR UPDATE
                """,
                (username,),
            )
            user = cur.fetchone()

            if not user:
                return {
                    "ok": False,
                    "reason": "user_not_found",
                    "saldo_disponible": None,
                }

            saldo_actual = float(user["saldo"])
            if saldo_actual < monto:
                return {
                    "ok": False,
                    "reason": "insufficient_funds",
                    "saldo_disponible": saldo_actual,
                }

            cur.execute(
                """
                UPDATE public.usuarios
                SET saldo = saldo - %s
                WHERE id = %s
                RETURNING saldo
                """,
                (monto, user["id"]),
            )
            saldo_actualizado = float(cur.fetchone()["saldo"])

            cur.execute(
                """
                INSERT INTO public.movimientos (user_id, tipo, monto, destino, fraude)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (user["id"], "transferencia", monto, destino, fraude),
            )

    return {
        "ok": True,
        "reason": "success",
        "saldo_actual": saldo_actualizado,
    }


def get_movimientos_by_username(username: str):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT m.tipo, m.monto, m.destino, m.fraude, m.creado_en
                FROM public.movimientos m
                INNER JOIN public.usuarios u ON u.id = m.user_id
                WHERE u.username = %s
                ORDER BY m.creado_en DESC
                """,
                (username,),
            )
            rows = cur.fetchall()

    return [
        {
            "tipo": row["tipo"],
            "monto": float(row["monto"]),
            "destino": row["destino"],
            "fraude": bool(row["fraude"]),
            "creado_en": row["creado_en"].isoformat() if row["creado_en"] else None,
        }
        for row in rows
    ]


def crear_usuario(username: str, password: str, saldo_inicial: float = 0.0):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO public.usuarios (username, password, saldo)
                VALUES (%s, %s, %s)
                RETURNING id, username, saldo
                """,
                (username, password, saldo_inicial),
            )
            row = cur.fetchone()

    return {
        "id": row["id"],
        "username": row["username"],
        "saldo": float(row["saldo"]),
    }


def recargar_saldo_y_registrar(username: str, monto: float):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id
                FROM public.usuarios
                WHERE username = %s
                FOR UPDATE
                """,
                (username,),
            )
            user = cur.fetchone()

            if not user:
                return {
                    "ok": False,
                    "reason": "user_not_found",
                    "saldo_actual": None,
                }

            cur.execute(
                """
                UPDATE public.usuarios
                SET saldo = saldo + %s
                WHERE id = %s
                RETURNING saldo
                """,
                (monto, user["id"]),
            )
            saldo_actualizado = cur.fetchone()["saldo"]

            cur.execute(
                """
                INSERT INTO public.movimientos (user_id, tipo, monto, destino, fraude)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (user["id"], "recarga", monto, None, False),
            )

    return {
        "ok": True,
        "reason": "success",
        "saldo_actual": float(saldo_actualizado),
    }

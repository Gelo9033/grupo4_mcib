from fastapi import FastAPI, Header, HTTPException, Request
import os

from models import Login, RecargaSaldo, Transferencia, UsuarioNuevo
from database import (
    crear_usuario,
    get_movimientos_by_username,
    get_user_by_username,
    init_db,
    recargar_saldo_y_registrar,
    transferir_y_registrar,
)
from auth import crear_token, verificar_token
from utils import detectar_fraude
from telegram_alert import enviar_alerta_saldo_insuficiente, enviar_alerta_telegram


def load_env_file(env_path: str = ".env") -> None:
    if not os.path.exists(env_path):
        return

    with open(env_path, "r", encoding="utf-8") as env_file:
        for line in env_file:
            line = line.strip()

            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            if key and key not in os.environ:
                os.environ[key] = value


load_env_file()

app = FastAPI(title="bank_api")


@app.on_event("startup")
def startup_event():
    init_db()


# -------- LOGIN --------
@app.post("/login")
def login(data: Login, request: Request):
    user = get_user_by_username(data.username)

    if not user or user["password"] != data.password:
        ip = request.client.host if request.client else "N/A"
        enviar_alerta_telegram(usuario=data.username, ip=ip)
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    token = crear_token({"sub": data.username})
    return {"access_token": token}


@app.post("/usuarios")
def registrar_usuario(data: UsuarioNuevo, x_admin_key: str | None = Header(default=None)):
    admin_key = os.getenv("ADMIN_API_KEY", "")
    if not admin_key:
        raise HTTPException(
            status_code=500,
            detail="Falta configurar ADMIN_API_KEY en variables de entorno",
        )

    if x_admin_key != admin_key:
        raise HTTPException(status_code=401, detail="No autorizado")

    if data.saldo_inicial < 0:
        raise HTTPException(status_code=400, detail="Saldo inicial no puede ser negativo")

    if get_user_by_username(data.username):
        raise HTTPException(status_code=409, detail="El usuario ya existe")

    nuevo = crear_usuario(data.username, data.password, data.saldo_inicial)
    return {"mensaje": "Usuario creado", "usuario": nuevo}


# -------- DEPENDENCIA --------
def get_username_from_token(token: str) -> str:
    payload = verificar_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")

    username = payload["sub"]
    return username


# -------- SALDO --------
@app.get("/saldo")
def saldo(token: str):
    username = get_username_from_token(token)
    user = get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return {"saldo": user["saldo"]}


# -------- TRANSFERENCIA --------
@app.post("/transferir")
def transferir(data: Transferencia, token: str):
    username = get_username_from_token(token)

    if data.monto <= 0:
        raise HTTPException(status_code=400, detail="El monto debe ser mayor a cero")

    fraude = detectar_fraude(data.monto)

    result = transferir_y_registrar(
        username=username,
        monto=data.monto,
        destino=data.destino,
        fraude=fraude,
    )

    if not result["ok"] and result["reason"] == "user_not_found":
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    if not result["ok"] and result["reason"] == "insufficient_funds":
        enviar_alerta_saldo_insuficiente(
            usuario=username,
            monto=data.monto,
            saldo=result["saldo_disponible"],
        )
        raise HTTPException(status_code=400, detail="Saldo insuficiente")

    return {"mensaje": "Transferencia realizada", "fraude_detectado": fraude}


@app.post("/recargar")
def recargar(data: RecargaSaldo, token: str):
    username = get_username_from_token(token)

    if data.monto <= 0:
        raise HTTPException(status_code=400, detail="El monto debe ser mayor a cero")

    result = recargar_saldo_y_registrar(username, data.monto)
    if not result["ok"] and result["reason"] == "user_not_found":
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return {
        "mensaje": "Recarga realizada",
        "saldo_actual": result["saldo_actual"],
    }


# -------- MOVIMIENTOS --------
@app.get("/movimientos")
def movimientos(token: str):
    username = get_username_from_token(token)
    return {"movimientos": get_movimientos_by_username(username)}


@app.get("/")
def inicio():
    return {"mensaje": "API Banco Simulado funcionando 🚀"}
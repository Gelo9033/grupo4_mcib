from fastapi import FastAPI, HTTPException, Request
import os

from models import Login, Transferencia
from database import users_db
from auth import crear_token, verificar_token
from utils import detectar_fraude
from telegram_alert import enviar_alerta_telegram


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

app = FastAPI(title="Banco Simulado Inteligente")


# -------- LOGIN --------
@app.post("/login")
def login(data: Login, request: Request):
    user = users_db.get(data.username)

    if not user or user["password"] != data.password:
        ip = request.client.host if request.client else "N/A"
        enviar_alerta_telegram(usuario=data.username, ip=ip)
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    token = crear_token({"sub": data.username})
    return {"access_token": token}


# -------- DEPENDENCIA --------
def get_user(token: str):
    payload = verificar_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")

    username = payload["sub"]
    return users_db.get(username)


# -------- SALDO --------
@app.get("/saldo")
def saldo(token: str):
    user = get_user(token)
    return {"saldo": user["saldo"]}


# -------- TRANSFERENCIA --------
@app.post("/transferir")
def transferir(data: Transferencia, token: str):
    user = get_user(token)

    if user["saldo"] < data.monto:
        raise HTTPException(status_code=400, detail="Saldo insuficiente")

    fraude = detectar_fraude(data.monto)

    user["saldo"] -= data.monto
    user["movimientos"].append(
        {
            "tipo": "transferencia",
            "monto": data.monto,
            "destino": data.destino,
            "fraude": fraude,
        }
    )

    return {"mensaje": "Transferencia realizada", "fraude_detectado": fraude}


# -------- MOVIMIENTOS --------
@app.get("/movimientos")
def movimientos(token: str):
    user = get_user(token)
    return {"movimientos": user["movimientos"]}


@app.get("/")
def inicio():
    return {"mensaje": "API Banco Simulado funcionando 🚀"}
from pydantic import BaseModel

class Login(BaseModel):
    username: str
    password: str

class Transferencia(BaseModel):
    destino: str
    monto: float


class UsuarioNuevo(BaseModel):
    username: str
    password: str
    saldo_inicial: float = 0.0


class RecargaSaldo(BaseModel):
    monto: float
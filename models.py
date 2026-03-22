from pydantic import BaseModel

class Login(BaseModel):
    username: str
    password: str

class Transferencia(BaseModel):
    destino: str
    monto: float
from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = "clave_secreta"
ALGORITHM = "HS256"

def crear_token(data: dict):
    datos = data.copy()
    datos["exp"] = datetime.utcnow() + timedelta(hours=1)
    return jwt.encode(datos, SECRET_KEY, algorithm=ALGORITHM)

def verificar_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except:
        return None
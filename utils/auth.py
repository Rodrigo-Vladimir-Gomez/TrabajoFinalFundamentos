import bcrypt
from passlib.context import CryptContext


# Crea un objeto de verificación para las contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# Función para verificar la contraseña
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

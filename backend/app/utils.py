import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from .config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

REGISTRATION_SECRET = settings.recaptcha_secret_key
ALGORITHM = "HS256"

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# def create_registration_token(email: str, hashed_pass: str) -> str:
#     expire = datetime.now(timezone.utc) + timedelta(hours=24)
#     payload = {
#         "sub": email,
#         "password_hash": hashed_pass,
#         "exp": expire
#     }
#     return jwt.encode(payload, REGISTRATION_SECRET, algorithm=ALGORITHM)
#
# def verify_registration_token(token: str) -> dict | None:
#     try:
#         payload = jwt.decode(token, REGISTRATION_SECRET, algorithms=[ALGORITHM])
#         return {
#             "email": payload.get("sub"),
#             "password_hash": payload.get("password_hash")
#         }
#     except jwt.PyJWTError:
#         return None
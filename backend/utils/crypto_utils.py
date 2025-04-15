import base64
import os

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

SECRET_KEY = os.getenv("SECRET_KEY", "lmaoiain'ttellingyouthekey")


def generate_key(password: str, salt: bytes | None = None):
    if salt is None:
        salt = os.urandom(16)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )

    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt


def encrypt_data(data: str) -> str:
    key, salt = generate_key(SECRET_KEY)
    f = Fernet(key)
    encrypted_data = f.encrypt(data.encode())
    # prepend salt to encrypted data
    return base64.urlsafe_b64encode(salt + encrypted_data).decode()


def decrypt_data(encrypted_data: str) -> str | None:
    try:
        decoded: bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        salt: bytes = decoded[:16]
        ciphertext: bytes = decoded[16:]
        key, _ = generate_key(SECRET_KEY, salt=salt)
        f = Fernet(key)
        decrypted_data: str = f.decrypt(ciphertext).decode()
        return decrypted_data
    except Exception:
        return None

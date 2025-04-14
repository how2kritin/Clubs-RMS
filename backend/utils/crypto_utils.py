import base64
import os

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

SECRET_KEY = os.getenv('SECRET_KEY', "lmaoiain'ttellingyouthekey")


def generate_key(password: str, salt: bytes = None):
    if salt is None:
        salt = os.urandom(16)

    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000, )

    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt


def get_encryption_key():
    key, _ = generate_key(SECRET_KEY)
    return key


def encrypt_data(data: str) -> str:
    key = get_encryption_key()
    f = Fernet(key)
    encrypted_data = f.encrypt(data.encode())
    return base64.urlsafe_b64encode(encrypted_data).decode()


def decrypt_data(encrypted_data: str) -> str:
    try:
        key = get_encryption_key()
        f = Fernet(key)
        decoded = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted_data = f.decrypt(decoded).decode()
        return decrypted_data
    except Exception:
        # if decryption fails, return None
        return None

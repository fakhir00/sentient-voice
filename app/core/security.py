from cryptography.fernet import Fernet
from app.core.config import settings

def get_fernet() -> Fernet:
    return Fernet(settings.ENCRYPTION_KEY)

def encrypt_value(value: str) -> str:
    """Encrypts a string value using Fernet."""
    if not value:
        return value
    f = get_fernet()
    return f.encrypt(value.encode()).decode()

def decrypt_value(value: str) -> str:
    """Decrypts a string value using Fernet."""
    if not value:
        return value
    f = get_fernet()
    return f.decrypt(value.encode()).decode()

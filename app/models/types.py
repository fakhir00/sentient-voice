from sqlalchemy import String, TypeDecorator
from app.core.security import encrypt_value, decrypt_value

class EncryptedString(TypeDecorator):
    """
    SQLAlchemy TypeDecorator that encrypts data before saving to DB
    and decrypts it when retrieving.
    """
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        return encrypt_value(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return decrypt_value(value)

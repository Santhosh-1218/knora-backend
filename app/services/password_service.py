from app.core.security import hash_password, verify_password


class PasswordService:
    @staticmethod
    def hash_password(password: str) -> str:
        return hash_password(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return verify_password(plain_password, hashed_password)


password_service = PasswordService()

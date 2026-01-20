from uuid import UUID

from domain.exceptions import CustomException
from domain.exceptions.common import NotFoundException


class RefreshTokenException(CustomException):
    pass


class RefreshTokenNotFoundException(RefreshTokenException, NotFoundException):
    def __init__(self, *, token_id: UUID | None = None, token_hash: str | None = None) -> None:
        if token_id:
            self.message = f"Refresh token with id {token_id} not found"
        elif token_hash:
            self.message = f"Refresh token with hash {token_hash} not found"
        else:
            self.message = "Refresh token not found"
        super().__init__(self.message)

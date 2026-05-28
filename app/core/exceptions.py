from fastapi import HTTPException, status

class AppException(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST) -> None:
        super().__init__(status_code=status_code, detail=detail)
        
        
class NotFoundException(AppException):
    def __init__(self, resource: str = "Resource") -> None:
        super().__init__(
            detail=f"{resource} not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
        
        
class UnauthorizedException(AppException):
    def __init__(self, detail: str = "Could not validate credentials") -> None:
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)


class ConflictException(AppException):
    def __init__(self, detail: str) -> None:
        super().__init__(detail=detail, status_code=status.HTTP_409_CONFLICT)

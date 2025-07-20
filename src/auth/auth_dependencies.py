from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, status
from fastapi import Request
from src.auth.auth_utils import decode_token
from fastapi.exceptions import HTTPException



class AccessTokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)


    async def __call__(self,request:Request) -> HTTPAuthorizationCredentials | None:
        creds= await super().__call__(request)

        token = creds.credentials

        token_data = decode_token(token)

        if not self.token_valid(token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                
            )
        
        if token_data['refresh']:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token is not allowed for this endpoint",
            )

        return token_data

    def token_valid(self, token:str) -> bool:
        
        token_data = decode_token(token)

        return True if token_data is not None else False
        
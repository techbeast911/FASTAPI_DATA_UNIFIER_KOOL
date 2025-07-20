from fastapi import APIRouter, Depends,status
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from src.auth.auth_schemas import UserCreateModel, UserModel,UserLoginModel
from src.auth.auth_services import UserService
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from src.auth.auth_utils import create_access_token,decode_token, verify_password
from datetime import timedelta
from fastapi.responses import JSONResponse


auth_router = APIRouter()
user_service = UserService()
REFRESH_TOKEN_EXPIRY = timedelta(days=2)  # Set the refresh token expiry to 2 days


@auth_router.post('/signup',
                response_model=UserModel,
                status_code=status.HTTP_201_CREATED,
                summary="Create a new user account",
                description="This endpoint allows you to create a new user account with a username, email, and password. The password will be securely hashed before storage."
                )
async def create_user_account(user_data: UserCreateModel,
session: AsyncSession = Depends(get_session)):
    email = user_data.email 
    user_exists = await user_service.user_exists(email, session)

    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists."
        )
    new_user = await user_service.create_user(user_data, session)

    return new_user


@auth_router.post('/login')
async def login_user(login_data: UserLoginModel,session: AsyncSession = Depends(get_session)):
    email = login_data.email
    password = login_data.password

    user = await user_service.get_user_by_email(email, session)


    if user is not None:
        password_valid = verify_password(password, user.password_hash)


        if password_valid:
            access_token = create_access_token(
                user_data={"uid": str(user.uid), 
                "email": user.email}
            )
            
            refresh_token = create_access_token(
                user_data={"uid": str(user.uid), 
                "email": user.email},
                refresh = True,
                expiry = REFRESH_TOKEN_EXPIRY
            )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "message" : "Login Successful",
                    "user":{
                        "email": user.email,
                        "uid": str(user.uid) 
                    }
                }
            )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password."
    )
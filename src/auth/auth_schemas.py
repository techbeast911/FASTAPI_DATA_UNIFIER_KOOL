# from pydantic import BaseModel, EmailStr, Field
# #from sqlmodel import SQLModel, Field, Column
# from uuid import UUID, uuid4          # <-- already brings UUID into scope
# from datetime import datetime



# class UserCreateModel(BaseModel):
#     username : str = Field(max_length=50, min_length=3)
#     email: str = Field(max_length=254)
#     password: str = Field(
#         min_length=8,)
    

# class UserModel(BaseModel):
#     uid: UUID 

#     username: str
#     first_name: str
#     last_name: str
#     is_verified: bool 
#     email: str
#     password_hash: str = Field(exclude=True)  # Exclude from model dumps, e.g., in responses
#     created_at: datetime 

from pydantic import BaseModel, EmailStr, Field
# from sqlmodel import SQLModel, Field, Column # Not needed here
from uuid import UUID # Only UUID is needed, uuid4 is used in model defaults
from datetime import datetime
from typing import Optional # <--- IMPORT OPTIONAL


class UserCreateModel(BaseModel):
    username : str = Field(max_length=50, min_length=3)
    email: EmailStr = Field(max_length=254) # Use EmailStr for proper email validation
    first_name: Optional[str] = None # Added Optional and default None
    last_name: Optional[str] = None  # Added Optional and default None
    password: str = Field(min_length=8)

    class Config:
        json_schema_extra = {
            "example": {
                "username": "testuser",
                "email": "test@example.com",
                "password": "StrongPassword123"
            }
        }


class UserModel(BaseModel):
    uid: UUID
    username: str
    # --- CRITICAL CHANGE HERE ---
    # Make first_name and last_name Optional to match your SQLModel's nullable settings
    first_name: Optional[str] = None # Added Optional and default None
    last_name: Optional[str] = None  # Added Optional and default None
    is_verified: bool
    email: EmailStr # Use EmailStr for consistency
    password_hash: str = Field(exclude=True) # Exclude from model dumps, e.g., in responses
    created_at: datetime

    class Config:
        from_attributes = True # This is crucial for Pydantic V2 to work with ORM objects
        json_schema_extra = {
            "example": {
                "uid": "123e4567-e89b-12d3-a456-426614174000",
                "username": "exampleuser",
                "first_name": "Example",
                "last_name": "User",
                "is_verified": True,
                "email": "example@domain.com",
                "created_at": "2025-06-25T15:00:00"
                # password_hash is excluded, so not in example
            }
        }

class UserLoginModel(BaseModel):
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "exampleuser@email.com",
                "password": "StrongPassword123"}}
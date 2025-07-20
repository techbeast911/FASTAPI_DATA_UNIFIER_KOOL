# src/auth/auth_services.py
from src.auth.auth_models import User
from src.auth.auth_schemas import UserCreateModel
from src.auth.auth_utils import generate_passwd_hash, verify_password
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from fastapi import HTTPException, status # Required for robust error handling


class UserService:
    async def get_user_by_email(self, email: str, session: AsyncSession) -> User | None:
        """Fetch a user by email."""
        statement = select(User).where(User.email == email)
        result = await session.execute(statement) # Correct: session.execute
        user = result.scalars().first() # Correct: scalars().first()
        return user
        
    async def user_exists(self, email: str, session: AsyncSession) -> bool:
        """Check if a user with the given email already exists."""
        user = await self.get_user_by_email(email, session)
        return user is not None # Returns True if user exists, False otherwise

    async def create_user(self, user_create: UserCreateModel, session: AsyncSession) -> User:
        """
        Creates a new user account.
        Ensures password is hashed and database-generated fields are refreshed.
        """
        # Get data from the Pydantic schema as a dictionary
        user_data_dict = user_create.model_dump()
        
        # --- CRITICAL FIXES RE-APPLIED HERE ---
        # 1. Pop the plain password from the dictionary before instantiating the SQLModel
        # The User SQLModel has 'password_hash', not 'password'.
        password_to_hash = user_data_dict.pop('password') 
        
        # 2. Instantiate the User SQLModel with the remaining data
        # This allows SQLModel to apply its default_factory (for uid) and default (for created_at).
        db_user = User(**user_data_dict) 
        
        # 3. Hash the password and assign it to the correct field
        db_user.password_hash = generate_passwd_hash(password_to_hash)

        session.add(db_user)
        
        try:
            await session.commit()
            # 4. IMPORTANT: Refresh the object after commit to get its database-generated state.
            # This populates `uid`, `created_at`, etc., back into the `db_user` object.
            await session.refresh(db_user) 
            
            print(f"DEBUG: Successfully created user: {db_user.username}, UID: {db_user.uid}")

        except Exception as e:
            # 5. Robust error handling: Rollback the session and raise an HTTPException.
            await session.rollback() 
            print(f"ERROR: Failed to create user during database operation: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create user due to a database error: {e}"
            )
        
        # 6. Return the fully populated and refreshed User SQLModel object.
        # FastAPI will then use UserModel (from response_model) to serialize this object.
        return db_user
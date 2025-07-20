from passlib.context import CryptContext
from datetime import timedelta, datetime
import jwt
from src.config import Config 
import uuid
import logging
from jwt.exceptions import PyJWTError




ACCESS_TOKEN_EXPIRY = 3600

# Create a password context for hashing and verifying passwords
passwd_context = CryptContext(schemes =["bcrypt"])

def generate_passwd_hash(password: str) -> str:
    """
    Generate a hashed password.
    
    Args:
        password (str): The plaintext password to hash.
        
    Returns:
        str: The hashed password.
    """
    hash= passwd_context.hash(password)
    return hash


def verify_password(password:str,hash: str) -> bool:

    """
    Verify a plaintext password against a hashed password.
    
    Args:
        password (str): The plaintext password to verify.
        hash (str): The hashed password to compare against.
        
    Returns:
        bool: True if the passwords match, False otherwise.
    """
    return passwd_context.verify(password, hash)


def create_access_token(user_data:dict, expiry: timedelta = None,refresh: bool = False):
    payload = {}

    payload['user'] = user_data
    payload['exp'] = datetime.utcnow() + (expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRY))

    payload['jti'] = str(uuid.uuid4())  # Unique identifier for the token
    payload['refresh'] = refresh


    token = jwt.encode(
        payload=payload,
        key= Config.JWT_SECRET,
        algorithm=Config.JWT_ALGORITHM)

    return token


def decode_token(token: str) -> dict:
    """
    Decode a JWT token and return the payload.
    
    Args:
        token (str): The JWT token to decode.
        
    Returns:
        dict: The decoded payload of the token.
    """
    try:
        token_data = jwt.decode(
            jwt= token,
            key=Config.JWT_SECRET,
            algorithms=[Config.JWT_ALGORITHM]
        )
        return token_data
    except PyJWTError as e:
        logging.exception(f"Token decoding failed: {e}")
        return None
from starlette.concurrency import run_in_threadpool
import bcrypt
import secrets
import hashlib

class Hashing:
    @staticmethod
    async def hash_password(password: str) -> str:
        """Hash a password using bcrypt with error handling."""
        try:
            salt = await run_in_threadpool(bcrypt.gensalt)
            hashed = await run_in_threadpool(bcrypt.hashpw, password.encode(), salt)
            return hashed.decode()
        except Exception as e:
            # You can log the exception here if needed
            print(f"Error hashing password: {e}")
            raise

    @staticmethod
    async def verify_password(password: str, hashed_password: str) -> bool:
        """Verify a password against a stored hash with error handling."""
        try:
            return await run_in_threadpool(bcrypt.checkpw, password.encode(), hashed_password.encode())
        except Exception as e:
            # You can log the exception here if needed
            print(f"Error verifying password: {e}")
            return False
        
    @staticmethod
    async def generate_random_hash():
        # Generate a secure random string
        random_string = secrets.token_hex(32)  # 64-character hex string

        # Hash it using SHA256
        hash_object = hashlib.sha256(random_string.encode())
        return hash_object.hexdigest()



# import asyncio
# hashed = asyncio.run(Hashing.hash_password("praveen1234"))
# hashe="$2b$12$JWB2ZwXPiu9Nr6c/jOxx7OGgycGOi5/1NfSj3HldcW6IkKcQUjviK"
# print("hashpass:", hashed)
# print("hashpass:", hashe)
# check = asyncio.run(Hashing.verify_password("praveen1234","$2b$12$JWB2ZwXPiu9Nr6c/jOxx7OGgycGOi5/1NfSj3HldcW6IkKcQUjviK"))
# print(check)
from fastapi import HTTPException
async def Auhtentication(authorization:str,password_hash):
    print(password_hash )
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing Authorization header")
    token = authorization.split(" ")[1]
    if token != password_hash:
        raise HTTPException(status_code=401, detail="Invalid token")
    return True   





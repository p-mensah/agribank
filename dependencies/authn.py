from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from dotenv import load_dotenv
import os
from db import users_collection

load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"

security = HTTPBearer(
    scheme_name="Bearer Token",
    description="Paste your JWT access token below",
    auto_error=False
)

def create_access_token(user_id: str):
    return jwt.encode({"sub": user_id}, JWT_SECRET, algorithm=ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        return None  # Let route handle unauth

    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = users_collection.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# Use in routes
authenticated_user = get_current_user
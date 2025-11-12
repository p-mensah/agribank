# router/users.py
from fastapi import APIRouter, Depends, HTTPException, status, Form
from pydantic import EmailStr
from typing import Annotated
import bcrypt
from db import users_collection
from dependencies.authn import authenticated_user, create_access_token
from utils import replace_mongo_id

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(
    name: Annotated[str, Form()],
    email: Annotated[EmailStr, Form()],
    password: Annotated[str, Form(min_length=8)],
    phone: Annotated[int, Form()],
    address: Annotated[str, Form()]
):
    """Creates a new user account.

    Args:
        name (str): The user's full name.
        email (EmailStr): The user's email address.
        password (str): The user's password (at least 8 characters).
        phone (int): The user's phone number.
        address (str): The user's physical address.

    Raises:
        HTTPException: If the email is already registered.

    Returns:
        dict: A message indicating successful user creation.
    """
    if users_collection.find_one({"email": email}):
        raise HTTPException(
            status_code=409,
            detail="This email is already registered"
        )
    
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user = {
        "_id": str(__import__("uuid").uuid4()),
        "name": name,
        "email": email,
        "password_hash": hashed,
        "phone": phone,          # ← SAVED
        "address": address,      # ← SAVED
        "is_active": True,
        "is_verified": False,
        "created_at": __import__("datetime").datetime.now()
    }
    users_collection.insert_one(user)
    return {"message": "User created successfully"}

@router.post("/login")
def login(
    email: Annotated[EmailStr, Form()],
    password: Annotated[str, Form()]
):
    """Authenticates a user and returns an access token.

    Args:
        email (EmailStr): The user's email address.
        password (str): The user's password.

    Raises:
        HTTPException: If the email or password is invalid.

    Returns:
        dict: A dictionary containing the access token and token type.
    """
    user = users_collection.find_one({"email": email})
    if not user or not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    token = create_access_token(user["_id"])
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me")
def me(current_user=Depends(authenticated_user)):
    """Retrieves the authenticated user's profile.

    Args:
        current_user (dict): The authenticated user's data, injected by Depends(authenticated_user).

    Returns:
        dict: The user's profile information with the '_id' field replaced by 'id'.
    """
    return replace_mongo_id(current_user)
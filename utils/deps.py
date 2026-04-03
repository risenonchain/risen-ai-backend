from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
import os

# =============================
# 🔹 AUTH SCHEME
# =============================
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# =============================
# 🔹 ENV CONFIG
# =============================
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"


# =============================
# 🔹 GET CURRENT USER (FROM JWT)
# =============================
def get_current_ai_user(token: str = Depends(oauth2_scheme)):
    try:
        if not SECRET_KEY:
            raise HTTPException(
                status_code=500,
                detail="SECRET_KEY not configured on server",
            )

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id = payload.get("sub")
        username = payload.get("username")
        email = payload.get("email")
        is_admin = payload.get("is_admin", False)

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token: missing user ID",
            )

        return {
            "id": int(user_id),
            "username": username,
            "email": email,
            "is_admin": is_admin,
        }

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )
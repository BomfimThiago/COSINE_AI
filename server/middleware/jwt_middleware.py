from fastapi import Request, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from typing import Callable, Any

# Define the OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# Middleware to validate JWT tokens
async def jwt_middleware(request: Request, call_next: Callable[[Request], Any]) -> Any:
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # Assuming the secret key is stored in an environment variable
        secret_key = "your_secret_key"
        payload = jwt.decode(token.split(" ")[1], secret_key, algorithms=["HS256"])
        request.state.user = payload  # Store user info in request state
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    response = await call_next(request)
    return response

# To use this middleware, include it in your FastAPI app:
# from fastapi import FastAPI
# from server.middleware.jwt_middleware import jwt_middleware
# app = FastAPI()
# app.middleware("http")(jwt_middleware)
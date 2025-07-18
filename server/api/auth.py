from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

router = APIRouter()

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        # Simulate user authentication (replace with actual logic)
        if form_data.username != "valid_user" or form_data.password != "valid_password":
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Simulate token generation (replace with actual logic)
        access_token = "fake_access_token"
        return Token(access_token=access_token, token_type="bearer")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/users/me")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    try:
        # Simulate token validation (replace with actual logic)
        if token != "valid_access_token":
            raise HTTPException(status_code=401, detail="Invalid token")

        return {"username": "valid_user"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
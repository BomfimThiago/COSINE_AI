from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr, constr
from sqlalchemy.orm import Session
from database import get_db, Base, engine
from models import User

# Create the database tables
Base.metadata.create_all(bind=engine)

router = APIRouter()

class UserCreate(BaseModel):
    username: constr(min_length=3, max_length=50)
    password: constr(min_length=6)
    email: EmailStr

@router.post('/register')
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if the user already exists
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail='Username already registered')

    # Create a new user instance
    new_user = User(username=user.username, email=user.email)
    new_user.set_password(user.password)  # Assuming a method to hash the password

    # Add the user to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {'username': new_user.username, 'email': new_user.email}

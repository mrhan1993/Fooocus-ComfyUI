from datetime import timedelta

from fastapi import APIRouter
from fastapi import HTTPException, Depends, status

from apis.models.users import UserInDB, User, UserCreate

user_route = APIRouter()


@user_route.post("/register", response_model=User)
async def register(user: UserCreate):
    if user.username in fake_users_db:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    user_in_db = UserInDB(**user.dict(), hashed_password=hashed_password)
    fake_users_db[user.username] = user_in_db.dict()
    return user


@user_route.post("/login")
async def login(username: str, password: str):
    user = authenticate_user(fake_users_db, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@user_route.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@user_route.get("/protected-endpoint/")
async def protected_endpoint(current_user: User = Depends(has_role(["admin"]))):
    return {"message": "You have access to the protected endpoint!"}

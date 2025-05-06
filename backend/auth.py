import asyncpg
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from db import load_db_config
import bcrypt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, status

from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends

SECRET_KEY = "your-secret-key"  # use a real secret in prod
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 300

router = APIRouter()

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None



@router.post("/bootstrap-user")
async def bootstrap_user():
    db_config = load_db_config()

    table_name="users"

    conn = await asyncpg.connect(
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database'],
        host=db_config['host'],
        port=int(db_config['port'])
    )

    # does the user table exist?
    exists = await conn.fetchval(
        """
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = $1
        );
        """,
        table_name
    )

    if exists:
        print(f"\ntable '{table_name}' exists - not creating.\n")
    else:
        print(f"\nCreating table '{table_name}'.\n")

        create_query = f"""
        CREATE TABLE public."{table_name}" (
            id serial4 NOT NULL,
            email text NOT NULL,
            hashed_password text NOT NULL,
            full_name text NULL,
            is_active bool DEFAULT true NULL,
            created_at timestamp DEFAULT CURRENT_TIMESTAMP NULL,
            CONSTRAINT users_email_key UNIQUE (email),
            CONSTRAINT users_pkey PRIMARY KEY (id)
        );
        """

        await conn.execute(create_query)
        print(f"Table '{table_name}' created successfully.")


    # does the bootstrap user exist?
    user_count = await conn.fetchval("SELECT COUNT(*) FROM users")
    if user_count > 0:
        await conn.close()
        raise HTTPException(status_code=403, detail="Users already exist")

    hashed_pw = pwd_context.hash("admin")

    await conn.execute(
        """
        INSERT INTO users (email, hashed_password, full_name)
        VALUES ($1, $2, $3)
        """,
        "admin@example.com",
        hashed_pw,
        "Admin User"
    )

    await conn.close()
    return {"msg": "bootstrap user created"}




@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db_config = load_db_config()
    conn = await asyncpg.connect(**db_config)

    try:
        user = await conn.fetchrow("SELECT * FROM users WHERE email = $1", form_data.username)
        if not user or not pwd_context.verify(form_data.password, user['hashed_password']):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        token_data = {"sub": user["email"]}
        access_token = create_access_token(token_data)
        return {"access_token": access_token, "token_type": "bearer"}
    
    finally:
        await conn.close()



class TokenData(BaseModel):
    email: str | None = None


@router.get("/me")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token: no subject")

        token_data = TokenData(email=email)

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Query the user by email
    db_config = load_db_config()
    conn = await asyncpg.connect(
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database'],
        host=db_config['host'],
        port=int(db_config['port'])
    )

    user = await conn.fetchrow("SELECT id, email, full_name, is_active FROM users WHERE email = $1", token_data.email)
    await conn.close()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return dict(user)





@router.post("/create-user")
async def create_user(user: UserCreate):
    db_config = load_db_config()

    conn = await asyncpg.connect(
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database'],
        host=db_config['host'],
        port=int(db_config['port'])
    )

    try:
        hashed_pw = pwd_context.hash(user.password)

        await conn.execute(
            """
            INSERT INTO users (email, hashed_password, full_name)
            VALUES ($1, $2, $3)
            """,
            user.email,
            hashed_pw,
            user.full_name
        )
        return {"status": "success"}
    
    except asyncpg.UniqueViolationError:
        raise HTTPException(status_code=400, detail="Email already registered")
    finally:
        await conn.close()









def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email: str = payload.get("sub")
        if user_email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_email
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)









# class LoginRequest(BaseModel):
#     email: str
#     password: str

# @router.post("/login_json")
# async def login_json(request: LoginRequest):
#     db_config = load_db_config()
#     conn = await asyncpg.connect(**db_config)

#     try:
#         user = await conn.fetchrow("SELECT * FROM users WHERE email = $1", request.email)
#         if not user or not pwd_context.verify(request.password, user['hashed_password']):
#             raise HTTPException(status_code=401, detail="Invalid email or password")
        
#         token_data = {"sub": user["email"]}  # You can also include user["id"] if needed
#         access_token = create_access_token(token_data)
#         return {"access_token": access_token, "token_type": "bearer"}
    
#     finally:
#         await conn.close()        















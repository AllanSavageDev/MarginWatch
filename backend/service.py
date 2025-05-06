from fastapi import FastAPI
from pydantic import BaseModel
import asyncpg
from db import load_db_config
from auth import router as auth_router
from fastapi import Depends

from auth import oauth2_scheme
from auth import decode_token

# Pydantic model
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

from fastapi.openapi.utils import get_openapi
import logging


#app = FastAPI()
app = FastAPI(root_path="/api")

logging.basicConfig(level=logging.INFO)
logging.info(f"FastAPI root_path: {app.root_path}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)





def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="MarginWatch API",
        version="1.0.0",
        description="API for margin data with secure authentication",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    # "tokenUrl": "/login",
                    "tokenUrl": f"{app.root_path}/login",
                    "scopes": {}
                }
            }
        }
    }
    # for path in openapi_schema["paths"]:
    #     for method in openapi_schema["paths"][path]:
    #         openapi_schema["paths"][path][method]["security"] = [{"OAuth2PasswordBearer": []}]
    # app.openapi_schema = openapi_schema
    # return app.openapi_schema

    # Rewrite all paths to include root_path
    new_paths = {}
    for path, methods in openapi_schema["paths"].items():
        new_paths[f"{app.root_path}{path}"] = methods
    openapi_schema["paths"] = new_paths

    # Apply security globally
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = [{"OAuth2PasswordBearer": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi








class Margin(BaseModel):
    id: int
    inserted_at: datetime
    exchange: str | None
    underlying: str | None
    product_description: str | None
    trading_class: str | None
    intraday_initial: float | None
    intraday_maintenance: float | None
    overnight_initial: float | None
    overnight_maintenance: float | None
    currency: str | None
    has_options: str | None
    short_overnight_initial: float | None
    short_overnight_maintenance: float | None


@app.get("/margins", response_model=list[Margin])
async def get_margins():
    db_config = load_db_config()

    conn = await asyncpg.connect(
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database'],
        host=db_config['host'],
        port=int(db_config['port'])
    )

    try:
        rows = await conn.fetch("SELECT * FROM ib_margins")
        result = []
        for row in rows:
            result.append(Margin(**dict(row)))
        return result

    finally:
        await conn.close()



@app.get("/margins_secure", response_model=list[Margin])
async def get_margins_secure(token: str = Depends(oauth2_scheme)):
    user_email = decode_token(token)  # Just verifying it's valid
    # optional: fetch user_id if you need user-specific access control
    
    db_config = load_db_config()
    conn = await asyncpg.connect(**db_config)

    try:
        rows = await conn.fetch("SELECT * FROM ib_margins")
        return [Margin(**dict(row)) for row in rows]
    finally:
        await conn.close()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apis.routes.fooocus import fooocus_router
from apis.routes.query import query_route
# from apis.routes.users import user_route


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow access from all sources
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all request headers
)

app.include_router(fooocus_router)
app.include_router(query_route)
# app.include_router(user_route)

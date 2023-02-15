from fastapi import FastAPI
from .routes import auth, users,todos, category
from .database import engine
from . import models
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# origins = [
#     "http://localhost",
#     "http://localhost:4200",
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(category.router)
app.include_router(todos.router)

@app.get("/")
def getExample():
    return {"msg":"success"}
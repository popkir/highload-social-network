from fastapi import FastAPI
from app.routers import template_router, user_router


app = FastAPI()

app.include_router(template_router.router, prefix="/template", tags=["template"])
app.include_router(user_router.router, prefix="/user", tags=["user"])

@app.get("/health-check")
def read_root():
    return {"Hello": "World"}


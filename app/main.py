from fastapi import FastAPI
from app.routers import template_router, user_router, auth_router, template_router
from asgi_correlation_id import CorrelationIdMiddleware

app = FastAPI()

from app.utils.logger import logger
app.add_middleware(CorrelationIdMiddleware, header_name="X-Request-ID")

# app.include_router(template_router.router, prefix="/template", tags=["template"])
app.include_router(user_router.router, prefix="/user", tags=["user"])
app.include_router(auth_router.router, tags=["auth"])
app.include_router(template_router.router, prefix="/template", tags=["template"])

@app.on_event("startup")
async def launch():
    logger.info("Starting up")


@app.get("/health-check")
def read_root():
    logger.info("Health check endpoint called")
    return {"Hello": "World"}
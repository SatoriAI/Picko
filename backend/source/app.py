from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from source.endpoints.status import router as status_router
from source.settings import settings


def create_app() -> FastAPI:
    application = FastAPI(
        name="Picko",
        description="Lightweight Secret Santa app for randomized draws and link-based result sharing.",
        docs_url=None,
        redoc_url="/docs",
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.cors_origins],
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    )

    application.include_router(status_router)

    return application


app = create_app()

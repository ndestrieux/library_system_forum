from contextlib import asynccontextmanager
from typing import Callable

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from database.db_conf import engine
from database.models import BaseModel
from exceptions import (
    ForumApiException,
    JWTTokenInvalidException,
    NoPermissionException,
)
from routers import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    BaseModel.metadata.create_all(bind=engine)
    print("Database connected on startup")
    yield
    engine.dispose()
    print("Database disconnected on shutdown")


app = FastAPI(lifespan=lifespan)

app.include_router(router)


def create_exception_handler() -> Callable[[Request, ForumApiException], JSONResponse]:

    async def exception_handler(_: Request, exc: ForumApiException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.STATUS_CODE, content={"detail": exc.message}
        )

    return exception_handler


app.add_exception_handler(
    exc_class_or_status_code=NoPermissionException,
    handler=create_exception_handler(),
)

app.add_exception_handler(
    exc_class_or_status_code=JWTTokenInvalidException,
    handler=create_exception_handler(),
)

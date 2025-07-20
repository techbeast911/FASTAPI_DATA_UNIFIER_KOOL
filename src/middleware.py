from fastapi import FastAPI
from fastapi.requests import Request
import time
import logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

logger = logging.getLogger('uvicorn.access')
logger.disabled = True  # Disable default logging to avoid duplicate logs

def register_middleware(app: FastAPI):
    """
    Registers middleware for the FastAPI application.
    This middleware logs the time taken for each request.
    """
    @app.middleware("http")
    async def custom_logging(request: Request, call_next):
        start_time = time.time()
        print("Before",start_time)
        response = await call_next(request)

        processing_time = time.time() - start_time
        message = f"{request.client.host}:{request.method} - {request.url.path} - {response.status_code} - completed {processing_time:.4f}s"
        print(message)
        return response


    app.add_middleware(CORSMiddleware,
        allow_origins=[
        "http://localhost:3000",
        "https://kool-portal.azurewebsites.net",
        "http://localhost:8000"
    ],
        allow_methods = ["*"] ,
        allow_headers = ["*"],
        allow_credentials = True,)


    app.add_middleware(TrustedHostMiddleware, allowed_hosts=[
        "kool-portal.azurewebsites.net",
        "localhost",
        "127.0.0.1"
    ])
        
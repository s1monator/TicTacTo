from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ._routes import define_routes

_app: FastAPI | None = None


def build_app():
    global _app
    if not _app:
        _app = FastAPI(
            title="TicTacToe Game API",
            description="A RESTful API for playing TicTacToe games with game history and move tracking",
            version="1.0.0",
            contact={
                "name": "TicTacToe API Support",
                "url": "https://github.com/",
            },
            license_info={
                "name": "GPL-3.0",
            }
        )
        
        # Add CORS middleware
        _app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        define_routes(_app)

    return _app

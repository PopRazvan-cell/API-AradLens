import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import admins, auth, invites, locations, tours
from app.core.config import settings

app = FastAPI(title="AradLens API", version="0.1.0")

app.include_router(auth.router)
app.include_router(admins.router)
app.include_router(invites.router)
app.include_router(locations.router)
app.include_router(tours.router)

os.makedirs(settings.media_dir, exist_ok=True)
app.mount("/media", StaticFiles(directory=settings.media_dir), name="media")


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

import sys
from pathlib import Path
from contextlib import asynccontextmanager



sys.path.append(str(Path(__file__).parent.parent))


from src.api.auth import router as router_auth
from src.api.hotels import router as router_hotels
from src.api.rooms import router as router_rooms
from src.api.bookings import router as router_bookings
from src.api.facilities import router as router_facilities

from src.init import redis_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_manager.connector()
    yield
    await redis_manager.close()

app = FastAPI(lifespan=lifespan)

app.include_router(router_auth)
app.include_router(router_hotels)
app.include_router(router_rooms)
app.include_router(router_bookings)
app.include_router(router_facilities)


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <a href="http://127.0.0.1:8000/docs">Docs</a><br>
    <a href="http://127.0.0.1:8000/redoc">ReDoc</a>
    """


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)

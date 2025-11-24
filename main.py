from fastapi import FastAPI

from db.base import Base
from db.session import engine
import models.user       # noqa: F401
import models.airport    # noqa: F401
import models.connection # noqa: F401
import models.route      # noqa: F401

from routers import auth, routes , airports,profile


app = FastAPI(title="Complejidad Routes API")


@app.get("/")
async def root():
    return {"message": "API Complejidad funcionando"}


app.include_router(auth.router)
app.include_router(routes.router)
app.include_router(airports.router)  
app.include_router(profile.router)  


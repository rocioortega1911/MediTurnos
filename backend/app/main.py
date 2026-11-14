from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.models import models
from app.routers import auth, especialidad, pacientes, medicos, turnos, reportes
from app.security import get_current_user, require_roles

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(
    title="MediTurnos API",
    description="Backend REST API/FastAPI,con base de datos en MySQL y Seguridad JWT",
    version="BETA 1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router público de Autenticación (Registro y Login)

app.include_router(auth.router)

# Routers protegidos con JWT (requieren sesión iniciada)

app.include_router(
    especialidad.router,
    dependencies=[Depends(get_current_user)]
)
app.include_router(
    pacientes.router,
    dependencies=[Depends(get_current_user)]
)
app.include_router(
    medicos.router,
    dependencies=[Depends(get_current_user)]
)
app.include_router(
    turnos.router,
    dependencies=[Depends(get_current_user)]
)

# Router de Reportes restringido por Rol

app.include_router(
    reportes.router,
    dependencies=[Depends(require_roles(["administrador", "recepcionista", "medico"]))]
)

@app.get("/", tags=["General"])
async def read_root():
    return {
        "status": "ok",
        "proyecto": "MediTurnos",
        "database": "MySQL Async (aiomysql)",
        "auth": "JWT Bearer habilitado"
    }
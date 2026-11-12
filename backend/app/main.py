from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import pacientes, medicos, turnos

app = FastAPI(
    title="API Mediturnos",
    description="Backend REST API/FastAPI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar los routers de las entidades principales
app.include_router(pacientes.router)
app.include_router(medicos.router)
app.include_router(turnos.router)

@app.get("/", tags=["General"])
def read_root():
    return {"status": "ok", "message": "API funcionando correctamente"}
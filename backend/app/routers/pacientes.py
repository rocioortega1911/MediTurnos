from fastapi import APIRouter, HTTPException, status
from typing import List
from app.schemas.schemas import PacienteCreate, PacienteUpdate, PacienteResponse

router = APIRouter(
    prefix="/pacientes",
    tags=["Pacientes"]
)

# Almacenamiento temporal (hasta conectar la BD en el siguiente punto)
pacientes_db = []
contador_id = 1

# READ ALL (GET)
@router.get("/", response_model=List[PacienteResponse], status_code=status.HTTP_200_OK)
def obtener_pacientes():
    return pacientes_db

# READ ONE (GET by ID)
@router.get("/{paciente_id}", response_model=PacienteResponse, status_code=status.HTTP_200_OK)
def obtener_paciente(paciente_id: int):
    for paciente in pacientes_db:
        if paciente["id"] == paciente_id:
            return paciente
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado")

# CREATE (POST)
@router.post("/", response_model=PacienteResponse, status_code=status.HTTP_201_CREATED)
def crear_paciente(paciente: PacienteCreate):
    global contador_id
    # Verificar DNI duplicado
    for p in pacientes_db:
        if p["dni"] == paciente.dni:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe un paciente con ese DNI")
            
    nuevo_paciente = paciente.model_dump()
    nuevo_paciente["id"] = contador_id
    contador_id += 1
    pacientes_db.append(nuevo_paciente)
    return nuevo_paciente

# UPDATE (PUT)
@router.put("/{paciente_id}", response_model=PacienteResponse, status_code=status.HTTP_200_OK)
def actualizar_paciente(paciente_id: int, datos: PacienteUpdate):
    for index, paciente in enumerate(pacientes_db):
        if paciente["id"] == paciente_id:
            datos_actualizados = datos.model_dump(exclude_unset=True)
            pacientes_db[index].update(datos_actualizados)
            return pacientes_db[index]
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado")

# DELETE (DELETE)
@router.delete("/{paciente_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_paciente(paciente_id: int):
    for index, paciente in enumerate(pacientes_db):
        if paciente["id"] == paciente_id:
            pacientes_db.pop(index)
            return
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado")
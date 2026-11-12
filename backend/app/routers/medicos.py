from fastapi import APIRouter, HTTPException, status
from typing import List
from app.schemas.schemas import MedicoCreate, MedicoUpdate, MedicoResponse

router = APIRouter(
    prefix="/medicos",
    tags=["Médicos"]
)

medicos_db = []
contador_id = 1

@router.get("/", response_model=List[MedicoResponse])
def obtener_medicos():
    return medicos_db

@router.get("/{medico_id}", response_model=MedicoResponse)
def obtener_medico(medico_id: int):
    for medico in medicos_db:
        if medico["id"] == medico_id:
            return medico
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Médico no encontrado")

@router.post("/", response_model=MedicoResponse, status_code=status.HTTP_201_CREATED)
def crear_medico(medico: MedicoCreate):
    global contador_id
    for m in medicos_db:
        if m["matricula"] == medico.matricula:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe un médico con esa matrícula")
            
    nuevo_medico = medico.model_dump()
    nuevo_medico["id"] = contador_id
    contador_id += 1
    medicos_db.append(nuevo_medico)
    return nuevo_medico

@router.put("/{medico_id}", response_model=MedicoResponse)
def actualizar_medico(medico_id: int, datos: MedicoUpdate):
    for index, medico in enumerate(medicos_db):
        if medico["id"] == medico_id:
            datos_actualizados = datos.model_dump(exclude_unset=True)
            medicos_db[index].update(datos_actualizados)
            return medicos_db[index]
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Médico no encontrado")

@router.delete("/{medico_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_medico(medico_id: int):
    for index, medico in enumerate(medicos_db):
        if medico["id"] == medico_id:
            medicos_db.pop(index)
            return
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Médico no encontrado")
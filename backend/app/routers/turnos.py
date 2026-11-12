from fastapi import APIRouter, HTTPException, status
from typing import List
from app.schemas.schemas import TurnoCreate, TurnoUpdate, TurnoResponse
from app.routers.pacientes import pacientes_db
from app.routers.medicos import medicos_db

router = APIRouter(
    prefix="/turnos",
    tags=["Turnos"]
)

turnos_db = []
contador_id = 1

@router.get("/", response_model=List[TurnoResponse])
def obtener_turnos():
    return turnos_db

@router.get("/{turno_id}", response_model=TurnoResponse)
def obtener_turno(turno_id: int):
    for turno in turnos_db:
        if turno["id"] == turno_id:
            return turno
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Turno no encontrado")

@router.post("/", response_model=TurnoResponse, status_code=status.HTTP_201_CREATED)
def crear_turno(turno: TurnoCreate):
    global contador_id
    
    # Validar que el paciente exista
    if not any(p["id"] == turno.paciente_id for p in pacientes_db):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El paciente indicado no existe")
        
    # Validar que el médico exista
    if not any(m["id"] == turno.medico_id for m in medicos_db):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El médico indicado no existe")
        
    # Validar que el médico no tenga otro turno en la misma fecha y hora (salvo que esté cancelado)
    for t in turnos_db:
        if (t["medico_id"] == turno.medico_id and 
            t["fecha"] == turno.fecha and 
            t["hora"] == turno.hora and 
            t["estado"] != "cancelado"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="El médico ya tiene un turno asignado en esa fecha y horario"
            )

    nuevo_turno = turno.model_dump()
    nuevo_turno["id"] = contador_id
    contador_id += 1
    turnos_db.append(nuevo_turno)
    return nuevo_turno

@router.put("/{turno_id}", response_model=TurnoResponse)
def actualizar_turno(turno_id: int, datos: TurnoUpdate):
    for index, turno in enumerate(turnos_db):
        if turno["id"] == turno_id:
            datos_actualizados = datos.model_dump(exclude_unset=True)
            turnos_db[index].update(datos_actualizados)
            return turnos_db[index]
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Turno no encontrado")

@router.delete("/{turno_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_turno(turno_id: int):
    for index, turno in enumerate(turnos_db):
        if turno["id"] == turno_id:
            turnos_db.pop(index)
            return
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Turno no encontrado")
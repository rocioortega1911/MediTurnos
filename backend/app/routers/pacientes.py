from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from typing import List
from app.database import get_db
from app.models.models import PacienteModel
from app.schemas.schemas import PacienteCreate, PacienteUpdate, PacienteResponse

router = APIRouter(prefix="/pacientes", tags=["Pacientes"])

@router.get("/", response_model=List[PacienteResponse])
async def obtener_pacientes(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PacienteModel))
    return result.scalars().all()

@router.get("/{paciente_id}", response_model=PacienteResponse)
async def obtener_paciente(paciente_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PacienteModel).where(PacienteModel.id == paciente_id))
    paciente = result.scalar_one_or_none()
    if not paciente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado")
    return paciente

@router.post("/", response_model=PacienteResponse, status_code=status.HTTP_201_CREATED)
async def crear_paciente(paciente: PacienteCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PacienteModel).where(PacienteModel.dni == paciente.dni))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe un paciente con ese DNI")
        
    nuevo_paciente = PacienteModel(**paciente.model_dump())
    db.add(nuevo_paciente)
    await db.commit()
    await db.refresh(nuevo_paciente)
    return nuevo_paciente

@router.put("/{paciente_id}", response_model=PacienteResponse)
async def actualizar_paciente(paciente_id: int, datos: PacienteUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PacienteModel).where(PacienteModel.id == paciente_id))
    paciente = result.scalar_one_or_none()
    if not paciente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado")
        
    for key, value in datos.model_dump(exclude_unset=True).items():
        setattr(paciente, key, value)
    await db.commit()
    await db.refresh(paciente)
    return paciente

@router.delete("/{paciente_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_paciente(paciente_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PacienteModel).where(PacienteModel.id == paciente_id))
    paciente = result.scalar_one_or_none()
    if not paciente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado")
    try:
        await db.delete(paciente)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar el paciente porque tiene turnos registrados"
        )
    return
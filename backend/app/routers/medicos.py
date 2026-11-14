from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from typing import List
from app.database import get_db
from app.models.models import MedicoModel, EspecialidadModel
from app.schemas.schemas import MedicoCreate, MedicoUpdate, MedicoResponse

router = APIRouter(prefix="/medicos", tags=["Médicos"])

@router.get("/", response_model=List[MedicoResponse])
async def obtener_medicos(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MedicoModel))
    return result.scalars().all()

@router.get("/{medico_id}", response_model=MedicoResponse)
async def obtener_medico(medico_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MedicoModel).where(MedicoModel.id == medico_id))
    medico = result.scalar_one_or_none()
    if not medico:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Médico no encontrado")
    return medico

@router.post("/", response_model=MedicoResponse, status_code=status.HTTP_201_CREATED)
async def crear_medico(medico: MedicoCreate, db: AsyncSession = Depends(get_db)):
    res_esp = await db.execute(select(EspecialidadModel).where(EspecialidadModel.id == medico.especialidad_id))
    if not res_esp.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La especialidad indicada no existe")
        
    res_mat = await db.execute(select(MedicoModel).where(MedicoModel.matricula == medico.matricula))
    if res_mat.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe un médico con esa matrícula")
        
    nuevo_medico = MedicoModel(**medico.model_dump())
    db.add(nuevo_medico)
    await db.commit()
    await db.refresh(nuevo_medico)
    return nuevo_medico

@router.put("/{medico_id}", response_model=MedicoResponse)
async def actualizar_medico(medico_id: int, datos: MedicoUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MedicoModel).where(MedicoModel.id == medico_id))
    medico = result.scalar_one_or_none()
    if not medico:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Médico no encontrado")
        
    for key, value in datos.model_dump(exclude_unset=True).items():
        setattr(medico, key, value)
    await db.commit()
    await db.refresh(medico)
    return medico

@router.delete("/{medico_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_medico(medico_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MedicoModel).where(MedicoModel.id == medico_id))
    medico = result.scalar_one_or_none()
    if not medico:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Médico no encontrado")
    try:
        await db.delete(medico)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar el médico porque tiene turnos asociados"
        )
    return
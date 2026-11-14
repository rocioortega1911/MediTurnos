from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from typing import List
from app.database import get_db
from app.models.models import EspecialidadModel
from app.schemas.schemas import EspecialidadCreate, EspecialidadUpdate, EspecialidadResponse

router = APIRouter(prefix="/especialidades", tags=["Especialidades"])

@router.get("/", response_model=List[EspecialidadResponse])
async def obtener_especialidades(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EspecialidadModel))
    return result.scalars().all()

@router.get("/{especialidad_id}", response_model=EspecialidadResponse)
async def obtener_especialidad(especialidad_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EspecialidadModel).where(EspecialidadModel.id == especialidad_id))
    esp = result.scalar_one_or_none()
    if not esp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Especialidad no encontrada")
    return esp

@router.post("/", response_model=EspecialidadResponse, status_code=status.HTTP_201_CREATED)
async def crear_especialidad(especialidad: EspecialidadCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EspecialidadModel).where(EspecialidadModel.nombre == especialidad.nombre))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe esa especialidad")
        
    nueva = EspecialidadModel(**especialidad.model_dump())
    db.add(nueva)
    await db.commit()
    await db.refresh(nueva)
    return nueva

@router.put("/{especialidad_id}", response_model=EspecialidadResponse)
async def actualizar_especialidad(especialidad_id: int, datos: EspecialidadUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EspecialidadModel).where(EspecialidadModel.id == especialidad_id))
    esp = result.scalar_one_or_none()
    if not esp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Especialidad no encontrada")
        
    for key, value in datos.model_dump(exclude_unset=True).items():
        setattr(esp, key, value)
    await db.commit()
    await db.refresh(esp)
    return esp

@router.delete("/{especialidad_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_especialidad(especialidad_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EspecialidadModel).where(EspecialidadModel.id == especialidad_id))
    esp = result.scalar_one_or_none()
    if not esp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Especialidad no encontrada")
    try:
        await db.delete(esp)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar la especialidad porque tiene médicos asociados"
        )
    return
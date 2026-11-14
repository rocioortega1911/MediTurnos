from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from sqlalchemy.exc import OperationalError, IntegrityError, DBAPIError
from typing import List
from app.database import get_db
from app.models.models import TurnoModel
from app.schemas.schemas import TurnoCreate, TurnoUpdate, TurnoResponse

router = APIRouter(prefix="/turnos", tags=["Turnos"])

@router.get("/", response_model=List[TurnoResponse])
async def obtener_turnos(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TurnoModel))
    return result.scalars().all()

@router.get("/{turno_id}", response_model=TurnoResponse)
async def obtener_turno(turno_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TurnoModel).where(TurnoModel.id == turno_id))
    turno = result.scalar_one_or_none()
    if not turno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Turno no encontrado")
    return turno

@router.post("/", response_model=TurnoResponse, status_code=status.HTTP_201_CREATED)
async def crear_turno(turno: TurnoCreate, db: AsyncSession = Depends(get_db)):
    try:
        sql_proc = text("""
            CALL registrar_turno(:paciente_id, :medico_id, :fecha_hora, :motivo)
        """)
        await db.execute(sql_proc, {
            "paciente_id": turno.paciente_id,
            "medico_id": turno.medico_id,
            "fecha_hora": turno.fecha_hora,
            "motivo": turno.motivo
        })
        await db.commit()

        result = await db.execute(
            select(TurnoModel).where(
                TurnoModel.medico_id == turno.medico_id,
                TurnoModel.fecha_hora == turno.fecha_hora
            )
        )
        return result.scalar_one()

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El médico ya tiene un turno asignado en esa fecha y hora (uq_medico_fecha)"
        )
    except (OperationalError, DBAPIError) as e:
        await db.rollback()
        mensaje_mysql = str(e.orig) if hasattr(e, "orig") else str(e)
        if "El paciente no existe" in mensaje_mysql:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El paciente no existe")
        if "El médico no existe o está inactivo" in mensaje_mysql:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El médico no existe o está inactivo")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error en base de datos: {mensaje_mysql}")

@router.put("/{turno_id}", response_model=TurnoResponse)
async def actualizar_turno(turno_id: int, datos: TurnoUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TurnoModel).where(TurnoModel.id == turno_id))
    turno = result.scalar_one_or_none()
    if not turno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Turno no encontrado")
        
    for key, value in datos.model_dump(exclude_unset=True).items():
        setattr(turno, key, value)
    try:
        await db.commit()
        await db.refresh(turno)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conflicto de horario: el médico ya posee un turno en esa fecha y hora"
        )
    return turno

@router.delete("/{turno_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_turno(turno_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TurnoModel).where(TurnoModel.id == turno_id))
    turno = result.scalar_one_or_none()
    if not turno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Turno no encontrado")
    await db.delete(turno)
    await db.commit()
    return
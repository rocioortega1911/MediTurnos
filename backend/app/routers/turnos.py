from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from app.database import get_db
from app.models.models import TurnoModel, PacienteModel, MedicoModel
from app.schemas.schemas import TurnoCreate, TurnoUpdate, TurnoResponse

router = APIRouter(prefix="/turnos", tags=["Turnos"])

@router.get("/", response_model=List[TurnoResponse])
def obtener_turnos(db: Session = Depends(get_db)):
    return db.query(TurnoModel).all()

@router.get("/{turno_id}", response_model=TurnoResponse)
def obtener_turno(turno_id: int, db: Session = Depends(get_db)):
    turno = db.query(TurnoModel).filter(TurnoModel.id == turno_id).first()
    if not turno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Turno no encontrado")
    return turno

@router.post("/", response_model=TurnoResponse, status_code=status.HTTP_201_CREATED)
def crear_turno(turno: TurnoCreate, db: Session = Depends(get_db)):
    if not db.query(PacienteModel).filter(PacienteModel.id == turno.paciente_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El paciente indicado no existe")
        
    medico = db.query(MedicoModel).filter(MedicoModel.id == turno.medico_id).first()
    if not medico:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El médico indicado no existe")
    if not medico.activo:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El médico no se encuentra activo")

    nuevo_turno = TurnoModel(**turno.model_dump())
    try:
        db.add(nuevo_turno)
        db.commit()
        db.refresh(nuevo_turno)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El médico ya tiene un turno asignado en esa fecha y hora exacta (uq_medico_fecha)"
        )
    return nuevo_turno

@router.put("/{turno_id}", response_model=TurnoResponse)
def actualizar_turno(turno_id: int, datos: TurnoUpdate, db: Session = Depends(get_db)):
    turno = db.query(TurnoModel).filter(TurnoModel.id == turno_id).first()
    if not turno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Turno no encontrado")
    for key, value in datos.model_dump(exclude_unset=True).items():
        setattr(turno, key, value)
    try:
        db.commit()
        db.refresh(turno)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conflicto de horario: el médico ya posee un turno en esa fecha y hora"
        )
    return turno

@router.delete("/{turno_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_turno(turno_id: int, db: Session = Depends(get_db)):
    turno = db.query(TurnoModel).filter(TurnoModel.id == turno_id).first()
    if not turno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Turno no encontrado")
    db.delete(turno)
    db.commit()
    return
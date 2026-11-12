from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from app.database import get_db
from app.models.models import MedicoModel, EspecialidadModel
from app.schemas.schemas import MedicoCreate, MedicoUpdate, MedicoResponse

router = APIRouter(prefix="/medicos", tags=["Médicos"])

@router.get("/", response_model=List[MedicoResponse])
def obtener_medicos(db: Session = Depends(get_db)):
    return db.query(MedicoModel).all()

@router.get("/{medico_id}", response_model=MedicoResponse)
def obtener_medico(medico_id: int, db: Session = Depends(get_db)):
    medico = db.query(MedicoModel).filter(MedicoModel.id == medico_id).first()
    if not medico:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Médico no encontrado")
    return medico

@router.post("/", response_model=MedicoResponse, status_code=status.HTTP_201_CREATED)
def crear_medico(medico: MedicoCreate, db: Session = Depends(get_db)):
    if not db.query(EspecialidadModel).filter(EspecialidadModel.id == medico.especialidad_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La especialidad indicada no existe")
    if db.query(MedicoModel).filter(MedicoModel.matricula == medico.matricula).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe un médico con esa matrícula")
        
    nuevo_medico = MedicoModel(**medico.model_dump())
    db.add(nuevo_medico)
    db.commit()
    db.refresh(nuevo_medico)
    return nuevo_medico

@router.put("/{medico_id}", response_model=MedicoResponse)
def actualizar_medico(medico_id: int, datos: MedicoUpdate, db: Session = Depends(get_db)):
    medico = db.query(MedicoModel).filter(MedicoModel.id == medico_id).first()
    if not medico:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Médico no encontrado")
    for key, value in datos.model_dump(exclude_unset=True).items():
        setattr(medico, key, value)
    db.commit()
    db.refresh(medico)
    return medico

@router.delete("/{medico_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_medico(medico_id: int, db: Session = Depends(get_db)):
    medico = db.query(MedicoModel).filter(MedicoModel.id == medico_id).first()
    if not medico:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Médico no encontrado")
    try:
        db.delete(medico)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar el médico porque tiene turnos asociados"
        )
    return
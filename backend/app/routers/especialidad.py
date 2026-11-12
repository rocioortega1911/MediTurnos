from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from app.database import get_db
from app.models.models import EspecialidadModel
from app.schemas.schemas import EspecialidadCreate, EspecialidadUpdate, EspecialidadResponse

router = APIRouter(prefix="/especialidades", tags=["Especialidades"])

@router.get("/", response_model=List[EspecialidadResponse])
def obtener_especialidades(db: Session = Depends(get_db)):
    return db.query(EspecialidadModel).all()

@router.get("/{especialidad_id}", response_model=EspecialidadResponse)
def obtener_especialidad(especialidad_id: int, db: Session = Depends(get_db)):
    esp = db.query(EspecialidadModel).filter(EspecialidadModel.id == especialidad_id).first()
    if not esp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Especialidad no encontrada")
    return esp

@router.post("/", response_model=EspecialidadResponse, status_code=status.HTTP_201_CREATED)
def crear_especialidad(especialidad: EspecialidadCreate, db: Session = Depends(get_db)):
    existe = db.query(EspecialidadModel).filter(EspecialidadModel.nombre == especialidad.nombre).first()
    if existe:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe esa especialidad")
    nueva = EspecialidadModel(**especialidad.model_dump())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@router.put("/{especialidad_id}", response_model=EspecialidadResponse)
def actualizar_especialidad(especialidad_id: int, datos: EspecialidadUpdate, db: Session = Depends(get_db)):
    esp = db.query(EspecialidadModel).filter(EspecialidadModel.id == especialidad_id).first()
    if not esp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Especialidad no encontrada")
    for key, value in datos.model_dump(exclude_unset=True).items():
        setattr(esp, key, value)
    db.commit()
    db.refresh(esp)
    return esp

@router.delete("/{especialidad_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_especialidad(especialidad_id: int, db: Session = Depends(get_db)):
    esp = db.query(EspecialidadModel).filter(EspecialidadModel.id == especialidad_id).first()
    if not esp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Especialidad no encontrada")
    try:
        db.delete(esp)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar la especialidad porque tiene médicos asociados"
        )
    return
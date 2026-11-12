from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from app.database import get_db
from app.models.models import PacienteModel
from app.schemas.schemas import PacienteCreate, PacienteUpdate, PacienteResponse

router = APIRouter(prefix="/pacientes", tags=["Pacientes"])

@router.get("/", response_model=List[PacienteResponse])
def obtener_pacientes(db: Session = Depends(get_db)):
    return db.query(PacienteModel).all()

@router.get("/{paciente_id}", response_model=PacienteResponse)
def obtener_paciente(paciente_id: int, db: Session = Depends(get_db)):
    paciente = db.query(PacienteModel).filter(PacienteModel.id == paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado")
    return paciente

@router.post("/", response_model=PacienteResponse, status_code=status.HTTP_201_CREATED)
def crear_paciente(paciente: PacienteCreate, db: Session = Depends(get_db)):
    existe = db.query(PacienteModel).filter(PacienteModel.dni == paciente.dni).first()
    if existe:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe un paciente con ese DNI")
    nuevo_paciente = PacienteModel(**paciente.model_dump())
    db.add(nuevo_paciente)
    db.commit()
    db.refresh(nuevo_paciente)
    return nuevo_paciente

@router.put("/{paciente_id}", response_model=PacienteResponse)
def actualizar_paciente(paciente_id: int, datos: PacienteUpdate, db: Session = Depends(get_db)):
    paciente = db.query(PacienteModel).filter(PacienteModel.id == paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado")
    for key, value in datos.model_dump(exclude_unset=True).items():
        setattr(paciente, key, value)
    db.commit()
    db.refresh(paciente)
    return paciente

@router.delete("/{paciente_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_paciente(paciente_id: int, db: Session = Depends(get_db)):
    paciente = db.query(PacienteModel).filter(PacienteModel.id == paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado")
    try:
        db.delete(paciente)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar el paciente porque tiene turnos registrados"
        )
    return
from pydantic import BaseModel, EmailStr, Field
from datetime import date, time
from typing import Optional

# ==========================================
# ESQUEMAS: PACIENTE
# ==========================================
class PacienteBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=50, examples=["Juan"])
    apellido: str = Field(..., min_length=2, max_length=50, examples=["Pérez"])
    dni: str = Field(..., min_length=7, max_length=10, examples=["40123456"])
    email: EmailStr = Field(..., examples=["juan.perez@email.com"])
    telefono: Optional[str] = Field(None, examples=["3804123456"])
    obra_social: Optional[str] = Field("Particular", examples=["OSDE"])

class PacienteCreate(PacienteBase):
    pass

class PacienteUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=50)
    apellido: Optional[str] = Field(None, min_length=2, max_length=50)
    dni: Optional[str] = Field(None, min_length=7, max_length=10)
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    obra_social: Optional[str] = None

class PacienteResponse(PacienteBase):
    id: int

    class Config:
        from_attributes = True


# ==========================================
# ESQUEMAS: MÉDICO
# ==========================================
class MedicoBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=50, examples=["María"])
    apellido: str = Field(..., min_length=2, max_length=50, examples=["Gómez"])
    matricula: str = Field(..., min_length=3, max_length=20, examples=["MP-1234"])
    especialidad: str = Field(..., min_length=3, max_length=50, examples=["Cardiología"])
    email: EmailStr = Field(..., examples=["m.gomez@mediturnos.com"])

class MedicoCreate(MedicoBase):
    pass

class MedicoUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    matricula: Optional[str] = None
    especialidad: Optional[str] = None
    email: Optional[EmailStr] = None

class MedicoResponse(MedicoBase):
    id: int

    class Config:
        from_attributes = True


# ==========================================
# ESQUEMAS: TURNO
# ==========================================
class TurnoBase(BaseModel):
    paciente_id: int = Field(..., examples=[1])
    medico_id: int = Field(..., examples=[1])
    fecha: date = Field(..., examples=["2026-11-20"])
    hora: time = Field(..., examples=["09:30:00"])
    motivo: Optional[str] = Field(None, max_length=200, examples=["Control anual"])
    estado: str = Field("pendiente", examples=["pendiente", "confirmado", "cancelado", "completado"])

class TurnoCreate(TurnoBase):
    pass

class TurnoUpdate(BaseModel):
    paciente_id: Optional[int] = None
    medico_id: Optional[int] = None
    fecha: Optional[date] = None
    hora: Optional[time] = None
    motivo: Optional[str] = None
    estado: Optional[str] = None

class TurnoResponse(TurnoBase):
    id: int

    class Config:
        from_attributes = True
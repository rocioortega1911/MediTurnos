from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
from typing import Optional, Literal

# ==========================================
# 1. ESQUEMAS: ESPECIALIDADES
# ==========================================
class EspecialidadBase(BaseModel):
    nombre: str = Field(..., max_length=100, examples=["Cardiología"])
    descripcion: Optional[str] = Field(None, max_length=255, examples=["Atención del sistema cardiovascular"])

class EspecialidadCreate(EspecialidadBase):
    pass

class EspecialidadUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=255)

class EspecialidadResponse(EspecialidadBase):
    id: int

    class Config:
        from_attributes = True


# ==========================================
# 2. ESQUEMAS: PACIENTES
# ==========================================
class PacienteBase(BaseModel):
    usuario_id: Optional[int] = Field(None, examples=[None])
    dni: str = Field(..., max_length=15, examples=["40123456"])
    nombre: str = Field(..., max_length=80, examples=["Juan"])
    apellido: str = Field(..., max_length=80, examples=["Pérez"])
    fecha_nacimiento: Optional[date] = Field(None, examples=["1998-05-14"])
    telefono: Optional[str] = Field(None, max_length=25, examples=["3804123456"])
    email: Optional[EmailStr] = Field(None, examples=["juan.perez@email.com"])
    direccion: Optional[str] = Field(None, max_length=150, examples=["Av. San Martín 123"])

class PacienteCreate(PacienteBase):
    pass

class PacienteUpdate(BaseModel):
    usuario_id: Optional[int] = None
    dni: Optional[str] = Field(None, max_length=15)
    nombre: Optional[str] = Field(None, max_length=80)
    apellido: Optional[str] = Field(None, max_length=80)
    fecha_nacimiento: Optional[date] = None
    telefono: Optional[str] = Field(None, max_length=25)
    email: Optional[EmailStr] = None
    direccion: Optional[str] = Field(None, max_length=150)

class PacienteResponse(PacienteBase):
    id: int

    class Config:
        from_attributes = True


# ==========================================
# 3. ESQUEMAS: MÉDICOS
# ==========================================
class MedicoBase(BaseModel):
    usuario_id: Optional[int] = Field(None, examples=[None])
    especialidad_id: int = Field(..., examples=[1])
    matricula: str = Field(..., max_length=30, examples=["MP-1234"])
    nombre: str = Field(..., max_length=80, examples=["María"])
    apellido: str = Field(..., max_length=80, examples=["Gómez"])
    telefono: Optional[str] = Field(None, max_length=25, examples=["3804998877"])
    email: Optional[EmailStr] = Field(None, examples=["m.gomez@mediturnos.com"])
    activo: bool = Field(True, examples=[True])

class MedicoCreate(MedicoBase):
    pass

class MedicoUpdate(BaseModel):
    usuario_id: Optional[int] = None
    especialidad_id: Optional[int] = None
    matricula: Optional[str] = Field(None, max_length=30)
    nombre: Optional[str] = Field(None, max_length=80)
    apellido: Optional[str] = Field(None, max_length=80)
    telefono: Optional[str] = Field(None, max_length=25)
    email: Optional[EmailStr] = None
    activo: Optional[bool] = None

class MedicoResponse(MedicoBase):
    id: int

    class Config:
        from_attributes = True


# ==========================================
# 4. ESQUEMAS: TURNOS
# ==========================================
EstadoTurno = Literal['pendiente', 'confirmado', 'cancelado', 'atendido']

class TurnoBase(BaseModel):
    paciente_id: int = Field(..., examples=[1])
    medico_id: int = Field(..., examples=[1])
    fecha_hora: datetime = Field(..., examples=["2026-11-20T09:30:00"])
    motivo: Optional[str] = Field(None, max_length=255, examples=["Consulta general"])
    estado: EstadoTurno = Field("pendiente", examples=["pendiente"])

class TurnoCreate(TurnoBase):
    pass

class TurnoUpdate(BaseModel):
    paciente_id: Optional[int] = None
    medico_id: Optional[int] = None
    fecha_hora: Optional[datetime] = None
    motivo: Optional[str] = Field(None, max_length=255)
    estado: Optional[EstadoTurno] = None

class TurnoResponse(TurnoBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
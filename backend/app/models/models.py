from sqlalchemy import (
    Column, Integer, String, Date, DateTime, Boolean, Enum,
    ForeignKey, TIMESTAMP, UniqueConstraint, text
)
from sqlalchemy.orm import relationship
from app.database import Base

class UsuarioModel(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)
    rol = Column(
        Enum('administrador', 'recepcionista', 'medico', 'paciente', name='rol_enum'),
        nullable=False,
        default='paciente'
    )
    activo = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    paciente = relationship("PacienteModel", back_populates="usuario", uselist=False)
    medico = relationship("MedicoModel", back_populates="usuario", uselist=False)


class PacienteModel(Base):
    __tablename__ = "pacientes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), unique=True, nullable=True)
    dni = Column(String(15), nullable=False, unique=True)
    nombre = Column(String(80), nullable=False)
    apellido = Column(String(80), nullable=False)
    fecha_nacimiento = Column(Date, nullable=True)
    telefono = Column(String(25), nullable=True)
    email = Column(String(100), nullable=True)
    direccion = Column(String(150), nullable=True)

    usuario = relationship("UsuarioModel", back_populates="paciente")
    turnos = relationship("TurnoModel", back_populates="paciente")


class EspecialidadModel(Base):
    __tablename__ = "especialidades"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, unique=True)
    descripcion = Column(String(255), nullable=True)

    medicos = relationship("MedicoModel", back_populates="especialidad")


class MedicoModel(Base):
    __tablename__ = "medicos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), unique=True, nullable=True)
    especialidad_id = Column(Integer, ForeignKey("especialidades.id", ondelete="RESTRICT"), nullable=False)
    matricula = Column(String(30), nullable=False, unique=True)
    nombre = Column(String(80), nullable=False)
    apellido = Column(String(80), nullable=False)
    telefono = Column(String(25), nullable=True)
    email = Column(String(100), nullable=True)
    activo = Column(Boolean, nullable=False, default=True)

    usuario = relationship("UsuarioModel", back_populates="medico")
    especialidad = relationship("EspecialidadModel", back_populates="medicos")
    turnos = relationship("TurnoModel", back_populates="medico")


class TurnoModel(Base):
    __tablename__ = "turnos"
    __table_args__ = (
        UniqueConstraint('medico_id', 'fecha_hora', name='uq_medico_fecha'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id", ondelete="RESTRICT"), nullable=False)
    medico_id = Column(Integer, ForeignKey("medicos.id", ondelete="RESTRICT"), nullable=False)
    fecha_hora = Column(DateTime, nullable=False)
    motivo = Column(String(255), nullable=True)
    estado = Column(
        Enum('pendiente', 'confirmado', 'cancelado', 'atendido', name='estado_turno_enum'),
        nullable=False,
        default='pendiente'
    )
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
    )

    paciente = relationship("PacienteModel", back_populates="turnos")
    medico = relationship("MedicoModel", back_populates="turnos")
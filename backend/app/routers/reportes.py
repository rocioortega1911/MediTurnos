from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db

router = APIRouter(
    prefix="/reportes",
    tags=["Reportes y Consultas SQL (Punto 3)"]
)

# =========================================================================
# CONSULTA 1: INNER JOIN (4 tablas: turnos + pacientes + medicos + especialidades)
# =========================================================================
@router.get("/turnos-detallados", summary="1. Consulta con INNER JOIN")
def obtener_turnos_detallados(db: Session = Depends(get_db)):
    sql = text("""
        SELECT 
            t.id AS turno_id,
            t.fecha_hora,
            t.estado,
            t.motivo,
            CONCAT(p.nombre, ' ', p.apellido) AS paciente,
            p.dni AS paciente_dni,
            CONCAT(m.nombre, ' ', m.apellido) AS medico,
            m.matricula,
            e.nombre AS especialidad
        FROM turnos t
        INNER JOIN pacientes p ON t.paciente_id = p.id
        INNER JOIN medicos m ON t.medico_id = m.id
        INNER JOIN especialidades e ON m.especialidad_id = e.id
        ORDER BY t.fecha_hora ASC
    """)
    return db.execute(sql).mappings().all()


# =========================================================================
# CONSULTA 2: GROUP BY + INNER JOIN
# Cantidad de turnos agrupados por Especialidad y Estado
# =========================================================================
@router.get("/estadisticas-por-especialidad", summary="2. Consulta con GROUP BY + INNER JOIN")
def estadisticas_por_especialidad(db: Session = Depends(get_db)):
    sql = text("""
        SELECT 
            e.id AS especialidad_id,
            e.nombre AS especialidad,
            COUNT(t.id) AS total_turnos,
            SUM(CASE WHEN t.estado = 'pendiente' THEN 1 ELSE 0 END) AS pendientes,
            SUM(CASE WHEN t.estado = 'confirmado' THEN 1 ELSE 0 END) AS confirmados,
            SUM(CASE WHEN t.estado = 'atendido' THEN 1 ELSE 0 END) AS atendidos,
            SUM(CASE WHEN t.estado = 'cancelado' THEN 1 ELSE 0 END) AS cancelados
        FROM especialidades e
        INNER JOIN medicos m ON e.id = m.especialidad_id
        INNER JOIN turnos t ON m.id = t.medico_id
        GROUP BY e.id, e.nombre
        ORDER BY total_turnos DESC
    """)
    return db.execute(sql).mappings().all()


# =========================================================================
# CONSULTA 3: SUBCONSULTA (Subquery) + GROUP BY + INNER JOIN
# Médicos cuya cantidad de turnos supera o iguala el promedio general
# =========================================================================
@router.get("/medicos-alta-demanda", summary="3. Consulta con SUBCONSULTA (Subquery)")
def obtener_medicos_alta_demanda(db: Session = Depends(get_db)):
    sql = text("""
        SELECT 
            m.id AS medico_id,
            CONCAT(m.nombre, ' ', m.apellido) AS medico,
            m.matricula,
            e.nombre AS especialidad,
            COUNT(t.id) AS total_turnos
        FROM medicos m
        INNER JOIN especialidades e ON m.especialidad_id = e.id
        INNER JOIN turnos t ON m.id = t.medico_id
        GROUP BY m.id, m.nombre, m.apellido, m.matricula, e.nombre
        HAVING COUNT(t.id) >= (
            SELECT AVG(conteo.cantidad)
            FROM (
                SELECT COUNT(id) AS cantidad
                FROM turnos
                GROUP BY medico_id
            ) AS conteo
        )
        ORDER BY total_turnos DESC
    """)
    return db.execute(sql).mappings().all()

-- ==========================================
-- PROYECTO: MEDI TURNOS
-- BASE DE DATOS: mediturnos
-- ==========================================

CREATE DATABASE IF NOT EXISTS mediturnos
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE mediturnos;


-- ==========================================
-- 1. TABLA USUARIOS
-- ==========================================

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    rol ENUM('administrador', 'recepcionista', 'medico', 'paciente')
        NOT NULL DEFAULT 'paciente',
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ==========================================
-- 2. TABLA PACIENTES
-- ==========================================

CREATE TABLE pacientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT UNIQUE,
    dni VARCHAR(15) NOT NULL UNIQUE,
    nombre VARCHAR(80) NOT NULL,
    apellido VARCHAR(80) NOT NULL,
    fecha_nacimiento DATE,
    telefono VARCHAR(25),
    email VARCHAR(100),
    direccion VARCHAR(150),

    CONSTRAINT fk_paciente_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES usuarios(id)
        ON DELETE SET NULL
);


-- ==========================================
-- 3. TABLA ESPECIALIDADES
-- ==========================================

CREATE TABLE especialidades (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion VARCHAR(255)
);


-- ==========================================
-- 4. TABLA MEDICOS
-- ==========================================

CREATE TABLE medicos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT UNIQUE,
    especialidad_id INT NOT NULL,
    matricula VARCHAR(30) NOT NULL UNIQUE,
    nombre VARCHAR(80) NOT NULL,
    apellido VARCHAR(80) NOT NULL,
    telefono VARCHAR(25),
    email VARCHAR(100),
    activo BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT fk_medico_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES usuarios(id)
        ON DELETE SET NULL,

    CONSTRAINT fk_medico_especialidad
        FOREIGN KEY (especialidad_id)
        REFERENCES especialidades(id)
        ON DELETE RESTRICT
);


-- ==========================================
-- 5. TABLA TURNOS
-- ==========================================

CREATE TABLE turnos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    paciente_id INT NOT NULL,
    medico_id INT NOT NULL,
    fecha_hora DATETIME NOT NULL,
    motivo VARCHAR(255),

    estado ENUM('pendiente', 'confirmado', 'cancelado', 'atendido')
        NOT NULL DEFAULT 'pendiente',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_turno_paciente
        FOREIGN KEY (paciente_id)
        REFERENCES pacientes(id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_turno_medico
        FOREIGN KEY (medico_id)
        REFERENCES medicos(id)
        ON DELETE RESTRICT,

    CONSTRAINT uq_medico_fecha
        UNIQUE (medico_id, fecha_hora),

    INDEX idx_turnos_paciente (paciente_id),
    INDEX idx_turnos_fecha (fecha_hora),
    INDEX idx_turnos_estado (estado)
);

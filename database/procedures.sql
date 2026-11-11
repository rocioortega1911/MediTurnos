
USE mediturnos;

DELIMITER //

CREATE PROCEDURE registrar_turno(
    IN p_paciente_id INT,
    IN p_medico_id INT,
    IN p_fecha_hora DATETIME,
    IN p_motivo VARCHAR(255)
)
BEGIN
    DECLARE v_paciente INT DEFAULT 0;
    DECLARE v_medico INT DEFAULT 0;

    -- Si ocurre un error, cancelar la transacción
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    -- Comprobar que exista el paciente
    SELECT COUNT(*) INTO v_paciente
    FROM pacientes
    WHERE id = p_paciente_id;

    IF v_paciente = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'El paciente no existe';
    END IF;

    -- Comprobar que exista el médico y esté activo
    SELECT COUNT(*) INTO v_medico
    FROM medicos
    WHERE id = p_medico_id
    AND activo = TRUE;

    IF v_medico = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'El médico no existe o está inactivo';
    END IF;

    -- Registrar el turno
    INSERT INTO turnos (
        paciente_id,
        medico_id,
        fecha_hora,
        motivo,
        estado
    )
    VALUES (
        p_paciente_id,
        p_medico_id,
        p_fecha_hora,
        p_motivo,
        'pendiente'
    );

    COMMIT;

END //

DELIMITER ;

-- Esquema para la Base de Datos de RENIEC (bd2_reniec)

-- Tabla de Personas
-- Almacena la información de los ciudadanos para validación de identidad.
CREATE TABLE Personas (
    dni VARCHAR(8) PRIMARY KEY,
    apellidos VARCHAR(255) NOT NULL,
    nombres VARCHAR(255) NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    sexo CHAR(1) NOT NULL, -- 'M' o 'F'
    direccion VARCHAR(255)
);

-- Poblar con algunos datos de ejemplo
INSERT INTO Personas (dni, apellidos, nombres, fecha_nacimiento, sexo, direccion)
VALUES
    ('12345678', 'QUISPE GONZALES', 'JUAN CARLOS', '1990-05-15', 'M', 'AV. SIEMPRE VIVA 123'),
    ('87654321', 'RAMIREZ FLORES', 'MARIA ELENA', '1985-10-20', 'F', 'CALLE LOS PINOS 456');

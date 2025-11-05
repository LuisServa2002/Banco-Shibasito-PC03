-- Esquema para la base de datos de RENIEC (BD2)

CREATE TABLE IF NOT EXISTS Personas (
    dni TEXT PRIMARY KEY,
    apellido_paterno TEXT NOT NULL,
    apellido_materno TEXT NOT NULL,
    nombres TEXT NOT NULL,
    fecha_nacimiento TEXT NOT NULL,
    sexo TEXT NOT NULL,
    direccion TEXT NOT NULL
);

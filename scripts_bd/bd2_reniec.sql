CREATE TABLE Personas (
    dni TEXT PRIMARY KEY,
    apellido_paterno TEXT NOT NULL,
    apellido_materno TEXT NOT NULL,
    nombres TEXT NOT NULL,
    fecha_nacimiento TEXT NOT NULL,
    sexo TEXT NOT NULL,
    direccion TEXT NOT NULL
);
PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE Personas (
    dni TEXT PRIMARY KEY,
    apellido_paterno TEXT NOT NULL,
    apellido_materno TEXT NOT NULL,
    nombres TEXT NOT NULL,
    fecha_nacimiento TEXT NOT NULL,
    sexo TEXT NOT NULL,
    direccion TEXT NOT NULL
);
INSERT INTO Personas VALUES('45678912','GARCÍA','FLORES','MARÍA ELENA','1990-07-15','F','Av. Universitaria 1234');
INSERT INTO Personas VALUES('78901234','RAMÍREZ','QUISPE','JUAN CARLOS','1985-03-22','M','Calle San Martín 456');
INSERT INTO Personas VALUES('12345678','TORRES','MENDOZA','LUIS ALBERTO','1992-11-05','M','Av. Sacsayhuamán 789');
INSERT INTO Personas VALUES('23456789','CHÁVEZ','ROJAS','ANA SOFÍA','1998-06-30','F','Jr. Huancayo 321');
INSERT INTO Personas VALUES('34567890','PÉREZ','VÁSQUEZ','CARLOS JUAN','1979-12-10','M','Av. Las Palmeras 101');
COMMIT;

-- Esquema para la Base de Datos del Banco (bd1_banco)

-- Tabla de Cuentas
-- Almacena la información de las cuentas de los clientes.
CREATE TABLE Cuentas (
    id_cuenta INT PRIMARY KEY,
    nombre_cliente VARCHAR(255) NOT NULL,
    saldo DECIMAL(10, 2) NOT NULL CHECK (saldo >= 0)
);

-- Tabla de Transacciones
-- Registra todas las transacciones realizadas.
CREATE TABLE Transacciones (
    id_transaccion SERIAL PRIMARY KEY,
    id_cuenta INT,
    tipo_transaccion VARCHAR(50) NOT NULL, -- 'DEPOSITO', 'RETIRO', 'TRANSFERENCIA'
    monto DECIMAL(10, 2) NOT NULL,
    fecha_transaccion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    cuenta_destino INT, -- Para transferencias
    FOREIGN KEY (id_cuenta) REFERENCES Cuentas(id_cuenta)
);

-- Tabla de Préstamos
-- Almacena información sobre los préstamos solicitados por los clientes.
CREATE TABLE Prestamos (
    id_prestamo SERIAL PRIMARY KEY,
    id_cliente INT NOT NULL, -- Se podría vincular a un DNI o a un id_cuenta
    monto DECIMAL(10, 2) NOT NULL,
    monto_pendiente DECIMAL(10, 2) NOT NULL,
    estado VARCHAR(50) NOT NULL, -- 'APROBADO', 'RECHAZADO', 'PAGADO'
    fecha_solicitud TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para mejorar el rendimiento de las búsquedas
CREATE INDEX idx_id_cuenta ON Transacciones(id_cuenta);
CREATE INDEX idx_id_cliente_prestamos ON Prestamos(id_cliente);

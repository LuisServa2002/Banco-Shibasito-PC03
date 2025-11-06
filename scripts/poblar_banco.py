#!/usr/bin/env python3
"""
Poblar BD1 (Banco) con datos de prueba
"""

import psycopg2

DB_CONFIG = {
    "dbname": "bd1_banco",
    "user": "postgres",
    "password": "mysecretpassword",
    "host": "localhost",
    "port": "5432",
}


def poblar_bd():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Crear tablas si no existen
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Cuentas (
        id_cuenta INTEGER PRIMARY KEY,
        dni TEXT NOT NULL,
        saldo NUMERIC(10,2) DEFAULT 0.0,
        fecha_apertura TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Transacciones (
        id_transaccion SERIAL PRIMARY KEY,
        id_cuenta INTEGER NOT NULL,
        tipo VARCHAR(50) NOT NULL,
        monto NUMERIC(10,2) NOT NULL,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_cuenta) REFERENCES Cuentas(id_cuenta)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Prestamos (
        id_prestamo SERIAL PRIMARY KEY,
        id_cuenta INTEGER NOT NULL,
        dni TEXT NOT NULL,
        monto NUMERIC(10,2) NOT NULL,
        monto_pendiente NUMERIC(10,2) NOT NULL,
        estado VARCHAR(20) DEFAULT 'activo',
        fecha_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        plazo_meses INTEGER,
        FOREIGN KEY (id_cuenta) REFERENCES Cuentas(id_cuenta)
    )
    """)

    # Insertar cuentas (coinciden con DNIs de RENIEC)
    cuentas = [
        (1001, "45678912", 2200.00),  # MARÍA ELENA
        (1002, "87654321", 1500.00),  # Usuario ficticio
        (8008, "23456789", 5300.00),  # ANA SOFÍA
        (8009, "12345678", 3400.00),  # LUIS ALBERTO
    ]

    cursor.executemany(
        "INSERT INTO Cuentas (id_cuenta, dni, saldo) VALUES (%s, %s, %s) ON CONFLICT (id_cuenta) DO UPDATE SET saldo = EXCLUDED.saldo",
        cuentas,
    )

    conn.commit()

    # Contar registros
    cursor.execute("SELECT COUNT(*) FROM Cuentas")
    count = cursor.fetchone()[0]

    print(f"✓ Banco poblado con {count} cuentas")
    print("\n📋 Credenciales de prueba:")
    print("  DNI: 45678912 | Cuenta: 1001 | Saldo: S/ 2,200.00")
    print("  DNI: 23456789 | Cuenta: 8008 | Saldo: S/ 5,300.00")
    print("  DNI: 12345678 | Cuenta: 8009 | Saldo: S/ 3,400.00")

    conn.close()


if __name__ == "__main__":
    try:
        poblar_bd()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Asegúrate de que PostgreSQL esté corriendo:")
        print("   docker start postgres-db")

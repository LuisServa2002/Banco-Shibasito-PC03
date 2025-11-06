import os
import sqlite3

DB_PATH = "db_reniec/reniec.db"
os.makedirs("db_reniec", exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Crear tabla
cursor.execute("""
CREATE TABLE IF NOT EXISTS Personas (
    dni TEXT PRIMARY KEY,
    apellido_paterno TEXT,
    apellido_materno TEXT,
    nombres TEXT,
    fecha_nacimiento TEXT,
    sexo TEXT,
    direccion TEXT
)
""")

# Insertar DNIs que coinciden con PostgreSQL
personas = [
    (
        "45678912",
        "GARCÍA",
        "FLORES",
        "MARÍA ELENA",
        "1990-07-15",
        "F",
        "Universitaria 1234",
    ),
    (
        "78901234",
        "RAMÍREZ",
        "QUISPE",
        "JUAN CARLOS",
        "1985-03-22",
        "M",
        "San Martín 456",
    ),
    (
        "12345678",
        "TORRES",
        "MENDOZA",
        "LUIS ALBERTO",
        "1992-11-05",
        "M",
        "Sacsayhuamán 789",
    ),
    ("23456789", "CHÁVEZ", "ROJAS", "ANA SOFÍA", "1998-06-30", "F", "Huancayo 321"),
    (
        "34567890",
        "PÉREZ",
        "VÁSQUEZ",
        "CARLOS JUAN",
        "1979-12-10",
        "M",
        "Las Palmeras 101",
    ),
]

cursor.executemany(
    "INSERT OR REPLACE INTO Personas VALUES (?, ?, ?, ?, ?, ?, ?)", personas
)
conn.commit()
conn.close()
print(f"✓ RENIEC poblado con {len(personas)} personas")
